from django.views.generic import TemplateView

from ..models import Coupon, CouponCode


class CouponManualVerifyView(TemplateView):
    template_name = "coupon/manual_verify.html"
