# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/22 15:59
@Author  : 半纸梁
@File    : urls.py
"""

from django.urls import path, re_path
from user import views

app_name = "user"
urlpatterns = [
    re_path("username/(?P<username>\w{5,20})/", views.CheckUsernameView.as_view(), name="username"),
    re_path("mobile/(?P<mobile>1[3-9]\d{9})/", views.CheckMobileView.as_view(), name="mobile"),
    path("sms_code/", views.SmsCodeView.as_view(), name="sms_code"),

    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),

    path('user_center/', views.UserCenterView.as_view(),name="user_center"),
    path('cart/', views.UserShoppingCartView.as_view(),name="cart"),
    path('address/', views.ShippingAddressView.as_view(),name="address"),
]
