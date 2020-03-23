# -*- coding: utf-8 -*-

from django.http import JsonResponse

from utils.json_code.status_code import Code


# 处理json格式转化，并加入异常码和异常信息
def to_json(errno=Code.OK, errmsg='', data=None, **kwargs):
    """
    返回给前端 json数据以及错误信息
    :param errno: 错误代码
    :param errmsg: 错误信息
    :param data: 数据
    :param kwargs: 不定长数据
    :return:
    """
    json_dict = {'errno': errno, 'errmsg': errmsg, 'data': data}

    if kwargs:
        json_dict.update(kwargs)

    return JsonResponse(json_dict)
