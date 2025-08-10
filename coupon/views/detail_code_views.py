from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.http import Http404
from django.utils import timezone
import logging

from ..models import Coupon, CouponCode
logger = logging.getLogger(__name__)


class CouponCodeDetailView(LoginRequiredMixin, DetailView):
    template_name = "coupon/detail-code.html"

    def get_object(self):
        """
        URLパスからクーポンコードIDを取得し、対応するクーポン情報を返す
        Returns:
            coupon, code: 指定されたクーポンコードID、クーポンIDが存在した場合
            None: レコード未存在、整合性エラー、DBエラー、その他予期せぬエラーが発生した場合
        """
        coupon_code_id = self.kwargs.get("coupon_code_id")
        coupon_id = self.coupon_id
        if coupon_id is None:
            coupon_id = CouponCode.get_coupon_id(coupon_code_id)
        coupon_code = CouponCode.get_coupon_code(coupon_code_id)
        coupon = Coupon.get_coupon(coupon_id)
        return {"coupon_code": coupon_code, "coupon": coupon}

    def get(self, request, *args, **kwargs):
        """
        クーポン発行後の詳細ページ。

        以下の条件に該当する場合はクーポン一覧ページにリダイレクトする：
        - coupon_code_id に紐づく coupon_id が取得できない場合
        - 権限がない場合（クーポンの店舗ユーザー ≠ ログインユーザー）
        - クーポンの有効期限が切れている場合（今日より前）
        - クーポンコードまたはクーポンの取得に失敗した場合（None）

        上記に該当しない場合は、クーポンコード詳細ページを表示する。
        """
        coupon_code_id = self.kwargs.get("coupon_code_id")
        coupon_id = CouponCode.get_coupon_id(coupon_code_id)
        try:
            # 権限チェック（店舗ユーザーとログインユーザーの一致を確認）
            store_user_id = Coupon.get_store_user_id(coupon_id)
            if store_user_id is None:
                raise Http404()
            if store_user_id != request.user.id:
                raise PermissionDenied()
            # 有効期限切れの場合は一覧へリダイレクト
            coupon_for_check = Coupon.get_for_status_check(coupon_id)
            if coupon_for_check is None:
                return redirect(reverse("coupon:coupon_list"))
            expiration_date = coupon_for_check.expiration_date
            today = timezone.now().date()
            if expiration_date is not None and expiration_date < today:
                return redirect(reverse("coupon:coupon_list"))
            self.coupon_id = coupon_id
            self.object = self.get_object()
            coupon_code = self.object.get("coupon_code")
            coupon = self.object.get("coupon")
            if coupon_code is None or coupon is None:
                return redirect(reverse("coupon:coupon_list"))
        except Http404:
            logger.info(
                "Coupon not found",
                extra={
                    "user_id": request.user.id,
                    "coupon_code_id": coupon_code_id,
                    "ip": request.META.get("REMOTE_ADDR"),
                },
            )
            return redirect(reverse("coupon:coupon_list"))
        except PermissionDenied:
            logger.warning(
                "Unauthorized access attempt",
                extra={
                    "user_id": request.user.id,
                    "coupon_code_id": coupon_code_id,
                    "ip": request.META.get("REMOTE_ADDR"),
                },
            )
            return redirect(reverse("coupon:coupon_list"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        テンプレートに渡すコンテキスト変数を設定する。
        self.object が dict（coupon, coupon_code を含む）の場合、
        その中身を context に展開してテンプレートで直接使えるようにする。
        Returns:
            dict: テンプレートに渡すコンテキスト（coupon, coupon_code などを含む）
        """
        context = super().get_context_data(**kwargs)
        if isinstance(self.object, dict):
            context.update(self.object)
        return context
