from django.urls import path
from .views import (
    CustomUserRegistration,
    UserRetrieveUpdateView,
    ResetPasswordPhoneView,
    ResetPasswordVerificationCodeView,
    SetNewPasswordView
)
user_detail = UserRetrieveUpdateView.as_view({
    'get': 'retrieve',
    'patch': 'update',
})


urlpatterns = [
    path('register/', CustomUserRegistration.as_view(), name='register_user'),
    path('user/', user_detail, name='user_detail'),
    path('reset_password/', ResetPasswordPhoneView.as_view(), name='reset_password'),
    path('reset_password_verify/', ResetPasswordVerificationCodeView.as_view(), name='reset_password'),
    path('set_new_password/', SetNewPasswordView.as_view(), name='set_new_password')
]
