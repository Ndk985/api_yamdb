from django.urls import include, path
from rest_framework.routers import DefaultRouter

from reviews.views import APIGetToken, APISignup, UsersViewSet


router = DefaultRouter()

router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', APISignup.as_view(), name='signup'),
    path('v1/auth/token/', APIGetToken.as_view(), name='get_token'),
]
