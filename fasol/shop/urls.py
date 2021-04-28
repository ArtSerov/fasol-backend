from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    CategoriesView,
    SubcategoriesView,
    ProductView,
    BasketView,
    AddToBasketView,
    DeleteFromBasketView,
    ChangeProductQTYView,
    OrderCreateView,
    OrderView,
)


categories_list = CategoriesView.as_view({
    'get': 'list',
    'post': 'create',
})
categories_detail = CategoriesView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

subcategories_list = SubcategoriesView.as_view({
    'get': 'list',
    'post': 'create'
})
subcategories_detail = SubcategoriesView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

products_list = ProductView.as_view({
    'get': 'list',
    'post': 'create',
})
products_detail = ProductView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
baskets = BasketView.as_view({
    'get': 'retrieve',
})
orders_list = OrderView.as_view({
    'get': 'list'
})
orders_detail = OrderView.as_view({
    'get': 'retrieve',
})


urlpatterns = format_suffix_patterns([
    path('categories/', categories_list, name="categories_list"),
    path('categories/<int:pk>', categories_detail, name="categories_detail"),

    path('subcategories/', subcategories_list, name="subcategories_list"),
    path('subcategories/<int:pk>', subcategories_detail, name="subcategories_detail"),

    path('products/', products_list, name="products_list"),
    path('products/<int:pk>', products_detail, name="products_detail"),

    path('orders/', orders_list, name="order_list"),
    path('orders/<int:pk>', orders_detail, name="order_detail"),
    path('order-create/', OrderCreateView.as_view({'post': 'create'}), name="order_create"),

    path('basket/', baskets, name="basket"),
    path('add-to-basket/', AddToBasketView.as_view({'post': 'add_to_basket'}), name="add_to_basket"),
    path('remove-from-basket/', DeleteFromBasketView.as_view({'post': 'destroy'}), name="remove_from_basket"),
    path('change-product-qty/', ChangeProductQTYView.as_view({'post': 'change_qty'}), name="change_product_qty/"),
])
