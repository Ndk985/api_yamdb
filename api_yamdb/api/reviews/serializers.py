from rest_framework import serializers
from reviews.models import Review, Comment
from django.core.validators import MaxValueValidator, MinValueValidator


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
