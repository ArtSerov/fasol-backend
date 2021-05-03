from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
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
    BasketProductSerializer,
    OrderStatusChangingSerializer
)
from .models import Category, Subcategory, Product, Basket, BasketProduct, Order
from users.models import CustomUser
from .mixins import ViewSetActionPermissionMixin


class CategoriesView(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_action_classes = {
        'list': [IsAuthenticated],
        'retrieve': [AllowAny],
        # 'create': [IsAdminUser],
        # 'update': [IsAdminUser],
        'destroy': [IsAdminUser],
        # 'partial_update': [IsAdminUser]
    }


class SubcategoriesView(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()

    permission_action_classes = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        # 'create': [IsAdminUser],
        # 'update': [IsAdminUser],
        # 'destroy': [IsAdminUser],
        # 'partial_update': [IsAdminUser]
    }

    def get_serializer_class(self):
        if self.action == 'create':
            return SubcategoryCreateSerializer
        return SubcategorySerializer


class ProductView(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'subcategory__name']
    ordering_fields = ['price', 'name']

    permission_action_classes = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        # 'create': [IsAdminUser],
        # 'update': [IsAdminUser],
        # 'destroy': [IsAdminUser],
        # 'partial_update': [IsAdminUser]
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action == 'retrieve':
            return ProductDetailSerializer
        else:
            return ProductCreateSerializer


class BasketView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True)
    def retrieve(self, request, *args, **kwargs):
        customer = CustomUser.objects.filter(phone=request.user.phone).first()
        basket = Basket.objects.filter(owner=customer, in_order=False).first()
        serializer = BasketSerializer(basket)
        return Response(serializer.data)


class AddToBasketView(viewsets.ModelViewSet):
    serializer_class = AddToBasketSerializer
    permission_classes = [IsAuthenticated, ]

    @action(detail=True, methods=['post'])
    def add_to_basket(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            customer = CustomUser.objects.filter(phone=request.user.phone).first()
            basket = Basket.objects.filter(owner=customer, in_order=False).first()
            if not basket:
                basket = Basket.objects.create(owner=customer)

            try:
                product = Product.objects.get(id=request.data.get('id'))
            except ObjectDoesNotExist:
                return Response({"error": f"объект с id={request.data.get('id')} не найден!"},
                                status=status.HTTP_400_BAD_REQUEST)

            basket_product, created = BasketProduct.objects.get_or_create(
                user=basket.owner, basket=basket, product=product
            )
            if created:
                basket.products.add(basket_product)
                recalculation_basket(basket)
                return Response({
                    'message': "This product was successfully added to this basket!",
                    'basket_product': BasketProductSerializer(basket_product,
                                                              context=self.get_serializer_context()).data
                }, status=status.HTTP_201_CREATED)
            return Response({'message': "The product is already existing in the basket!"}, status=status.HTTP_200_OK)


class ChangeProductQTYView(viewsets.ModelViewSet):
    serializer_class = ChangeQTYBasketProductSerializer
    permission_classes = [IsAuthenticated, ]

    @action(detail=True, methods=['post'])
    def change_qty(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            customer = CustomUser.objects.filter(phone=request.user.phone).first()
            basket = Basket.objects.filter(owner=customer, in_order=False).first()

            try:
                basket_product = BasketProduct.objects.get(id=request.data.get('id'), user=basket.owner, basket=basket)
            except ObjectDoesNotExist:
                return Response({"error": f"Объект с id={request.data.get('id')} не найден!"},
                                status=status.HTTP_400_BAD_REQUEST)
            if request.data.get('action') == "addition":
                basket_product.quantity += 1
            elif request.data.get('action') == "subtraction":
                if basket_product.quantity == 1:
                    basket.products.remove(basket_product)
                basket_product.quantity -= 1
            else:
                return Response({"error": f"Неверное значение в поле action. Ожидалось 'addition' или 'subtraction'"},
                                status=status.HTTP_400_BAD_REQUEST)

            basket_product.save()
            recalculation_basket(basket)
            return Response({'message': "The product quantity has been changed!"}, status=status.HTTP_200_OK)


class DeleteFromBasketView(viewsets.ModelViewSet):
    serializer_class = AddToBasketSerializer
    permission_classes = [IsAuthenticated, ]

    @action(detail=True, methods=['post'])
    def destroy(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            customer = CustomUser.objects.filter(phone=request.user.phone).first()
            basket = Basket.objects.filter(owner=customer, in_order=False).first()

            basket_product = BasketProduct.objects.get(
                user=basket.owner, basket=basket, product=request.data.get('id')
            )
            basket.products.remove(basket_product)
            basket_product.delete()
            recalculation_basket(basket)
            return Response({'message': "The product was successfully removed from the basket!"},
                            status=status.HTTP_200_OK)


class OrderView(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        else:
            return Order.objects.filter(customer=self.request.user)


class OrderCreateView(viewsets.ModelViewSet):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated, ]

    @action(detail=True, methods=['post'])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            customer = CustomUser.objects.get(phone=request.user.phone)
            basket = Basket.objects.filter(owner=customer, in_order=False).first()
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
            basket.in_order = True
            basket.save()
            new_order.basket = basket
            new_order.save()
            customer.orders.add(new_order)
            return Response("Заказ успешно оформлен!")


class ChangingOrderStatusView(viewsets.ModelViewSet):
    serializer_class = OrderStatusChangingSerializer

    @action(detail=True, methods=['post'], permission_classes=IsAuthenticated)
    def change_status(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(serializer.is_valid())
        if serializer.is_valid(raise_exception=True):
            try:
                if request.user.is_staff:
                    order = Order.objects.get(id=request.data.get("id"))
                else:
                    order = Order.objects.filter(customer=request.user, id=request.data.get("id")).first()
                order.status = request.data.get("status")
                order.save()
                return Response({'message': OrderSerializer(order, context=self.get_serializer_context()).data},
                                status=status.HTTP_200_OK)
            except AttributeError:
                return Response({"error": f"Объект не найден!"},
                                status=status.HTTP_400_BAD_REQUEST)
