
from django.urls import path
from .views import CustomSignupView, CustomLoginView
from django.contrib.auth.views import LogoutView

app_name = 'account'

urlpatterns = [
    path('signup/', CustomSignupView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page="account:login"), name='logout'),
]
