from django.shortcuts import render
from django.views import View

app_name = "account"

class TopPageView(View):
    def get(self, request):
        return render(request, 'account/index.html')

