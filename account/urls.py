
from django.urls import path
from .views import SignUpView, LoginView
from django.contrib.auth.views import LogoutView

app_name = 'account'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page="account:login"), name='logout'),
]
