from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import get_user_model
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import Store

app_name = "account"

User = get_user_model()


class TopPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('coupon:coupon_list')
        return render(request, 'account/index.html')

class CustomSignupView(CreateView):
    template_name = 'account/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('coupon:coupon_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        store_name = form.cleaned_data.get('store_name')
        Store.objects.create(store_name=store_name, user=self.object)
        login(self.request, self.object)
        return response

class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    authentication_form = CustomAuthenticationForm
    def get_success_url(self):
        return reverse_lazy('coupon:coupon_list')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('coupon:coupon_list')
        return super().dispatch(request, *args, **kwargs)
