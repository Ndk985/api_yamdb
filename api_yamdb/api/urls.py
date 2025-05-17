from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    APIGetToken, APISignup, UsersViewSet,
    TitleViewSet, CategoryViewSet, GenreViewSet,
    ReviewViewSet, CommentViewSet
)

router = DefaultRouter()
router.register('users', UsersViewSet, basename='users')
router.register('titles', TitleViewSet, basename='titles')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', APISignup.as_view(), name='signup'),
    path('auth/token/', APIGetToken.as_view(), name='get_token'),
]
