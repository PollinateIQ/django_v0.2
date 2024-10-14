import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DineUp.settings')
django.setup()



from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from main_app.models import (
    MenuItem, Cart, Order, OrderItem, Payment, User, Category, Table, Tenant,
)   

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['item_id', 'restaurant', 'category', 'name', 'description', 'price', 'availability']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'restaurant', 'name', 'description']

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['table_id', 'restaurant', 'table_number', 'seating_capacity', 'link']

class CartSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)
    item_ids = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), many=True, write_only=True, source='items')

    class Meta: 
        model = Cart
        fields = ['cart_id', 'user', 'restaurant', 'items', 'item_ids', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['cart_id', 'user', 'restaurant', 'total_price', 'created_at', 'updated_at']

    def create(self, validated_data):
        items = validated_data.pop('items', [])
        cart = Cart.objects.create(**validated_data)
        cart.items.set(items)
        cart.save()
        return cart

    def update(self, instance, validated_data):
        items = validated_data.pop('items', None)
        if items is not None:
            instance.items.set(items)
        instance.save()
        return instance

class OrderItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['order_item_id', 'order', 'item', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'restaurant', 'table', 'user', 'total_price', 'status', 'created_at', 'updated_at', 'order_items']
        read_only_fields = ['order_id', 'restaurant', 'user', 'total_price', 'status', 'created_at', 'updated_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_id', 'order', 'restaurant', 'payment_method', 'payment_status', 'amount', 'transaction_id', 'created_at', 'updated_at']
        read_only_fields = ['payment_id', 'restaurant', 'payment_status', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['user_id', 'name', 'email', 'password', 'password2', 'role', 'created_at']
        read_only_fields = ['user_id', 'role', 'created_at']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['email'],  # Assuming username is email
            email=validated_data['email'],
            name=validated_data['name'],
            role='User',  # Default role
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'name', 'email', 'role', 'created_at']
        read_only_fields = ['user_id', 'email', 'role', 'created_at']

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['restaurant_id', 'name', 'address', 'contact_info', 'created_at', 'tenant_identifier']
