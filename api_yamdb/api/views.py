from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from django.shortcuts import get_object_or_404
from .serializers import ReviewSerializer, CommentSerializer
from reviews.models import Title, Review, Comment


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        review_id = self.kwargs['review_id']
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)
