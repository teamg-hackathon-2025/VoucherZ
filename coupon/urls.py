from django.urls import path
from .views import (
    CouponDetailView
)
app_name = "coupon"

urlpatterns = [
    path('<int:coupon_id>/', CouponDetailView.as_view(), name='coupon_detail'),
]
