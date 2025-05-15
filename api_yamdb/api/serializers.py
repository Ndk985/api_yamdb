from rest_framework import serializers
from reviews.models import Review, Comment


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Оценка должна быть от 1 до 10")
        return value

    def validate(self, data):
        # Проверка на уникальность отзыва пользователя
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs['title_id']
            user = self.context['request'].user
            if Review.objects.filter(title_id=title_id, author=user).exists():
                raise serializers.ValidationError('Вы уже оставляли отзыв')
        return data

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')