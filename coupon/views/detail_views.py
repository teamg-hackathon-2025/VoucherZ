from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
import logging

from ..models import Coupon
logger = logging.getLogger(__name__)


class CouponDetailView(LoginRequiredMixin, DetailView):
    template_name = "coupon/detail.html"
    model = Coupon
    context_object_name = "coupon"

    def get_object(self):
        """
        URLパスからクーポンIDを取得し、対応するクーポン情報を返す
        Returns:
            coupon: 指定されたクーポンIDが存在すれば coupon インスタンス。
            None: 存在しない場合。
        Raises:
            PermissionDenied: アクセス権がない場合
        """
        coupon_id = self.kwargs.get("coupon_id")
        # 権限チェック（店舗ユーザーとログインユーザーの一致を確認）
        store_user_id = Coupon.get_store_user_id(coupon_id)
        if store_user_id != self.request.user.id:
            logger.warning(
                "Unauthorized access attempt",
                extra={
                    "user_id": self.request.user.id,
                    "coupon_id": coupon_id,
                    "ip": self.request.META.get("REMOTE_ADDR"),
                },
            )
            raise PermissionDenied("リソースにアクセスできません。")
        # coupon_idからcouponデータ取得
        coupon = Coupon.get_coupon(coupon_id)
        return coupon

    def get(self, request, *args, **kwargs):
        """
        クーポン詳細ページ。
        - 権限がない場合は一覧ページにリダイレクトする。
        - 取得結果が None の場合も一覧ページにリダイレクトする。
        - 今日より有効期限が前の場合も一覧ページにリダイレクトする
        - 発行数の上限に達した場合も一覧ページにリダイレクトする
        - 正常取得できた場合は詳細ページを表示する。
        """
        try:
            self.object = self.get_object()
        except PermissionDenied:
            return redirect(reverse("coupon:coupon_list"))
        if self.object is None:
            return redirect(reverse("coupon:coupon_list"))
        expiration_date = self.object.expiration_date
        today = timezone.now().date()
        max_issuance = self.object.max_issuance
        issued_count = self.object.issued_count
        if (
            (expiration_date is not None and expiration_date < today) or
            (max_issuance is not None and max_issuance <= issued_count)
        ):
            return redirect(reverse("coupon:coupon_list"))
        return super().get(request, *args, **kwargs)
