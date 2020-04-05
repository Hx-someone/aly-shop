# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/22 21:57
@Author  : 半纸梁
@File    : forms.py
"""
import re
from django import forms
from django.core.validators import RegexValidator

from user import models
from django.db.models import Q
from user import contains
from django_redis import get_redis_connection
from django.contrib.auth import login


class RegisterForm(forms.Form):
    """
    register field verify
    """
    # 1. 单字段验证
    username = forms.CharField(
        max_length=20,
        min_length=5,
        error_messages={
            "max_length": "用户名格式不正确",
            "min_length": "用户名格式不正确",
            "required": "用户名不能为空"
        }
    )
    password = forms.CharField(
        max_length=18,
        min_length=5,
        error_messages={
            "max_length": "密码格式不正确",
            "min_length": "密码格式不正确",
            "required": "密码不能为空"
        }
    )

    mobile = forms.CharField(
        max_length=11,
        min_length=11,
        error_messages={
            "max_length": "手机号格式不正确",
            "min_length": "手机号格式不正确",
            "required": "手机号不能为空"
        }
    )
    sms_text = forms.CharField(
        max_length=6,
        min_length=6,
        error_messages={
            "max_length": "短信验证码格式不正确",
            "min_length": "短信验证码格式不正确",
            "required": "短信验证码不能为空"
        }
    )

    # 2. 校验用户名是否已被注册
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if models.User.objects.filter(username=username).exists():
            raise forms.ValidationError("用户名已经被注册，请重新输入")
        return username

    # 3. 校验手机号是否已被注册
    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile")
        if models.User.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError("手机号已被注册，请重新输入")
        return mobile

    # 4. 联合校验获取到清洗后的数据
    def clean(self):
        cleaned_data = super().clean()
        cleaned_mobile = cleaned_data.get("mobile")
        cleaned_sms_code = cleaned_data.get("sms_text")

        redis_obj = get_redis_connection("verify")
        sms_key = "sms_code_{}".format(cleaned_mobile).encode("utf8")  # 短信验证码
        sms_repeat_key = "sms_sixty_{}".format(cleaned_mobile).encode("utf8")  # 短信过期
        redis_sms_text = redis_obj.get(sms_key)
        redis_sms_repeat_text = redis_obj.get(sms_repeat_key)

        # 用完后就删除该键
        redis_obj.delete(sms_key)
        redis_obj.delete(sms_repeat_key)

        if not redis_sms_repeat_text:
            raise forms.ValidationError("短信验证码已经过期，请重新获取")

        if (not redis_sms_text) or (cleaned_sms_code != redis_sms_text.decode("utf8")):
            raise forms.ValidationError("短信验证码不正确，请重新输入")


class LoginForm(forms.Form):
    """
    check login field
    param: login_name、password、is_remember_me
    """
    # 1. 校验字段
    login_name = forms.CharField()
    password = forms.CharField(
        max_length=18,
        min_length=6,
        error_messages={
            "max_length": "密码格式不正确",
            "min_length": "密码格式不正确",
            "required": "密码不能为空",
        }
    )
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_login_name(self):
        login_name = self.cleaned_data.get("login_name")

        if not login_name:
            raise forms.ValidationError("登录名不能为空")

        if not (re.match(r'^1[3-9]\d{9}', login_name)) and len(login_name) < 5 or len(login_name) > 18:
            raise forms.ValidationError("登录名格式不正确")

        return login_name

    def clean(self):
        cleaned_data = super().clean()
        login_name = cleaned_data.get("login_name")
        password = cleaned_data.get("password")
        remember_me = cleaned_data.get("remember_me")

        user_queryset = models.User.objects.filter(Q(username=login_name) | Q(mobile=login_name))

        if user_queryset:
            user = user_queryset.first()
            if user.check_password(password):
                if remember_me:
                    self.request.session.set_expiry(contains.SESSION_EXPIRE_TIME)  # None是14天
                else:
                    self.request.session.set_expiry(0)
                login(self.request, user)
            else:
                raise forms.ValidationError("密码不正确，请重新输入")
        else:
            raise forms.ValidationError("用户名不存在，请重新输入")


class ResetPasswordForm(forms.Form):
    login_name = forms.CharField()
    old_password = forms.CharField(
        max_length=20,
        min_length=6,
        error_messages={
            "max_length": "密码格式不正确",
            "min_length": "密码格式不正确",
            "required": "密码不能为空"
        }
    )
    new_password = forms.CharField(
        max_length=20,
        min_length=6,
        error_messages={
            "max_length": "密码格式不正确",
            "min_length": "密码格式不正确",
            "required": "密码不能为空"
        }
    )
    re_new_password = forms.CharField(
        max_length=20,
        min_length=6,
        error_messages={
            "max_length": "密码格式不正确",
            "min_length": "密码格式不正确",
            "required": "密码不能为空"
        }
    )

    # 单独校验登录名
    def clean_login_name(self):
        login_name = self.cleaned_data.get("login_name")
        if not login_name:
            raise forms.ValidationError("登录名不能为空")

        if not re.match(r"^1[3-9]{9}$]", login_name) and len(login_name) < 5 \
                or len(login_name) > 18:
            raise forms.ValidationError("登录名格式不正确")

        return login_name

    def clean(self):
        cleaned_data = super().clean()
        login_name = cleaned_data.get("login_name")
        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        re_new_password = cleaned_data.get("re_new_password")

        user_queryset = models.User.objects.filter(Q(username=login_name) |
                                                   Q(mobile=login_name))

        if user_queryset:
            user = user_queryset.first()
            if user.check_password(old_password):  # 判断密码是否和登录名对的上
                if new_password == re_new_password:  # 判断新密码输入是否一致
                    if old_password != new_password:  # 判断新密码和旧密码是否一致
                        user.set_password(new_password)  # 更新新密码
                        user.save()
                    else:
                        raise forms.ValidationError("密码未做修改")
                else:
                    raise forms.ValidationError("新密码前后输入不一致，请重新输入")
            else:
                raise forms.ValidationError("密码输入不正确，请重新输入密码")
        else:
            raise forms.ValidationError("用户名不存在，请重新输入")


mobile_regex = RegexValidator(r"^1[3-9]\d{9}$","手机号格式不正确")
zip_code_regex = RegexValidator(r"^\d{6}$","邮编格式不正确")


class AddressForm(forms.Form):
    receiver = forms.CharField(
        max_length=18,
        min_length=1,
        error_messages={
            "max_length": "收件人姓名格式不正确",
            "min_length": "收件人姓名格式不正确",
            "required": "收件人姓名不能为空"
        }
    )

    address = forms.CharField(
        max_length=200,
        min_length=1,
        error_messages={
            "max_length": "收件人地址格式不正确",
            "min_length": "收件人地址格式不正确",
            "required": "收件人地址不能为空"
        }
    )

    zip_code = forms.CharField(
        validators=[zip_code_regex],
        max_length=6,
        min_length=6,
        error_messages={
            "max_length": "邮编长度不正确",
            "min_length": "邮编长度不正确",
            "required": "邮编不能为空"
        })

    phone = forms.CharField(
        validators = [mobile_regex],
        max_length=11,
        min_length=11,
        error_messages={
            "max_length": "手机号长度不正确",
            "min_length": "手机号长度不正确",
            "required": "密码不能为空"
        }
    )

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop("user_id")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        receiver = cleaned_data.get("receiver")
        address = cleaned_data.get("address")
        zip_code = cleaned_data.get("zip_code")
        phone = cleaned_data.get("phone")

        address_data = {
            "user_id": self.user_id,
            "receiver": receiver,
            "addr": address,
            "zip_code": zip_code,
            "phone": phone,
            "is_default": True
        }

        # 可以使用get_or_create获取或者是创建
        if models.Address.objects.filter(**address_data):
            return forms.ValidationError("该地址已存在，请重新添加新地址")

        models.Address.objects.create(**address_data)

