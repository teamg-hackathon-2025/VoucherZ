from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from ..forms import CouponForm
from ..models import Coupon
from account.models import Store

SESSION_KEY = "coupon_data"


class CouponCreateView(LoginRequiredMixin, FormView):
    form_class = CouponForm
    template_name = "coupon/create.html"

    def get_initial(self):
        """
        フォームの初期値を取得する。

        親クラスの初期値に加えて、セッションに保存されている
        クーポン情報（dict型）があればそれをマージして返す。

        Returns:
            dict: フォームの初期値。
        """
        initial = super().get_initial()
        session_data = self.request.session.get(SESSION_KEY)
        if session_data is not None and isinstance(session_data, dict):
            coupon = session_data.get("coupon")
            if isinstance(coupon, dict):
                initial.update(coupon)
        return initial

    def form_valid(self, form):
        """
        フォーム送信がバリデーションを通過した際の処理。

        Args:
            form (Form): バリデーションを通過したフォームインスタンス。

        Returns:
            作成確認画面にリダイレクトする
        """
        # ログインユーザーの店舗IDを取得。
        user_id = self.request.user.id
        store_id = Store.get_store_id_for_user(user_id)

        # 店舗IDが存在しない場合はクーポン一覧ページへリダイレクトする。
        if store_id is None:
            return redirect(reverse("coupon:coupon_list"))

        coupon_data = form.cleaned_data.copy()
        # expiration_date を文字列化して保存
        if coupon_data.get("expiration_date"):
            coupon_data["expiration_date"] = coupon_data["expiration_date"].strftime("%Y-%m-%d")

        # フォームの入力値（cleaned_data）と店舗IDをセッションに保存する。
        self.request.session[SESSION_KEY] = {
            "coupon": coupon_data,
            "store_id": store_id,
        }
        return redirect("coupon:coupon_create_confirm")


class CouponCreateConfirmView(LoginRequiredMixin, TemplateView):
    template_name = "coupon/create-confirm.html"
    session_key = SESSION_KEY

    def get(self, request, *args, **kwargs):
        """
        クーポン作成確認画面の表示処理。

        以下の条件に該当する場合は、クーポン一覧ページへリダイレクトする：
        - セッションにクーポン作成データが存在しない
        - 店舗IDが存在しない
        - 店舗名が取得できない
        - クーポンの有効期限が不正な形式、または本日より前である

        上記以外の場合は、セッションから取得したクーポン情報と店舗名を
        インスタンス変数に設定し、親クラスの get() を呼び出してページを表示する。

        Args:
            request (HttpRequest): GETリクエストオブジェクト。

        Returns:
            正常時は確認画面、条件不一致時は一覧画面へのリダイレクト。
        """
        session_data = request.session.get(self.session_key)
        if session_data is None:
            return redirect(reverse("coupon:coupon_list"))

        store_id = session_data.get("store_id")
        coupon_data = session_data.get("coupon")
        if store_id is None or not isinstance(coupon_data, dict):
            return redirect(reverse("coupon:coupon_list"))

        store_name = Store.get_store_name(store_id)
        if store_name is None:
            return redirect(reverse("coupon:coupon_list"))

        # 文字列→date に変換してから比較
        expiration_date_string = coupon_data.get("expiration_date")
        expiration_date_object = None
        if expiration_date_string:
            try:
                # 文字列 (YYYY-MM-DD) → date型 に変換
                expiration_date_object = datetime.strptime(
                    expiration_date_string, "%Y-%m-%d"
                ).date()
            except ValueError:
                return redirect(reverse("coupon:coupon_list"))
        # 有効期限切れの場合は一覧へリダイレクト
        today = timezone.localdate()
        if expiration_date_object is not None and expiration_date_object < today:
            return redirect(reverse("coupon:coupon_list"))

        self.coupon = coupon_data
        self.store_name = store_name
        # テンプレート表示用に「YYYY/MM/DD」形式の文字列を追加
        self.expiration_date_display = expiration_date_object
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        テンプレートに渡すコンテキストデータを作成する。

        Args:
            **kwargs: 親クラスに渡すコンテキスト引数。

        Returns:
            dict: テンプレートに渡すコンテキストデータ。
        """
        context = super().get_context_data(**kwargs)
        context["coupon"] = {
            **self.coupon,
            "expiration_date_display": self.expiration_date_display,
            "store": {"store_name": self.store_name},
        }
        return context

    def post(self, request, *args, **kwargs):
        """
        クーポン作成確認画面のPOST処理。

        セッションに保持されたクーポン作成データを検証し、
        問題がなければクーポンを新規作成する。
        データが不正または有効期限切れの場合は一覧画面へリダイレクトする。

        Returns:
            作成完了後、または条件不一致時の一覧画面へのリダイレクト。
        """
        # セッションから作成中データを取得し、存在・型を確認する
        session_data = request.session.get(self.session_key)
        if session_data is None:
            return redirect(reverse("coupon:coupon_list"))
        store_id = session_data.get("store_id")
        coupon_data = session_data.get("coupon")
        if store_id is None or not isinstance(coupon_data, dict):
            return redirect(reverse("coupon:coupon_list"))

        # 文字列→date に変換（保存用）
        expiration_date_string = coupon_data.get("expiration_date")
        expiration_date_object = None
        if expiration_date_string:
            try:
                # 文字列 (YYYY-MM-DD) を date 型に変換
                expiration_date_object = datetime.strptime(
                    expiration_date_string, "%Y-%m-%d"
                ).date()
            except ValueError:
                return redirect(reverse("coupon:coupon_list"))
        # 有効期限切れの場合は一覧へリダイレクト
        today = timezone.localdate()
        if expiration_date_object is not None and expiration_date_object < today:
            return redirect(reverse("coupon:coupon_list"))

        Coupon.create(
            store_id,
            coupon_data.get("title"),
            coupon_data.get("discount"),
            coupon_data.get("target_product"),
            coupon_data.get("message"),
            expiration_date_object,
            coupon_data.get("max_issuance"),
        )

        # セッション上の作成中データを削除する
        request.session.pop(self.session_key, None)

        return redirect(reverse("coupon:coupon_list"))
