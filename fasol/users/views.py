import self as self
from django.utils import timezone
from rest_framework import status, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import CustomUser, Code
from .serializers import RegisterUserSerializer, CustomUserSerializer, ResetPasswordPhoneSerializer, \
    ResetPasswordVerificationCodeSerializer, NewPasswordSerializer


class CustomUserRegistration(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            custom_user = serializer.save()
            if custom_user:
                return Response({"user": CustomUserSerializer(custom_user, context=self.get_serializer_context()).data,
                                 "message": "User Created Successfully.  Now perform Login to get your token",
                                 })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveUpdateView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CustomUserSerializer

    @action(detail=True, methods=['get'])
    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def update(self, request, *args, **kwargs):
        serializer_data = request.data
        print(serializer_data)
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetPasswordPhoneView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordPhoneSerializer

    def post(self, request, *args, **kwargs):
        user = CustomUser.objects.get(phone=request.data.get('phone'))
        if user:
            code, create = Code.objects.get_or_create(user=user)
            code.save()
            return Response(f"Код {code.number} сгенерирован в {code.creation_date}")
        return Response("Error!")


class ResetPasswordVerificationCodeView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordVerificationCodeSerializer

    def post(self, request, *args, **kwargs):
        code = Code.objects.get(number=request.data.get('number'))
        if ((timezone.now() - code.creation_date).total_seconds()) < 300:
            return Response({'user_id': code.user.id, 'code': code.number})
        return Response(f"Код просрочен!")


class SetNewPasswordView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = NewPasswordSerializer

    def post(self, request, *args, **kwargs):
        code = Code.objects.get(number=request.data.get('code'))
        if ((timezone.now() - code.creation_date).total_seconds()) < 300:
            user = CustomUser.objects.get(id=request.data.get('user_id'))
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')
            if password == confirm_password:
                user.set_password(password)
                user.save()
                code.delete()
                return Response("Пароль успешно изменён")
            return Response("Паароль подтверждения указан не верно!")
        return Response("Код просрочен!")
