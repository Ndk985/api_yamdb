from rest_framework import mixins, viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.parsers import (
    JSONParser, FormParser, MultiPartParser, BaseParser
)
from reviews.models import Title, Category, Genre
from api.core.permissions import AdminOnly
from .serializers import (
    TitleReadSerializer, TitleWriteSerializer,
    CategorySerializer, GenreSerializer,
)


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления произведениями."""

    queryset = Title.objects.all()
    filter_backends = [filters.SearchFilter]
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

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category')
        genre_slug = self.request.query_params.get('genre')
        year = self.request.query_params.get('year')
        name = self.request.query_params.get('name')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(year=year)
            except ValueError:
                pass
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class PlainTextParser(BaseParser):
    media_type = '*/*'

    def parse(self, stream, media_type=None, parser_context=None):
        return {}


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
    parser_classes = [JSONParser, FormParser, MultiPartParser, PlainTextParser]
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [AdminOnly()]
        return [permissions.AllowAny()]


class GenreViewSet(viewsets.ModelViewSet):
    """ViewSet для управления жанрами произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [AdminOnly()]
        return [permissions.AllowAny()]

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
