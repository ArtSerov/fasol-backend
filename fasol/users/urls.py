from django.urls import path
from .views import CustomUserRegistration, UserRetrieveUpdateView

user_detail = UserRetrieveUpdateView.as_view({
    'get': 'retrieve',
    'patch': 'update',
})


urlpatterns = [
    path('register/', CustomUserRegistration.as_view(), name='register_user'),
    path('user/', user_detail, name="user_detail"),
]
