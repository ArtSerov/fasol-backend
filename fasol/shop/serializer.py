from rest_framework import serializers

from .models import Category, Subcategory, Product, Basket, BasketProduct, Order
from users.models import CustomUser


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubcategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, read_only=True)

    class Meta:
        model = Subcategory
        fields = "__all__"


class SubcategoryCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="id", many=False, queryset=Category.objects, read_only=False)

    class Meta:
        model = Subcategory
        fields = "__all__"


class ProductListSerializer(serializers.ModelSerializer):
    subcategory = serializers.SlugRelatedField(slug_field="name", many=False, read_only=True)

    class Meta:
        model = Product
        exclude = ('description',)


class ProductDetailSerializer(serializers.ModelSerializer):
    subcategory = SubcategorySerializer(many=False, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class ProductCreateSerializer(serializers.ModelSerializer):
    subcategory = serializers.SlugRelatedField(slug_field="id",
                                               queryset=Subcategory.objects,
                                               many=False,
                                               read_only=False,
                                               )

    class Meta:
        model = Product
        fields = "__all__"


class BasketProductSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(slug_field="name", many=False, read_only=True)

    class Meta:
        model = BasketProduct
        fields = ("id", "product", "quantity", "total_price")


class BasketSerializer(serializers.ModelSerializer):
    products = BasketProductSerializer(many=True, read_only=True)

    class Meta:
        model = Basket
        fields = "__all__"


class AddToBasketSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = Product
        fields = ("id",)


class ChangeQTYBasketProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    action = serializers.CharField(required=True)

    class Meta:
        model = BasketProduct
        fields = ("id", "action")


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ("customer", "basket", "status", "order_date")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
