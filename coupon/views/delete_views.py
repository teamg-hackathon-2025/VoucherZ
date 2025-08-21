from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.http import Http404
from django.utils import timezone
import logging

from ..models import Coupon, CouponCode
logger = logging.getLogger(__name__)


class CouponDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "coupon/list.html"