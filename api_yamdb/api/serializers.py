from rest_framework import serializers
from datetime import datetime
from reviews.models import User, Category, Genre, Title, Review, Comment
from django.core.validators import MaxValueValidator, MinValueValidator
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


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для работы с категориями произведений."""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с жанрами произведений."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных о произведениях."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи данных о произведениях."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')

    def validate_year(self, value):
        if value > datetime.now().year:
            raise serializers.ValidationError(
                "Год выпуска не может быть больше текущего"
            )
        return value

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        title.genre.set(genres)
        return title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с отзывами на произведения."""

    score = serializers.IntegerField(
        validators=[
            MinValueValidator(1, message="Оценка не может быть меньше 1"),
            MaxValueValidator(10, message="Оценка не может быть больше 10")
        ]
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError(
                "Оценка должна быть в диапазоне от 1 до 10"
            )
        return value

    def validate(self, data):
        # Проверка аутентификации пользователя
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Требуется авторизация")

        # Проверка уникальности отзыва только при POST-запросе
        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            author = request.user
            if Review.objects.filter(
                title_id=title_id, author=author
            ).exists():
                raise serializers.ValidationError(
                    {'detail': 'Вы уже оставляли отзыв на это произведение'}
                )

        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с комментариями к отзывам."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
