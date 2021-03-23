from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializer import (
    CategorySerializer,
    SubcategorySerializer,
    SubcategoryCreateSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateSerializer,
    BasketSerializer,
    AddToBasketSerializer,
    ChangeQTYBasketProductSerializer)
from .models import Category, Subcategory, Product, Basket, Customer, BasketProduct
from .mixins import BasketMixin


class CategoriesView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubcategoriesView(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list':
            return SubcategorySerializer
        if self.action == 'create':
            return SubcategoryCreateSerializer


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()

    def get_serializer_class(self):
        print(self.request)
        if self.action == 'list':
            return ProductListSerializer
        if self.action == 'retrieve':
            return ProductDetailSerializer
        else:
            return ProductCreateSerializer


class BasketView(BasketMixin, viewsets.ModelViewSet):

    @action(detail=True)
    def retrieve(self, request, *args, **kwargs):
        serializer = BasketSerializer(self.basket)
        return Response(serializer.data)


class AddToBasketView(BasketMixin, viewsets.ModelViewSet):
    serializer_class = AddToBasketSerializer

    @action(detail=True, methods=['post'])
    def create(self, request, *args, **kwargs):
        product = Product.objects.get(id=request.data.get('id'))
        basket_product, created = BasketProduct.objects.get_or_create(
            user=self.basket.owner, basket=self.basket, product=product
        )
        if created:
            self.basket.products.add(basket_product)
            self.basket.save()
            return Response("Товар добавлен в корзину!")
        return Response("Товар уже есть в корзине!")


class ChangeProductQTYView(BasketMixin, viewsets.ModelViewSet):
    serializer_class = ChangeQTYBasketProductSerializer

    @action(detail=True, methods=['post'])
    def change_qty(self, request, *args, **kwargs):
        basket_product = BasketProduct.objects.get(
            id=request.data.get('id'), user=self.basket.owner, basket=self.basket,
        )
        if request.data.get('action') == "addition":
            basket_product.quantity += 1
        elif request.data.get('action') == 'subtraction' and basket_product.quantity != 1:
            print(basket_product.quantity)
            basket_product.quantity -= 1
        basket_product.save()
        self.basket.save()
        return Response("Количество тавара изменено!")


class DeleteFromBasketView(BasketMixin, viewsets.ModelViewSet):
    serializer_class = AddToBasketSerializer

    @action(detail=True, methods=['post'])
    def destroy(self, request, *args, **kwargs):
        product = Product.objects.get(id=request.data.get('id'))
        basket_product = BasketProduct.objects.get(
            user=self.basket.owner, basket=self.basket, product=product
        )
        self.basket.products.remove(basket_product)
        basket_product.delete()
        self.basket.save()
        return Response("Товар удален из корзины!")
