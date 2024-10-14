from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import  TokenObtainPairView,TokenRefreshView

from rest_framework.routers import DefaultRouter

from main_app.views import (
    MenuItemViewSet,
    CartViewSet,
    OrderViewSet,
    PaymentViewSet,
    user_profile,
    RegisterView,
    RestaurantViewSet,
    UserViewSet
)

# Define a router and register our viewsets
router = DefaultRouter()
# Admin endpoints
router.register(r'admin/restaurants', RestaurantViewSet, basename='admin-restaurants')    
router.register(r'admin/users', UserViewSet, basename='admin-users')
# Staff endpoints
router.register(r'staff/orders', OrderViewSet, basename='staff-orders')
# User endpoints
router.register(r'users/menu', MenuItemViewSet, basename='users-menu')
# router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'menu-items', MenuItemViewSet, basename='menu-items')
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/user-profile/', user_profile, name='user-profile'),
    path('profile/', user_profile, name='user-profile'),
    path('', include(router.urls)),
]