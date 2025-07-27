from django.urls import path
from .views import CouponListView

app_name = "coupon"

urlpatterns = [
    path('', CouponListView.as_view(), name='coupon_list')
]
