from django.views.generic import TemplateView

from ..models import Coupon, CouponCode


class CouponListView(TemplateView):
    template_name = "coupon/list.html"
