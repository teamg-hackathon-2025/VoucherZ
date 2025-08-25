from django.db.models import Q, F, Case, When, Value, IntegerField
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

        today = timezone.localdate()
        # 期限内
        not_expired = Q(expiration_date__gte=today)
        # 無期限
        no_expiration_limit = Q(expiration_date__isnull=True)
        # 発行上限が設定されていない
        no_issue_limit = Q(max_issuance__isnull=True)
        # 発行上限にまだ達していない（上限未達 or 上限なし）
        issue_limit_not_reached = Q(issued_count__lt=F("max_issuance")) | no_issue_limit
        # 発行上限に達している
        issue_limit_reached = Q(max_issuance__lte=F("issued_count"))
        # すでに有効期限が切れている
        already_expired = Q(expiration_date__lt=today)
        queryset = queryset.annotate(
            sort_priority=Case(
                # 1) 期限内 & 上限未達
                When(not_expired & issue_limit_not_reached, then=Value(0)),
                # 2) 無期限
                When(no_expiration_limit, then=Value(1)),
                # 3) 期限内だが上限到達
                When(not_expired & issue_limit_reached, then=Value(2)),
                # 4) 期限切れ
                When(already_expired, then=Value(3)),
                default=Value(9),
                output_field=IntegerField(),
            )
        ).order_by("sort_priority", "-expiration_date")

        # 計算処理: 利用率（%）
        for coupon in queryset:
            if coupon.issued_count > 0:
                coupon.usage_rate = round((coupon.redeemed_count / coupon.issued_count) * 100)
            else:
                coupon.usage_rate = 0  # max_issuanceがない場合は利用率なし

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["store_name"] = Store.get_store_name(self.store_id)
        context["today"] = timezone.localdate()
        return context
    
    
