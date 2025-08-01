from django.shortcuts import render
from django.views import View

app_name = "coupon"

class CouponListView(View):
    def get(self, request):
        return render(request, 'coupon/list.html')
    
class CouponManualVerifyView(View):
    def get(self, request):
        return render(request, 'coupon/manual_verify.html')
