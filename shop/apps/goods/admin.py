from django.contrib import admin
from celery_tasks.static_html.tasks import get_index_static_html

from goods.models import GoodsType, GoodsSKU, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner, Goods
from django.core.cache import cache


# 后台更改表数据时会调用该方法ModelAdmin  作为基类来
class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """后台修改表中数据时调用"""
        super().save_model(request, obj, form, change)

        # 调用方法时celery重新生成静态页面
        get_index_static_html.delay()

        # 当修改后台数据时删除掉缓存
        cache.delete("index_static_data")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)

        get_index_static_html.delay()

        # 当修改后台数据时删除掉缓存
        cache.delete("index_static_data")


class IndexGoodsBannerAdmin(BaseModelAdmin):
    """主页商品轮播图后台修改后静态页面生成"""
    pass


class GoodsAdmin(BaseModelAdmin):
    """主页商品后台修改后静态页面生成"""
    pass


class GoodsSKUAdmin(BaseModelAdmin):
    """主页商品SKU后台修改后静态页面生成"""
    pass


class GoodsTypeAdmin(BaseModelAdmin):
    """主页商品类型后台修改后静态页面生成"""
    pass


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    """主页商品类型轮播图后台修改后静态页面生成"""
    pass


class IndexPromotionBannerAdmin(BaseModelAdmin):
    """主页商品促销后台修改后静态页面生成"""
    pass


admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
