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
            dict: {"coupon_code": CouponCode, "coupon": Coupon}
        Raises:
            Http404: 対応するクーポンコードまたはクーポンが存在しない場合
        """
        coupon_code_id = self.kwargs.get("coupon_code_id")
        coupon_id = self.coupon_id
        if coupon_id is None:
            coupon_id = CouponCode.get_coupon_id(coupon_code_id)

        coupon_code = CouponCode.get_coupon_code(coupon_code_id)
        if coupon_code is None:
            raise Http404()

        coupon = Coupon.get_coupon(coupon_id)
        if coupon is None:
            raise Http404()

        return {"coupon_code": coupon_code, "coupon": coupon}

    def get(self, request, *args, **kwargs):
        """
        クーポン発行後の詳細ページ。

        Returns:
            HttpResponse: 404/ホーム画面にリダイレクト/詳細ページのいずれか。
        """
        coupon_code_id = self.kwargs.get("coupon_code_id")
        coupon_id = CouponCode.get_coupon_id(coupon_code_id)
        if coupon_id is None:
            raise Http404()

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
                raise Http404()

            expiration_date = coupon_for_check.expiration_date
            today = timezone.localdate()
            if expiration_date is not None and expiration_date < today:
                return redirect(reverse("coupon:coupon_list"))

            self.coupon_id = coupon_id
            return super().get(request, *args, **kwargs)
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
