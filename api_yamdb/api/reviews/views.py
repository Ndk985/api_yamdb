from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import (IsAuthenticatedOrReadOnly)
from reviews.models import Title, Review
from api.core.permissions import IsAuthorOrModeratorOrAdmin
from .serializers import (
    ReviewSerializer, CommentSerializer
)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для управления отзывами на произведения."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin
    ]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(
            author=self.request.user,
            title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления комментариями к отзывам."""
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthorOrModeratorOrAdmin,
        IsAuthenticatedOrReadOnly
    ]

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs["review_id"])

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
