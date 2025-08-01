from django.urls import path
from .views import (
    CouponListView,
    CouponManualVerifyView,
)

app_name = "coupon"

urlpatterns = [
    path('', CouponListView.as_view(), name='coupon_list'),
    path('verify/manual/', CouponManualVerifyView.as_view(), name='coupon_verify_manual'),
]
