from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .utils import recalculation_basket
from .serializer import (
    CategorySerializer,
    SubcategorySerializer,
    SubcategoryCreateSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateSerializer,
    BasketSerializer,
    AddToBasketSerializer,
    ChangeQTYBasketProductSerializer,
    OrderCreateSerializer,
    OrderSerializer,
)
from .models import Category, Subcategory, Product, Basket, BasketProduct, Order
from users.models import CustomUser
from .mixins import BasketMixin, ViewSetActionPermissionMixin


class CategoriesView(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_action_classes = {
        'create': [IsAdminUser],
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'update': [IsAdminUser],
        'destroy': [IsAdminUser],
        'partial_update': [IsAdminUser]
    }


class SubcategoriesView(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()

    permission_action_classes = {
        'create': [IsAdminUser],
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'update': [IsAdminUser],
        'destroy': [IsAdminUser],
        'partial_update': [IsAdminUser]
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return SubcategorySerializer
        if self.action == 'create':
            return SubcategoryCreateSerializer


class ProductView(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'subcategory__name']
    ordering_fields = ['price', 'name']

    permission_action_classes = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'create': [IsAdminUser],
        'update': [IsAdminUser],
        'destroy': [IsAdminUser],
        'partial_update': [IsAdminUser]
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action == 'retrieve':
            return ProductDetailSerializer
        else:
            return ProductCreateSerializer


class BasketView(BasketMixin, viewsets.ModelViewSet):
    permission_classes = IsAuthenticated

    @action(detail=True)
    def retrieve(self, request, *args, **kwargs):
        serializer = BasketSerializer(self.basket)
        return Response(serializer.data)


class AddToBasketView(BasketMixin, viewsets.ModelViewSet):
    serializer_class = AddToBasketSerializer
    permission_classes = IsAuthenticated

    @action(detail=True, methods=['post'])
    def add_to_basket(self, request, *args, **kwargs):
        product = Product.objects.get(id=request.data.get('id'))
        basket_product, created = BasketProduct.objects.get_or_create(
            user=self.basket.owner, basket=self.basket, product=product
        )
        if created:
            self.basket.products.add(basket_product)
            recalculation_basket(self.basket)
            return Response({'message': "The product was successfully added to the basket!"}, status=status.HTTP_201_CREATED)
        return Response({'message': "The product is already existing in the basket!"}, status=status.HTTP_200_OK)


class ChangeProductQTYView(BasketMixin, viewsets.ModelViewSet):
    serializer_class = ChangeQTYBasketProductSerializer
    permission_classes = IsAuthenticated

    @action(detail=True, methods=['post'])
    def change_qty(self, request, *args, **kwargs):
        basket_product = BasketProduct.objects.get(
            id=request.data.get('id'), user=self.basket.owner, basket=self.basket,
        )
        if request.data.get('action') == "addition":
            basket_product.quantity += 1
        elif request.data.get('action') == 'subtraction' and basket_product.quantity != 1:
            basket_product.quantity -= 1
        basket_product.save()
        recalculation_basket(self.basket)
        return Response({'message': "The product quantity has been changed!"}, status=status.HTTP_200_OK)


class DeleteFromBasketView(BasketMixin, viewsets.ModelViewSet):
    serializer_class = AddToBasketSerializer
    ermission_classes = IsAuthenticated

    @action(detail=True, methods=['post'])
    def destroy(self, request, *args, **kwargs):
        product = Product.objects.get(id=request.data.get('id'))
        basket_product = BasketProduct.objects.get(
            user=self.basket.owner, basket=self.basket, product=product
        )
        self.basket.products.remove(basket_product)
        basket_product.delete()
        recalculation_basket(self.basket)
        return Response({'message': "The product was successfully removed from the basket!"}, status=status.HTTP_200_OK)


class OrderView(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        customer = CustomUser.objects.get(user=self.request.user)
        return Order.objects.filter(customer=customer)


class OrderCreateView(BasketMixin, viewsets.ModelViewSet):
    serializer_class = OrderCreateSerializer

    @action(detail=True, methods=['post'])
    def create(self, request, *args, **kwargs):
        customer = CustomUser.objects.get(user=request.user)
        new_order = Order.objects.create(
            customer=customer,
            first_name=request.data.get('first_name'),
            last_name=request.data.get('last_name'),
            phone=request.data.get('phone'),
            address=request.data.get('address'),
            buying_type=request.data.get('buying_type'),
            comment=request.data.get('comment')
        )
        new_order.save()
        self.basket.in_order = True
        self.basket.save()
        new_order.basket = self.basket
        new_order.save()
        customer.orders.add(new_order)
        return Response("Заказ успешно оформлен!")
