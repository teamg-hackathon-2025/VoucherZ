from django.urls import path
from .views import (
    CouponDetailView,
    CouponIssueView
)
app_name = "coupon"

urlpatterns = [
    path('<int:coupon_id>/', CouponDetailView.as_view(), name='coupon_detail'),
    # path('<int:coupon_id>/issue/', CouponIssueView.as_view(), name='coupon_issue'),
    path('issue/', CouponIssueView.as_view(), name='coupon_issue'),
]
