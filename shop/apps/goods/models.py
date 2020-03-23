# -*-coding:utf-8-*-
from django.db import models
from utils.base_model.base_model import BaseModel
from tinymce.models import HTMLField


class GoodsType(BaseModel):
    """商品类型模型类"""
    name = models.CharField(max_length=20, verbose_name='商品种类名称', help_text="商品种类名称")
    logo = models.CharField(max_length=20, verbose_name='类型logo', help_text="类型logo")
    image = models.URLField(default="", verbose_name='商品类型图片', help_text="商品类型图片")

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_goods_type'
        verbose_name = '商品种类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsSKU(BaseModel):
    """商品SKU模型类"""
    status_choices = (
        (0, '下线'),
        (1, '上线')
    )
    type = models.ForeignKey('GoodsType', on_delete=models.SET_NULL, null=True, verbose_name='商品种类')
    goods = models.ForeignKey('Goods', on_delete=models.SET_NULL, null=True, verbose_name='商品SPU')
    name = models.CharField(max_length=20, verbose_name='商品名称', help_text="商品名称")
    desc = models.CharField(max_length=256, verbose_name='商品简介', help_text="商品简介")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格', help_text="价格")
    unite = models.CharField(max_length=20, verbose_name='商品单位', help_text="商品单位")
    image = models.URLField(default='', verbose_name='商品图片', help_text="商品图片")
    stock = models.IntegerField(default=1, verbose_name='商品库存', help_text="商品库存")
    sales = models.IntegerField(default=0, verbose_name='商品销量', help_text="商品销量'")
    status = models.SmallIntegerField(default=1, choices=status_choices, verbose_name='状态', help_text="状态")

    class Meta:
        ordering = ['sales', '-update_time', '-id']
        db_table = 'tb_goods_sku'
        verbose_name = '商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Goods(BaseModel):
    """商品SPU模型类"""
    name = models.CharField(max_length=20, verbose_name='商品SPU名称', help_text="商品SPU名称")
    # 富文本类型：带有格式的文本
    detail = HTMLField(blank=True, verbose_name='商品详情', help_text="商品详情")

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_goods'
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class IndexGoodsBanner(BaseModel):
    """首页轮播商品展示模型类"""
    PRI_CHOICE = [
        (1, "第一级"),
        (2, "第二级"),
        (3, "第三级"),
        (4, "第四级"),

    ]
    sku = models.ForeignKey('GoodsSKU', on_delete=models.CASCADE, verbose_name='商品', )
    image = models.URLField(default='', verbose_name='图片', help_text="图片")
    priority = models.IntegerField(default=4, choices=PRI_CHOICE,verbose_name='展示顺序', help_text="展示顺序")

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_index_banner'
        verbose_name = '首页轮播商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku.name


class IndexTypeGoodsBanner(BaseModel):
    """首页分类商品展示模型类"""
    DISPLAY_TYPE_CHOICES = (
        (0, '标题'),
        (1, '图片')
    )
    PRI_CHOICE = [
        (1, "第一级"),
        (2, "第二级"),
        (3, "第三级"),
        (4, "第四级"),
    ]

    type = models.ForeignKey('GoodsType', on_delete=models.CASCADE, verbose_name='商品类型')
    sku = models.ForeignKey('GoodsSKU', on_delete=models.CASCADE, verbose_name='商品SKU')
    display_type = models.SmallIntegerField(default=1, choices=DISPLAY_TYPE_CHOICES, verbose_name='展示类型',
                                            help_text="展示类型")
    priority = models.IntegerField(default=4, choices=PRI_CHOICE,verbose_name='展示顺序', help_text="展示顺序")

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_index_type_goods'
        verbose_name = '主页分类展示商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku.name


class IndexPromotionBanner(BaseModel):
    """轮播图促销活动模型类"""
    PRI_CHOICES = [
        (1, "第一级"),
        (2, "第二级"),
        (3, "第三级"),
        (4, "第四级"),
        (5, "第五级"),
        (6, "第六级"),
    ]
    name = models.CharField(max_length=20, verbose_name='活动名称', help_text="活动名称")
    url = models.URLField(verbose_name='活动链接', help_text="活动链接")
    image = models.URLField(default='', verbose_name='活动图片', help_text="活动图片")
    priority = models.IntegerField(default=6, choices=PRI_CHOICES, verbose_name="优先级", help_text="优先级")

    class Meta:
        ordering = ['priority', '-update_time', '-id']
        db_table = 'tb_index_promotion'
        verbose_name = '主页促销活动'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
