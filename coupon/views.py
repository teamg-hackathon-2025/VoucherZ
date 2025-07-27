from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class CouponListView(TemplateView):
    template_name = 'coupon/list.html'
