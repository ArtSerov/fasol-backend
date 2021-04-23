from django.views.generic import View

from .models import Basket
from users.models import CustomUser


class BasketMixin(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = CustomUser.objects.filter(user=request.user).first()
            if not customer:
                customer = CustomUser.objects.create(
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


class ViewSetActionPermissionMixin(View):
    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_action_classes[self.action]
            ]
        except KeyError:
            if self.action:
                action_func = getattr(self, self.action, {})
                action_func_kwargs = getattr(action_func, "kwargs", {})
                permission_classes = action_func_kwargs.get(
                    "permission_classes"
                )
            else:
                permission_classes = None

            return [permission() for permission in (permission_classes or self.permission_classes)]
