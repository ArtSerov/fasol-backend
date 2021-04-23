from rest_framework import serializers
from .models import CustomUser


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('phone', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = CustomUser
        fields = ('id', 'phone', 'password', 'first_name', 'last_name', 'address')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class ResetPasswordPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class ResetPasswordVerificationCodeSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=5)


class NewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    confirm_password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    code = serializers.CharField(max_length=5)
    user_id = serializers.CharField(max_length=255)
