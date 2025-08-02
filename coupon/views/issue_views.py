from django.shortcuts import render
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse

from ..models import Coupon


# class CouponIssueView(LoginRequiredMixin, View):
class CouponIssueView(View):
    def get(self, request):
        return render(request, 'coupon/issue.html')

    # def post(request, *args, **kwargs):
        # 所有者チェック（クーポンが所属する店舗のユーザーとログインユーザーが一致するか）
