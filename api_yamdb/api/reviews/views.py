from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import (IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from reviews.models import Title, Review, Comment
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

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {"detail": "Метод PUT не разрешен"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления комментариями к отзывам."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthorOrModeratorOrAdmin,
        IsAuthenticatedOrReadOnly
    ]

    def get_queryset(self):
        review_id = self.kwargs['review_id']
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)
