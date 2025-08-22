from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
import logging

from ..models import Coupon
logger = logging.getLogger(__name__)


class CouponDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "coupon/list.html"
    success_url = reverse_lazy("coupon:coupon_list")

    def post(self, request, *args, **kwargs):
        """
        クーポン削除処理。

        - 既に削除済みの場合は一覧へリダイレクト。
        - 有効期限内または無期限で、かつ発行済みがある場合は削除不可とし一覧へリダイレクト。
        - 上記以外の場合は削除処理を実行。
        """
        coupon_id = self.kwargs.get("coupon_id")

        # 削除済みの場合ホーム画面にリダイレクト
        coupon_for_deleted_at = Coupon.get_for_delete_check(coupon_id)
        if coupon_for_deleted_at is None:
            return redirect(reverse("coupon:coupon_list"))

        deleted_at = coupon_for_deleted_at.deleted_at
        if deleted_at is not None:
            return redirect(reverse("coupon:coupon_list"))

        # 有効期限内や無期限かつ1件以上発行数が存在する場合ホーム画面にリダイレクト
        coupon_for_expiration_date = Coupon.get_for_expiration_check(coupon_id)
        if coupon_for_expiration_date is None:
            return redirect(reverse("coupon:coupon_list"))

        coupon_for_issuance_check = Coupon.get_for_issuance_check(coupon_id)
        if coupon_for_issuance_check is None:
            return redirect(reverse("coupon:coupon_list"))

        expiration_date = coupon_for_expiration_date.expiration_date
        today = timezone.localdate()
        issued_count = coupon_for_issuance_check.issued_count
        if (
            (
                (expiration_date is not None and today <= expiration_date) or
                (expiration_date is None)
            ) and
            (issued_count > 0)
        ):
            return redirect(reverse("coupon:coupon_list"))

        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        論理削除処理を実行する

        Returns:
            削除後にホーム画面にリダイレクト
        """
        coupon_id = self.kwargs.get("coupon_id")
        Coupon.logical_delete(coupon_id)
        return redirect(self.success_url)
