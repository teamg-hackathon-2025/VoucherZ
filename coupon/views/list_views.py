from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils import timezone

import logging
now = timezone.localdate()

from ..models import Coupon
from account.models import Store
logger = logging.getLogger(__name__)


class CouponListView(LoginRequiredMixin, ListView):
    template_name = "coupon/list.html"

    def setup(self, request, *args, **kwargs):
        """
        View インスタンスの初期化処理。

        ログインユーザーに紐づく store_id を取得し、インスタンス変数に保持する。
        """
        super().setup(request, *args, **kwargs)
        user_id = self.request.user.id
        self.store_id = Store.get_store_id_for_user(user_id)

    def get_queryset(self):
        queryset = Coupon.get_coupon_list(self.store_id)

        # 計算処理: 利用率（%）
        for coupon in queryset:
            if coupon.redeemed_count > 0:
                coupon.usage_rate = round((coupon.redeemed_count / coupon.issued_count) * 100)
            else:
                coupon.usage_rate = None  # max_issuanceがない場合は利用率なし

        return queryset

    def get_context_data(self, **kwargs):
        store_name = Store.get_store_name(self.store_id)
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.localdate()
        return context
