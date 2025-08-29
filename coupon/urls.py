from django.urls import path
from .views import (
    CouponCodeCustomerView,
    CouponDeleteView,
    CouponCreateView,
    CouponCreateConfirmView,
    CouponDetailView,
    CouponIssueView,
    CouponCodeDetailView,
    CouponVerifyPageView,
    CouponManualVerifyView,
    CouponQrVerifyView,
    CouponListView
)
app_name = "coupon"

urlpatterns = [
    path('', CouponListView.as_view(), name='coupon_list'),
    path('delete/<int:coupon_id>/', CouponDeleteView.as_view(), name='coupon_delete'),
    path('view/<uuid:coupon_code_uuid>/', CouponCodeCustomerView.as_view(), name='coupon_customer_view'),
    path('create/', CouponCreateView.as_view(), name='coupon_create'),
    path('create/confirm/', CouponCreateConfirmView.as_view(), name='coupon_create_confirm'),
    path('<int:coupon_id>/', CouponDetailView.as_view(), name='coupon_detail'),
    path('<int:coupon_id>/issue/', CouponIssueView.as_view(), name='coupon_issue'),
    path('code/<int:coupon_code_id>/', CouponCodeDetailView.as_view(), name='coupon_code_detail'),
    path('verify/', CouponVerifyPageView.as_view(), name='coupon_verify'),
    path('api/verify/manual/<str:code>/', CouponManualVerifyView.as_view(), name='coupon_verify_manual'),
    path('api/verify/uuid/<uuid:coupon_uuid>/', CouponQrVerifyView.as_view(), name='coupon_verify_qr'),
]
