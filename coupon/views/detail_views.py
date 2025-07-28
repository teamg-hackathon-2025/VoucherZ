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
        coupon_id = self.kwargs.get("coupon_id")
        # coupon_idからcouponデータ取得
        coupon = Coupon.get_coupon(coupon_id)
        return coupon

    def get(self, request, *args, **kwargs):
        """
        GETリクエストができなかった場合、リダイレクト
        """
        self.object = self.get_object()
        if self.object is None:
            messages.warning(
                request,
                f"指定されたクーポンが存在しないか、既に削除されています。"
            )
            return redirect(reverse("coupon:coupon_list"))
        return super().get(request, *args, **kwargs)
