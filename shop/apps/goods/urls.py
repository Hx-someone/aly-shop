# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/22 15:59
@Author  : 半纸梁
@File    : urls.py
"""
from django.urls import path
from goods import views

app_name = "goods"
urlpatterns = [
    path('index/', views.GoodsIndexView.as_view(), name="index"),
    path('detail/<int:goods_id>', views.GoodsDetailView.as_view(), name="detail"),
    path('list/<int:type_id>/<int:page>/', views.GoodsTypeListView.as_view(), name="list"),
]
