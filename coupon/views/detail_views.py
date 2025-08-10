from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.http import Http404
from django.utils import timezone
import logging

from ..models import Coupon
logger = logging.getLogger(__name__)


class CouponDetailView(LoginRequiredMixin, DetailView):
    template_name = "coupon/detail.html"
    context_object_name = "coupon"

    def get_object(self):
        """
        URLパスからクーポンIDを取得し、対応するクーポン情報を返す
        Returns:
            coupon: 指定されたクーポンIDが存在すれば coupon インスタンス
            None: レコード未存在、整合性エラー、DBエラー、その他予期せぬエラーが発生した場合
        """
        coupon_id = self.kwargs.get("coupon_id")
        coupon = Coupon.get_coupon(coupon_id)
        return coupon

    def get(self, request, *args, **kwargs):
        """
        クーポン詳細ページ。

        以下の条件に該当する場合はクーポン一覧ページにリダイレクトする：
        - coupon_idに紐づいているデータがない場合
        - 権限がない場合（クーポンの店舗ユーザー ≠ ログインユーザー）
        - クーポンの有効期限が切れている場合（今日より前）
        - 発行数の上限に達した場合
        - クーポンの取得結果が None の場合

        上記に該当しない場合は、クーポン詳細ページを表示する。
        """
        coupon_id = self.kwargs.get("coupon_id")
        try:
            # 権限チェック（店舗ユーザーとログインユーザーの一致を確認）
            store_user_id = Coupon.get_store_user_id(coupon_id)
            if store_user_id is None:
                raise Http404()
            if store_user_id != request.user.id:
                raise PermissionDenied()
            # 有効期限切れまたは発行数上限に達している場合は一覧へリダイレクト
            coupon_for_check = Coupon.get_for_status_check(coupon_id)
            if coupon_for_check is None:
                return redirect(reverse("coupon:coupon_list"))
            expiration_date = coupon_for_check.expiration_date
            today = timezone.now().date()
            max_issuance = coupon_for_check.max_issuance
            issued_count = coupon_for_check.issued_count
            if (
                (expiration_date is not None and expiration_date < today) or
                (max_issuance is not None and max_issuance <= issued_count)
            ):
                return redirect(reverse("coupon:coupon_list"))
            self.object = self.get_object()
            if self.object is None:
                return redirect(reverse("coupon:coupon_list"))
        except Http404:
            logger.info(
                "Coupon not found",
                extra={
                    "user_id": request.user.id,
                    "coupon_id": coupon_id,
                    "ip": request.META.get("REMOTE_ADDR"),
                },
            )
            return redirect(reverse("coupon:coupon_list"))
        except PermissionDenied:
            logger.warning(
                "Unauthorized access attempt",
                extra={
                    "user_id": request.user.id,
                    "coupon_id": coupon_id,
                    "ip": request.META.get("REMOTE_ADDR"),
                },
            )
            return redirect(reverse("coupon:coupon_list"))
        return super().get(request, *args, **kwargs)
