# @Time    : 2024/8/24 17:39
# @Author  :      

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServerViewSet

router = DefaultRouter()
router.register(r'servers', ServerViewSet, basename='server')

urlpatterns = [
    path('', include(router.urls)),
]