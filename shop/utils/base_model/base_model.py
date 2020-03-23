# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/22 15:16
@Author  : 半纸梁
@File    : base_model.py
"""
from django.db import models


class BaseModel(models.Model):
    """
    base model,public field
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_delete = models.BooleanField(default=False, verbose_name="逻辑删除")

    class Meta:
        abstract = True   # 用于其他模型继承，在数据迁移时不会创建表格
