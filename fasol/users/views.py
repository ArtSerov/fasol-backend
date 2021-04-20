import self as self
from django.shortcuts import render
from rest_framework import status, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import RegisterUserSerializer, CustomUserSerializer


class CustomUserRegistration(generics.GenericAPIView):
    permission_classes = [AllowAny]
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
