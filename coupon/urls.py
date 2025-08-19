from django.urls import path
from .views import (
    CouponCreateView,
    CouponCreateConfirmView,
    CouponDetailView,
    CouponIssueView,
    CouponCodeDetailView
)
app_name = "coupon"

urlpatterns = [
    path('create/', CouponCreateView.as_view(), name='coupon_create'),
    path('create/confirm/', CouponCreateConfirmView.as_view(), name='coupon_create_confirm'),
    path('<int:coupon_id>/', CouponDetailView.as_view(), name='coupon_detail'),
    path('<int:coupon_id>/issue/', CouponIssueView.as_view(), name='coupon_issue'),
    path('code/<int:coupon_code_id>/', CouponCodeDetailView.as_view(), name='coupon_code_detail'),
]
