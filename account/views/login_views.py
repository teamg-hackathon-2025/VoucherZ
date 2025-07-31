from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from account.forms.login_forms import LoginForm

User = get_user_model()

class LoginView(LoginView):
    template_name = 'account/login.html'
    form_class = LoginForm
    def get_success_url(self):
        return reverse_lazy('coupon:coupon_list')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('coupon:coupon_list')
        return super().dispatch(request, *args, **kwargs)
