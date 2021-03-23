from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Product)
admin.site.register(BasketProduct)
admin.site.register(Basket)
admin.site.register(Customer)


