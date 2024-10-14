# views.py
from rest_framework import generics, viewsets, status 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes

from main_app.models import MenuItem, Cart, Order, OrderItem, Payment, User, Tenant
from main_app.serializers import (
    MenuItemSerializer,
    CartSerializer,
    OrderSerializer,
    PaymentSerializer,
    UserProfileSerializer,
    UserSerializer,
    RestaurantSerializer
)
from main_app.permissions import IsAdminUserCustom

# Menu Browsing
class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.filter(availability=True)
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

# Cart Management
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        cart= Cart.objects.get_or_create(user=request.user, restaurant=request.user.restaurant)
        serializer = self.get_serializer(cart, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.clear()
            cart.total_price = 0
            cart.save()
            return Response({'status': 'cart cleared'}, status=status.HTTP_200_OK)
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

# Order Placement and History
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            restaurant=cart.restaurant,
            table=None,  # Adjust as necessary
            user=request.user,
            total_price=cart.total_price,
            status='pending',
        )
        for item in cart.items.all():
            quantity = 1  # Adjust as necessary if you have quantity in cart
            price = item.price * quantity
            OrderItem.objects.create(
                order=order,
                item=item,
                quantity=quantity,
                price=price
            )
        # Clear the cart after creating the order
        cart.items.clear()
        cart.total_price = 0
        cart.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Payment Processing
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(restaurant=request.user.restaurant)
        # Here you would integrate with a payment gateway
        # For simplicity, we'll assume payment is successful
        payment.payment_status = 'completed'
        payment.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# User Profile
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        serializer = UserProfileSerializer(request.user, data=request.data, partial=(request.method == 'PATCH'))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# Register User
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Restaurant Management
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

# User Management
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom] 
