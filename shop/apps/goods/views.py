import json

from django.views import View
from django.urls import reverse
from django.core.cache import cache
from django.core.paginator import Paginator
from django_redis import get_redis_connection
from django.shortcuts import render, redirect
from haystack.views import  SearchView

from goods import contains

from celery_tasks.static_html.tasks import get_index_static_html
from goods.models import GoodsSKU, IndexGoodsBanner, GoodsType, IndexPromotionBanner, GoodsComments


class GoodsIndexView(View):
    """商品主页"""

    def get(self, request):
        """
        商品类型，商品轮播图，商品促销轮播图，商品信息这些保存到缓存中，这部分所有人看到的都是一样的
        :param request:
        :return:
        """
        # １．先判断是否已经缓存
        context = {}
        # context = cache.get("index_static_data")
        if not context:
            # 商品类型
            goods_types = GoodsType.objects.only("id", "name", "logo").filter(is_delete=False).order_by("id")

            # 商品主页轮播图
            index_banners = IndexGoodsBanner.objects.only("image", "sku__goods__id").filter(is_delete=False).order_by(
                "priority")

            # 商品促销轮播图
            pro_banners = IndexPromotionBanner.objects.only("url", "image").filter(is_delete=False).order_by("priority")

            for goods_type in goods_types:
                good_sku_obj = GoodsSKU.objects.only("image").filter(is_delete=False, type_id=goods_type.id).order_by(
                    "-update_time")[:4]
                goods_type.good_sku_obj = good_sku_obj

            context = {
                "goods_types": goods_types,
                "index_banners": index_banners,
                "pro_banners": pro_banners,
            }
            # 2.设置缓存
            # key，value，timeout = DEFAULT_TIMEOUT
            cache.set("index_static_data", context, timeout=1)  # 秒为单位

        # 判断用户是否已经登录
        cart_count = 0
        user = request.user
        if user.is_authenticated:
            # 获取购物车中的数量
            redis_conn = get_redis_connection("cart")
            re_key = "cart_{}".format(user.id)
            cart_count = redis_conn.hlen(re_key)
        context.update(cart_count=cart_count)

        return render(request, 'goods/index.html', context=context)


class GoodsDetailView(View):
    """商品详情"""

    def get(self, request, goods_id):

        # 1.查询到id=goods_id的商品信息
        try:
            goods = GoodsSKU.objects.only().filter(is_delete=False, id=goods_id).first()

        except GoodsSKU.DoesNotExist:  # 如果商品不存在就重定向到主页面
            return redirect(reverse("goods:index"))

        # 2. 获取到新品：获取同类型的最前面的两个产品,同时不包括上面的产品呢
        new_goods_rec = GoodsSKU.objects.only("image", "price", "name"). \
                            filter(is_delete=False, type=goods.type).exclude(id=goods.id).order_by("-create_time")[:2]

        # 获取同种类的不同规格的SPU商品
        same_goods = GoodsSKU.objects.only("name").filter(is_delete=False, goods=goods.goods).exclude(id=goods.id)

        # 4. 获取到评论
        comments = GoodsComments.objects.only().filter(is_delete=False, goods=goods.id)

        user = request.user
        if user.is_authenticated:
            # 获取商品浏览历史记录
            his_conn = get_redis_connection("history")
            his_key = "history_{}".format(request.user.id)
            # 判断列表中是否已经有了该商品
            his_conn.lrem(his_key, 0, goods.id)  # 移除浏览记录该商品
            his_conn.lpush(his_key, goods.id)  # 左侧插入
            # 只保存5条的浏览记录
            his_conn.ltrim(his_key, 0, 4)

            # 获取购物车中的商品个数
            cart_conn = get_redis_connection("cart")
            cart_key = "cart_{}".format(request.user.id)

            cart_count = cart_conn.hget(cart_key, goods_id)
            # 如果不存在就将购物车数量s设定为0
            if not cart_count:
                cart_count = 0
            cart_count = int(cart_count)


        return render(request, 'goods/detail.html', locals())


class GoodsTypeListView(View):
    """
    类型商品展示列表
    """

    def get(self, request, type_id, page):
        try:
            type = GoodsType.objects.only().filter(id=type_id, is_delete=False).first()
        except GoodsType.DoesNotExist:
            return redirect(reverse("goods:index"))

        sort = request.GET.get("sort")
        if sort == "price":  # 价格排序
            goods = GoodsSKU.objects.only().filter(is_delete=False, type=type).order_by("price")
        elif sort == "sales":  # 销量排序
            goods = GoodsSKU.objects.only().filter(is_delete=False, type=type).order_by("sales")
        elif sort == "time":  # 上架时间排序
            goods = GoodsSKU.objects.only().filter(is_delete=False, type=type).order_by("create_time")
        elif sort == "comments":  # 评论数
            goods = GoodsSKU.objects.only().filter(is_delete=False, type=type).order_by("goodscomments__goods")
        else:
            sort = "default"  # id排序
            goods = GoodsSKU.objects.only().filter(is_delete=False, type=type).order_by("id")

        # 创建分页对象
        pagin = Paginator(goods, contains.PER_PAGE_NUMBER)

        # 获取到页数
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > pagin.num_pages:  # 判读传来的页码数是否大于最大页码数
            page = pagin.num_pages  # 直接最大页

        goods_data = pagin.page(page)  # 分页对象
        # 2. 获取到新品：获取同类型的最前面的两个产品,同时不包括上面的产品呢
        new_goods_rec = GoodsSKU.objects.only("image", "price", "name"). \
                            filter(is_delete=False, type=type).order_by("-create_time")[:2]

        user = request.user
        cart_count = 0
        if user.is_authenticated:
            redis_conn = get_redis_connection("default")
            re_key = "cart_id_{}".format(user.id)
            cart_count = redis_conn.hlen(re_key)

        context = {
            "type": type,
            "new_goods_rec": new_goods_rec,
            "goods_data": goods_data,
            "sort": sort,
        }
        context.update(cart_count=cart_count)
        return render(request, 'goods/list.html', context=context)



class Search(SearchView):
    pass
    template ="goods/search"



