from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.http import Http404
from django.utils import timezone
import logging

from ..models import Coupon, CouponCode
logger = logging.getLogger(__name__)


class CouponIssueView(LoginRequiredMixin, View):
    def post(self, request, **kwargs):
        """
        クーポン発行処理。
        - coupon_idに紐づくクーポンが存在しない場合は404に返す
        - 権限がない場合はホーム画面にリダイレクトする
        - 有効期限切れまたは発行数上限に達している場合はホーム画面にリダイレクトする
        - 正常な場合はクーポンコードを発行し、発行後の処理を実行する
        Returns:
            HttpResponse:
            - 成功時: 発行したクーポン内容を表示するレスポンス
            - 失敗時: ホーム画面へのリダイレクトレスポンス
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
            today = timezone.localdate()
            if expiration_date is not None and expiration_date < today:
                return redirect(reverse("coupon:coupon_list"))

            max_issuance = coupon_for_check.max_issuance
            issued_count = coupon_for_check.issued_count
            if max_issuance is not None and max_issuance <= issued_count:
                return redirect(reverse("coupon:coupon_list"))

            coupon_code = CouponCode.issue(coupon_id)
            if coupon_code is None:
                return redirect(reverse("coupon:coupon_list"))
            return redirect(
                reverse("coupon:coupon_code_detail", kwargs={"coupon_code_id": coupon_code.id})
            )
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
