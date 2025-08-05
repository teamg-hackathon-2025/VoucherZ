from django.shortcuts import render
from django.views import View

app_name = "coupon"

class CouponListView(View):
    template_name = "coupon/list.html"