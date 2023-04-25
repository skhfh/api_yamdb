from django.urls import include, path

from rest_framework import routers

from .views import CategoryViewSet, GenreViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')

urlpatterns = [
    path('v1/', include(router.urls)),
]
