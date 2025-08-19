from django.urls import path
from .views import (
    CouponDetailView,
    CouponIssueView,
    CouponListView,
    CouponCodeDetailView
)

app_name = "coupon"

urlpatterns = [
    path('', CouponListView.as_view(), name='coupon_list'),
    path('<int:coupon_id>/', CouponDetailView.as_view(), name='coupon_detail'),
    path('<int:coupon_id>/issue/', CouponIssueView.as_view(), name='coupon_issue'),
    path('code/<int:coupon_code_id>/', CouponCodeDetailView.as_view(), name='coupon_code_detail'),
]
