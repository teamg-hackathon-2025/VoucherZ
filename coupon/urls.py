from django.urls import path
from .views import (
    CouponDetailView,
    CouponIssueView,
    CouponCodeDetailView,
    CouponManualVerifyView,
    CouponListView,
)
app_name = "coupon"

urlpatterns = [
    path('<int:coupon_id>/', CouponDetailView.as_view(), name='coupon_detail'),
    path('<int:coupon_id>/issue/', CouponIssueView.as_view(), name='coupon_issue'),
    path('code/<int:coupon_code_id>/', CouponCodeDetailView.as_view(), name='coupon_code_detail'),
    path('verify/manual/', CouponManualVerifyView.as_view(), name='coupon_verify_manual'),
    path('', CouponListView.as_view(), name='coupon_list'),
    
]
