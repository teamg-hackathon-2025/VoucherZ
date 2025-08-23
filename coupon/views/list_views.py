from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.db.models import Q, F, Case, When, Value, IntegerField
from django.utils import timezone
import logging

from account.models import Store
from ..models import Coupon
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
        """
        クーポン一覧を取得し、並び順と利用率を付与する。

        並び順の優先度:
            0 = 有効期限内かつ上限未達
            1 = 無期限
            2 = 有効期限内だが上限到達
            3 = 有効期限切れ
            9 = その他

        - sort_priority を annotate して order_by で並び替えを行う。
        - 各クーポンに usage_rate（利用率%）を計算して付与する。

        Returns:
            QuerySet: 注釈と利用率が付与されたクーポン一覧
        """
        today = timezone.localdate()
        queryset = Coupon.get_coupon_list(self.store_id)
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
                coupon.usage_rate = 0

        return queryset

    def get_context_data(self, **kwargs):
        """
        テンプレートに渡すコンテキストを設定する。

        - 今日の日付を "today" として追加する。
        - ログインユーザーに紐づく店舗名を "store_name" として追加する。

        Args:
            **kwargs: 親クラスから受け取るコンテキストの追加引数

        Returns:
            dict: テンプレートに渡すコンテキスト
        """
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.localdate()
        context["store_name"] = Store.get_store_name(self.store_id)
        return context
