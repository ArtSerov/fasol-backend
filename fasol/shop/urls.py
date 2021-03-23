from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    CategoriesView,
    SubcategoriesView,
    ProductView,
    BasketView,
    AddToBasketView,
    DeleteFromBasketView,
    ChangeProductQTYView
)


categories = CategoriesView.as_view({
    'get': 'list',
    'post': 'create'
})

subcategories = SubcategoriesView.as_view({
    'get': 'list',
    'post': 'create'
})

products_list = ProductView.as_view({
    'get': 'list',
})

products_detail = ProductView.as_view({
    'get': 'retrieve',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
basket = BasketView.as_view({
    'get': 'retrieve',
})


urlpatterns = format_suffix_patterns([
    path('categories/', categories, name="categories"),
    path('subcategories/', subcategories, name="subcategories"),
    path('products/', products_list, name="products_list"),
    path('products/<int:pk>', products_detail, name="products_detail"),
    path('basket/', basket, name="basket"),
    path('add-to-basket/', AddToBasketView.as_view({'post': 'create'}), name="add_to_basket"),
    path('remove-from-basket/', DeleteFromBasketView.as_view({'post': 'destroy'}), name="remove_from_basket"),
    path('change-product-qty/', ChangeProductQTYView.as_view({'post': 'change_qty'}), name="change-product-qty/")
])