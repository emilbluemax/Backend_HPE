from django.contrib import admin
from django.urls import path

from .views import ProductViewSet, UserAPIView, TestAPIView

urlpatterns = [
    path('products', ProductViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('products/<str:pk>', ProductViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    path('user', UserAPIView.as_view()),
    path('user/<str:pk>', UserAPIView.as_view()),

    path('test', TestAPIView.as_view())
]