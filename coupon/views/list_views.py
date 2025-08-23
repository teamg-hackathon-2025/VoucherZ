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
    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        store_id = Store.get_store_id_for_user(user_id)
        coupon_list = Coupon.get_coupon_list(store_id)
        store_name = Store.get_store_name(store_id)

        # 計算処理: 利用率（%）
        for coupon in coupon_list:
            if coupon.max_issuance and coupon.max_issuance > 0:
                coupon.usage_rate = round((coupon.issued_count / coupon.max_issuance) * 100)
            else:
                coupon.usage_rate = None  # max_issuanceがない場合は利用率なし

        return render(
            request,
            'coupon/list.html',
            {
                'coupon_list': coupon_list,
                'store_name': store_name,
            }
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.localdate()
        return context
