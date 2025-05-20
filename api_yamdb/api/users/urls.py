from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UsersViewSet, APISignup, APIGetToken

router = DefaultRouter()
router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('auth/signup/', APISignup.as_view(), name='signup'),
    path('auth/token/', APIGetToken.as_view(), name='get_token'),
] + router.urls
