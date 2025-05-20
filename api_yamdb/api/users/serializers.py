from rest_framework import serializers
from users.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.validators import RegexValidator
from typing import Any, Dict


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей."""

    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы!'
            )
        ]
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        extra_kwargs: Dict[str, Dict[str, Any]] = {
            'username': {'validators': []},
            'email': {'validators': []},
        }

    def validate_username(self, value):
        # Запрещаем использовать 'me' в качестве имени пользователя
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено!'
            )
        return value

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        user = User.objects.filter(username=username).first()

        # Проверка существующего пользователя
        if user:
            if user.email != email:
                raise serializers.ValidationError({
                    'email': 'Email не совпадает с существующим пользователем.'
                })
        else:
            # Проверка уникальности email для нового пользователя
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({
                    'email': 'Этот email используется другим пользователем.'
                })
            # Создаем нового пользователя
            user = User.objects.create(username=username, email=email)

        # Генерация и сохранение кода подтверждения
        user.confirmation_code = default_token_generator.make_token(user)
        user.save()
        return user


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с профилями пользователей."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'role', 'bio'
        )

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and not request.user.is_admin:
            fields["role"].read_only = True
        return fields


class GetTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
