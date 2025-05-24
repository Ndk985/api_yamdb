from django_filters import rest_framework as django_filters
from rest_framework import mixins, viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.parsers import (
    JSONParser, FormParser, MultiPartParser
)
from reviews.models import Title, Category, Genre
from api.core.permissions import AdminOnly
from rest_framework.permissions import AllowAny
from .serializers import (
    TitleReadSerializer, TitleWriteSerializer,
    CategorySerializer, GenreSerializer,
)
from .filters import TitleFilter


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления произведениями."""

    queryset = Title.objects.all()
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter
    ]
    filterset_class = TitleFilter
    search_fields = ['name', 'year', 'category__slug', 'genre__slug']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [AdminOnly()]
        return [permissions.AllowAny()]


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    """ViewSet для управления категориями произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [AdminOnly()]
        return [permissions.AllowAny()]


class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """ViewSet для управления жанрами произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'partial_update', 'update']:
            return [AdminOnly()]
        return [AllowAny()]

    def update(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
