from django.urls import path
from .views import (
    CouponListView,
    CouponDetailView,
)

app_name = "coupon"

urlpatterns = [
    path('', CouponListView.as_view(), name='coupon_list'),
    path('<int:coupon_id>/', CouponDetailView.as_view(), name='coupon_detail'),
]
