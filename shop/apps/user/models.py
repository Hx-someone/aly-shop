# -*-coding:utf-8-*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.base_model.base_model import BaseModel
from django.contrib.auth.models import AbstractUser, UserManager as _UserManager


class UserManager(_UserManager):
    """
     重写创建超级用户时需要输入email字段
    """
    def create_superuser(self, username, password, email=None, **extra_fields):
        return super().create_superuser(username=username, password=password, email=email, **extra_fields)


class User(AbstractUser,BaseModel):
    """
    重写users模型
    """
    objects = UserManager()
    mobile = models.CharField(
        max_length=11,
        unique=True,
        help_text="手机号",
        verbose_name="手机号",
        error_messages={
            "unique": "手机号已被注册"
        })
    email_active = models.BooleanField(default=False, help_text="邮箱状态")


class AddressManager(models.Manager):
    """地址模型管理器类"""
    # 1. 改变原有查询的结果集:all()
    # 2. 封装方法:用户操作模型类对应的数据表(增删查改)

    def get_default_address(self, user):
        # 获取用户的默认收货地址
        try:
            address = self.get(user=user, is_default=True)
        except self.model.DoesNotExist:
            address = None  # 不存在默认地址

        return address


class Address(BaseModel):
    """地址模型类"""
    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='所属用户')
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    # 自定义一个模型管理器类
    objects = AddressManager()

    class Meta:
        db_table = 'tb_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username
