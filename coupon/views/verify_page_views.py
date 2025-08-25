from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class CouponVerifyPageView(LoginRequiredMixin, TemplateView):
    template_name = "coupon/verify.html"

