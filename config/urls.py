"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from account.views import TopPageView
import environ
from .views import health_check

env = environ.Env()

urlpatterns = [
    path('account/', include('account.urls', namespace='account')),
    path('coupon/', include('coupon.urls', namespace='coupon')),
    path('', TopPageView.as_view(), name='index'),
    path('health/', health_check, name='health_check'),
]

if settings.DEBUG and env("DJANGO_ENV") == "development":
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        path('admin/', admin.site.urls),
    ]
