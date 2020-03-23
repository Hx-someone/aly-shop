from django.shortcuts import render
from django.views import View
from utils.json_code.status_code import Code, error_map
from utils.json_code.to_json import to_json
import json
import re
from user.forms import RegisterForm, LoginForm
import logging
from user import models
import random
from django_redis import get_redis_connection
from user import contains
from django.contrib.auth import login, logout
from django.shortcuts import redirect, reverse

logger = logging.getLogger("django")


class CheckUsernameView(View):
    """
    create username verify view

    # 1. 创建一个类
    request: GET
    params: username
    """

    # 2. 创建个get方法来处理逻辑
    def get(self, request, username):
        # 3. 从数据库中查看是否存在该用户
        data = {
            "username": username,
            "count": models.User.objects.only("id").filter(username=username).count()  # 获取数据库中有几条这个信息:无则0
        }

        # 4. 返回到前端
        return to_json(data=data)


class CheckMobileView(View):
    """
    create mobile verify view

    # 1.创建一个类
    request: GET
    params: mobile
    """

    # 2. 创建个get方法来处理逻辑
    def get(self, request, mobile):
        # 3. 从数据库中查看是否存在该用户
        data = {
            "mobile": mobile,
            "count": models.User.objects.only('mobile').filter(mobile=mobile).count()
        }
        # 5. 返回到前端

        return to_json(data=data)


class SmsCodeView(View):
    """
    # 1. 创建一个SmsCodeView类
    param: mobile、image_text、image_code_id
    """

    def post(self, request):
        json_data = request.body
        dict_data = json.loads(json_data)

        mobile = dict_data.get("mobile")
        if not mobile:
            return to_json(errno=Code.PARAMERR, errmsg="手机号为空")

        if not re.match(r'^1[3-9]\d{9}', mobile):
            return to_json(errno=Code.PARAMERR, errmsg="手机号格式不正确")

        sms_text = "%06d" % random.randint(0, 999999)

        redis_obj = get_redis_connection("verify")
        sms_text_key = "sms_code_{}".format(mobile).encode("utf8")
        sms_repeat_key = "sms_sixty_{}".format(mobile).encode("utf8")

        redis_obj.setex(sms_text_key, contains.SMS_CODE_EXPIRE_TIME, sms_text)  # key, expire_time, value
        redis_obj.setex(sms_repeat_key, contains.SMS_CODE_EXPIRE_TIME, contains.SMS_REPEAT_EXPIRE_TIME)

        logger.info("发送短信正常[mobile:%s sms_num:%s]" % (mobile, sms_text))
        return to_json(errmsg="短信发送成功")  # 短信调试

        # # 使用用通讯插件发送短信
        # try:
        #     result = CCP().send_Template_sms(mobile, [sms_text, contains.SMS_CCP_EXPIRE_TIME], contains.SMS_TEMPLATE)
        # except Exception as e:
        #     logger.error("短信发送异常[mobile:{},error:{}]".format(mobile, e))
        #     return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])  # 短信发送异常
        # else:
        #     if result == 0:  # 发送成功
        #         logger.info("短信发送成功[mobile:{},sms_code:{}]".format(mobile, sms_text))
        #         return to_json_data(errmsg="短信发送正常")
        #     else:  # 发送失败
        #         logger.warning("短信发送失败[mobile:{}]".format(mobile))
        #         return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])


class RegisterView(View):
    def get(self, request):
        return render(request, 'user/register.html')

    def post(self, request):

        json_data = request.body

        if json_data:
            dict_data = json.loads(json_data.decode("utf-8"))
        else:
            return to_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        form = RegisterForm(dict_data)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            mobile = form.cleaned_data.get("mobile")
            password = form.cleaned_data.get("password")

            models.User.objects.create_user(username=username, password=password, mobile=mobile)

            return to_json(errmsg="恭喜您注册成功")

        else:
            err_msg_list = []

            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_str = "/".join(err_msg_list)

            return to_json(errno=Code.PARAMERR, errmsg=err_str)


class LoginView(View):
    """
    # 1. 创建一个LoginView类
    deal login
    param: login_name、password、is_remember_me
    """

    def get(self, request):
        return render(request, "user/login.html")

    def post(self, request):

        json_data = request.body
        if not json_data:
            return to_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])  # 参数错误

        dict_data = json.loads(json_data.decode("utf-8"))

        form = LoginForm(data=dict_data, request=request)

        if form.is_valid():

            return to_json(errmsg="恭喜您登录成功")

        else:
            err_msg_list = []

            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_str = "/".join(err_msg_list)

            return to_json(errno=Code.PARAMERR, errmsg=err_str)


class LogoutView(View):
    """
    logout view
    """

    def get(self, request):
        logout(request)
        return redirect(reverse("user:login"))  # 重定向到登录界面

# class ResetPasswordView(View):
#     """
#     修改密码
#     """
#     def get(self, request):
#         return render(request, 'user/reset_password.html')
#
#     def post(self, requests):
#         try:
#             json_data = requests.body
#             if not json_data:
#                 return to_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
#             dict_data = json.loads(json_data)
#         except Exception as e:
#             return to_json(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])
#
#         form = ResetPasswordForm(dict_data)
#         if form.is_valid():
#             return to_json(errmsg="修改密码成功")
#
#         else:
#             err_msg_list = []
#             for item in form.errors.values():
#                 err_msg_list.append(item[0])
#             err_str = '/'.join(err_msg_list)
#             return to_json(errno=Code.PARAMERR, errmsg=err_str)
