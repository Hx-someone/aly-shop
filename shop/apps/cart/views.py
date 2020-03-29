from django.shortcuts import render
import json

from django.views import View
from utils.json_code.to_json import to_json
from utils.json_code.status_code import Code, error_map
from goods.models import GoodsSKU, IndexGoodsBanner, GoodsType, IndexPromotionBanner, GoodsComments
from django_redis import get_redis_connection


class CartIndexView(View):
    def get(self,request):
        user = request.user

        cart_conn = get_redis_connection("cart")
        cart_key = "cart_{}".format(user.id)
        cart_dict = cart_conn.hgetall(cart_key) # 获取该用户的所有购物车商品情况

        total_price = 0
        total_count = 0
        goods_ls = []
        for sku_id,count in cart_dict.items():
            goods = GoodsSKU.objects.only("name","price","unite","image").filter(is_delete=False,id=sku_id).first()

            # 计算价格
            amount = goods.price * int(count)
            goods.amount = amount  # 给该商品增加一个小计价格
            goods.count = int(count) # 给该商品增加一个数量
            total_price += amount

            # 计算商品总数目
            total_count +=int(count)

            goods_ls.append(goods)

        context = {
            "total_price":total_price,
            "total_count": total_count,
            "goods_ls": goods_ls
        }

        return render(request, 'cart/cart_index.html',context=context)

class AddCartView(View):
    """购物车添加"""

    def post(self, request):
        user = request.user  # 如果是游客怎么办？
        if not user.is_authenticated:
            return to_json(errmsg="请先登录后再添加购物车！")

        json_data = request.body

        if not json_data:
            return to_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        dict_data = json.loads(json_data.decode("utf-8"))

        sku_id = dict_data.get("sku_id")
        if not sku_id:
            return to_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        count = int(dict_data.get("count").strip())
        if not count:
            return to_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        try:
            goods = GoodsSKU.objects.only("id").filter(is_delete=False, id=sku_id).first()

        except GeneratorExit:
            return to_json(errno=Code.PARAMERR, errmsg="商品不存在")

        # 判断redis中存储的商品个数

        redis_conn = get_redis_connection("cart")
        cart_key = "cart_{}".format(user.id)  # 如果是游客怎么办？

        redis_count = redis_conn.hget(cart_key, sku_id)
        if redis_count:
            count += int(redis_count)  # 累计购物车中的商品件数

        if count > goods.stock:
            return to_json(errmsg="商品存库不足")

        # 存储数据到redis中
        redis_conn.hset(cart_key, sku_id, count)
        data = {
            "count":count
        }
        return to_json(data=data, errno=Code.OK, errmsg="购物车添加成功")

    def put(self,request,goods_id):
        GoodsSKU.objects.only().filter(is_delete=False,id=goods_id).first()
        pass


