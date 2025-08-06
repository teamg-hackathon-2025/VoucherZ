from django.shortcuts import render, redirect
from django.views import View


class TopPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('coupon:coupon_list')
        return render(request, 'account/index.html')
