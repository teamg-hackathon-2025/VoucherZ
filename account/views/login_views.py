from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from account.forms.login_forms import LoginForm
from django.db import DatabaseError
from django.contrib import messages
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class LoginView(LoginView):
    template_name = 'account/login.html'
    form_class = LoginForm
    def get_success_url(self):
        return reverse_lazy('coupon:coupon_list')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('coupon:coupon_list')
        
        try:
            return super().dispatch(request, *args, **kwargs)
        except DatabaseError as e:
            logger.exception("Database error occurred during login process.")
            messages.error(request, 'データベースエラーが発生しました。もう一度お試しください。')
            return redirect(reverse_lazy('account:login'))
        except Exception as e:
            # その他の予期せぬエラー
            logger.exception("Unexpected error occurred during login process.")
            messages.error(request, '不明なエラーが発生しました。時間をおいてから再度お試しください。')
            return redirect(reverse_lazy('account:login'))
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        if hasattr(user, 'store'):
            self.request.session['store_id'] = user.store.id
        return response
