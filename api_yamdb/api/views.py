from rest_framework import viewsets, permissions, filters
from reviews.models import Title, Category, Genre
from .serializers import (
    TitleReadSerializer,
    TitleWriteSerializer,
    CategorySerializer,
    GenreSerializer
)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'year', 'category__slug', 'genre__slug']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация по параметрам запроса
        category_slug = self.request.query_params.get('category__slug')
        genre_slug = self.request.query_params.get('genre__slug')
        year = self.request.query_params.get('year')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(year=year)
            except ValueError:
                pass  # Игнорируем невалидный год

        return queryset


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
