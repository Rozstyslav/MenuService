from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, MenuViewSet, EmployeeViewSet

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'menu', MenuViewSet, basename='menu')
router.register(r'employee', EmployeeViewSet, basename='employee')


urlpatterns = [
    path('', include(router.urls)),
]
