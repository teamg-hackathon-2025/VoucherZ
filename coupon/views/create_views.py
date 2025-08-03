from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.generic import FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse

from ..models import Coupon


# class CouponCreateView(LoginRequiredMixin, FormView):
class CouponCreateView(View):
    def get(self, request):
        return render(request, 'coupon/create.html')


class CouponCreateConfirmView(View):
    def get(self, request):
        return render(request, 'coupon/create-confirm.html')
