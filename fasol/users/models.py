from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import random


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, phone, user_name, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True')

        return self.create_user(phone, user_name, password, **other_fields)

    def create_user(self, phone, user_name, password, **other_fields):
        user = self.model(phone=phone, user_name=user_name, **other_fields)
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=12, verbose_name='Мобильный телефон', unique=True)
    user_name = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=150, verbose_name='Имя', null=True, blank=True)
    last_name = models.CharField(max_length=150, verbose_name='Фамилия', null=True, blank=True)
    orders = models.ManyToManyField("shop.Order", verbose_name='Заказы', related_name='related_customer')
    start_date = models.DateTimeField(default=timezone.now)
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['user_name']

    def __str__(self):
        return f"Покупатель {self.phone}"


class Code(models.Model):
    number = models.CharField(max_length=5, blank=True)
    creation_date = models.DateTimeField(default=timezone.now)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.number)

    def save(self, *args, **kwargs):
        number_list = [x for x in range(10)]
        code_items = []

        for i in range(5):
            num = random.choice(number_list)
            code_items.append(num)
        code_string = "".join(str(item) for item in code_items)
        self.number = code_string
        self.creation_date = timezone.now()
        super().save(*args, **kwargs)
