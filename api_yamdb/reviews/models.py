from django.db import models
from django.db.models import Avg


class Title(models.Model):
    rating = models.IntegerField(null=True, blank=True)  # Поле для рейтинга

    def update_rating(self):
        """Обновление рейтинга при изменении отзывов"""
        avg_score = self.reviews.aggregate(Avg('score'))['score__avg']
        self.rating = int(avg_score) if avg_score else None
        self.save()


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)
