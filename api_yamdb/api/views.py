from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import (
    JSONParser, FormParser, MultiPartParser, BaseParser
)
from reviews.models import User, Title, Category, Genre, Review, Comment
from .permissions import AdminOnly, IsAuthorOrModeratorOrAdmin
from .serializers import (
    GetTokenSerializer, SignUpSerializer, UsersSerializer,
    TitleReadSerializer, TitleWriteSerializer,
    CategorySerializer, GenreSerializer,
    ReviewSerializer, CommentSerializer
)


class UsersViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticated, AdminOnly,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def get_current_user_info(self, request):
        user = get_object_or_404(User, id=request.user.id)
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UsersSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class APISignup(APIView):
    """    API эндпоинт для регистрации новых пользователей."""

    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']]
        )
        email.send()

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        email_body = (
            f'Доброе время суток, {user.username}.'
            f'\nКод подтвержения для доступа к API: {user.confirmation_code}'
        )
        data = {
            'email_body': email_body,
            'to_email': user.email,
            'email_subject': 'Код подтвержения для доступа к API!'
        }
        self.send_email(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIGetToken(APIView):
    """Эндпоинт для получения токена."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return Response(
                {'username': 'Пользователь не найден!'},
                status=status.HTTP_404_NOT_FOUND)
        if data.get('confirmation_code') == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST)


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
