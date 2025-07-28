from django.shortcuts import render
from django.contrib import messages
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse

from ..models import Coupon


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
        """
        coupon_id = self.kwargs.get("coupon_id")
        # coupon_idからcouponデータ取得
        coupon = Coupon.get_coupon(coupon_id)
        return coupon

    def get(self, request, *args, **kwargs):
        """
        クーポン詳細ページ。
        存在しない、または利用できないクーポンIDが指定された場合は一覧ページへリダイレクトする。
        """
        self.object = self.get_object()
        if self.object is None:
            return redirect(reverse("coupon:coupon_list"))
        return super().get(request, *args, **kwargs)
