# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# Restaurant model (replacing Tenant)
class Tenant(models.Model):
    """
    Represents a restaurant tenant, including basic information such as name, address, contact info, and a unique identifier.
    """
    restaurant_id = models.AutoField(primary_key=True)
    name = models.TextField()
    address = models.TextField()
    contact_info = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tenant_identifier = models.TextField()

    def __str__(self):
        return str(self.name)

# User model
class User(AbstractUser):
    """
    Custom user model extending the default AbstractUser. Users are linked to a restaurant.
    """
    user_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    name = models.TextField()
    email = models.EmailField(unique=True)
    role = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return str(self.email)

# Social Account model
class SocialAccount(models.Model):
    """
    Represents a social account linked to a user, including the provider and user ID.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.TextField()
    uid = models.TextField(unique=True)
    extra_data = models.JSONField(null=True, blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'provider')

# Table model
class Table(models.Model):
    """
    Represents a table in a restaurant, including table number and seating capacity.
    """
    table_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    table_number = models.TextField()
    seating_capacity = models.IntegerField()
    link = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('restaurant', 'table_number')

# Category model
class Category(models.Model):
    """
    Represents a menu category in a restaurant, such as appetizers or drinks.
    """
    category_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

# Menu Item model
class MenuItem(models.Model):
    """
    Represents an item on the restaurant's menu, including price and availability.
    """
    item_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name='chk_price_non_negative')
        ]
        indexes = [
            models.Index(fields=['restaurant', 'category'], name='restaurant_category_index'),
        ]

# Order model
class Order(models.Model):
    """
    Represents an order placed by a user, linked to a specific restaurant and table.
    """
    order_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Order Item model
class OrderItem(models.Model):
    """
    Represents an individual item within an order, including quantity and price.
    """
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

# Inventory model
class Inventory(models.Model):
    """
    Represents the inventory of a menu item in a restaurant, including quantity in stock.
    """
    inventory_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity_in_stock = models.IntegerField()
    reorder_level = models.IntegerField()
    last_restocked_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Payment model
class Payment(models.Model):
    """
    Represents a payment for an order, including payment method and status.
    """
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    payment_method = models.TextField()
    payment_status = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Transaction model
class Transaction(models.Model):
    """
    Represents a financial transaction related to an order, including type and amount.
    """
    transaction_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    transaction_type = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gte=0), name='chk_amount_non_negative')
        ]

# Temporary Session model
class TemporarySession(models.Model):
    """
    Represents a temporary session for a guest user, storing cart data and expiration.
    """
    guest_session_id = models.AutoField(primary_key=True)
    session_token = models.TextField(unique=True)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    cart_data = models.JSONField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

# Customization model
class Customization(models.Model):
    """
    Represents restaurant-specific customizations, such as logo and theme settings.
    """
    customization_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    logo_image = models.ImageField(upload_to='logos/', null=True, blank=True)
    theme_color = models.TextField(null=True, blank=True)
    background_image = models.ImageField(upload_to='backgrounds/', null=True, blank=True)
    font_style = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Image model
class Image(models.Model):
    """
    Represents images uploaded by a restaurant, including the type of image.
    """
    image_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='images/')
    image_type = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Cart model
class Cart(models.Model):
    """
    Represents a shopping cart for a user, including items and total price.
    """
    cart_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    items = models.ManyToManyField(MenuItem)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Receipt model
class Receipt(models.Model):
    """
    Represents a receipt for an order, including payment details and receipt data.
    """
    receipt_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.TextField()
    receipt_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)