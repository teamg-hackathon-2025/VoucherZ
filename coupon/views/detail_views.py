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
        Raises:
            Http404: 該当するクーポンが存在しない場合
        """
        coupon_id = self.kwargs.get("coupon_id")
        coupon = Coupon.get_coupon(coupon_id)
        if coupon is None:
            raise Http404()
        return coupon

    def get(self, request, *args, **kwargs):
        """
        クーポン詳細ページ。

        - coupon_idに紐づいているデータがない場合404に返す
        - 権限がない場合ホーム画面にリダイレクトする
        - 削除済みの場合ホーム画面にリダイレクトする
        - クーポンの有効期限が切れている場合（今日より前）ホーム画面にリダイレクトする
        - 発行数の上限に達した場合ホーム画面にリダイレクトする

        上記に該当しない場合は、ホーム画面にリダイレクトする
        """
        coupon_id = self.kwargs.get("coupon_id")
        try:
            # 権限チェック（店舗ユーザーとログインユーザーの一致を確認）
            store_user_id = Coupon.get_store_user_id(coupon_id)
            if store_user_id is None:
                raise Http404()
            if store_user_id != request.user.id:
                raise PermissionDenied()

            # 削除済みの場合はホーム画面へリダイレクト
            coupon_for_deleted_at = Coupon.get_for_delete_check(coupon_id)
            if coupon_for_deleted_at is None:
                raise Http404()

            deleted_at = coupon_for_deleted_at.deleted_at
            if deleted_at is not None:
                return redirect(reverse("coupon:coupon_list"))

            # 有効期限切れの場合はホーム画面へリダイレクト
            coupon_for_expiration_date = Coupon.get_for_expiration_check(coupon_id)
            if coupon_for_expiration_date is None:
                raise Http404()

            expiration_date = coupon_for_expiration_date.expiration_date
            today = timezone.localdate()
            if expiration_date is not None and expiration_date < today:
                return redirect(reverse("coupon:coupon_list"))

            # 発行数上限に達している場合はホーム画面へリダイレクト
            coupon_for_issuance_check = Coupon.get_for_issuance_check(coupon_id)
            if coupon_for_issuance_check is None:
                raise Http404()

            max_issuance = coupon_for_issuance_check.max_issuance
            issued_count = coupon_for_issuance_check.issued_count
            if max_issuance is not None and max_issuance <= issued_count:
                return redirect(reverse("coupon:coupon_list"))

            return super().get(request, *args, **kwargs)
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
