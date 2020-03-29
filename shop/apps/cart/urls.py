# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/22 15:59
@Author  : 半纸梁
@File    : urls.py
"""
from django.urls import path
from cart import  views

app_name = 'cart'

urlpatterns = [
    path('',views.CartIndexView.as_view(), name="index"),
    path('add/',views.AddCartView.as_view(), name="add")

]
