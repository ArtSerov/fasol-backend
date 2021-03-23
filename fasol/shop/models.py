from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    representation = models.ImageField(upload_to="сategory/", null=True, blank=True, verbose_name='Изображение')
    # slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category,
                                 verbose_name='Категория',
                                 on_delete=models.CASCADE,
                                 related_name='related_category')

    name = models.CharField(max_length=255, verbose_name='Имя подкатегории')
    # slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    subcategory = models.ForeignKey(Subcategory, null=True, verbose_name='Подкатегория', on_delete=models.SET_NULL)

    name = models.CharField(max_length=255, verbose_name='Наименование товара')
    description = models.TextField(verbose_name='Описание')
    representation = models.ImageField(upload_to="product/", verbose_name='Изображение')
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Цена')

    def get_absolute_url(self):
        return reverse("actor_detail", kwargs={'slug': self.name})

    def __str__(self):
        return self.name


class BasketProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    basket = models.ForeignKey(
        'Basket', verbose_name='Корзина',
        on_delete=models.CASCADE,
        related_name='related_products')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name='Итого')

    def __str__(self):
        return f"Продукт {self.product.name} для корзины {self.basket.id}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.product.price
        super().save(*args, **kwargs)


class Basket(models.Model):
    owner = models.ForeignKey('Customer', null=True, verbose_name='Покупатель', on_delete=models.CASCADE)
    products = models.ManyToManyField(BasketProduct, blank=True, related_name='related_basket')

    total_products = models.PositiveIntegerField(default=0,)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name='Итого')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        basket_data = self.products.aggregate(models.Sum("total_price"), models.Sum("quantity"))
        if basket_data['total_price__sum']:
            self.total_price = basket_data['total_price__sum']
        else:
            self.total_price = 0
        if basket_data["quantity__sum"]:
            self.total_products = basket_data["quantity__sum"]
        else:
            self.total_products = 0
        super().save(*args, **kwargs)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Покупатель', on_delete=models.CASCADE)
    orders = models.ManyToManyField('Order', verbose_name='Заказы', related_name='related_customer')
    phone = models.CharField(max_length=12, verbose_name='Мобильный телефон', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)

    def __str__(self):
        return f"Покупатель {self.phone}"


class Order(models.Model):
    STATUS_NOW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'status_ready'
    STATUS_COMPLETED = 'status_completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'
    STATUS_CHOICES = (
        (STATUS_NOW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(
        Customer,
        verbose_name='Покупатель',
        related_name='related_orders',
        on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.CharField(max_length=100, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Статус заказа',
        choices=STATUS_CHOICES,
        default=STATUS_NOW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_DELIVERY
    )
    comment = models.TextField(verbose_name='Коментарий к заказу', null=True, blank=True)
    order_date = models.DateTimeField(auto_now=True, verbose_name='Дата заказа')