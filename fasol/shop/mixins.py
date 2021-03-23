from django.views.generic import View

from .models import Customer, Basket


class BasketMixin(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )
            basket = Basket.objects.filter(owner=customer, in_order=False).first()
            if not basket:
                basket = Basket.objects.create(owner=customer)
        else:
            basket = Basket.objects.filter(for_anonymous_user=True).first()
            if not basket:
                basket = Basket.objects.create(for_anonymous_user=True)
        self.basket = basket
        return super().dispatch(request, *args, **kwargs)
