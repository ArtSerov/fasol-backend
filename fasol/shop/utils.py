from django.db import models


def recalculation_basket(basket):
    basket_data = basket.products.aggregate(models.Sum("total_price"), models.Sum("quantity"))
    if basket_data['total_price__sum']:
        basket.total_price = basket_data['total_price__sum']
    else:
        basket.total_price = 0
    if basket_data["quantity__sum"]:
        basket.total_products = basket_data["quantity__sum"]
    else:
        basket.total_products = 0
    basket.save()
