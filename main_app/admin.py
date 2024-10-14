from django.contrib import admin
from main_app.models import (
    Tenant, User, SocialAccount, Table, Category, MenuItem, Order, OrderItem,
    Inventory, Payment, Transaction, TemporarySession, Customization, Image,
    Cart, Receipt
)

admin.site.register(Tenant)
admin.site.register(User)
admin.site.register(SocialAccount)
admin.site.register(Table)
admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Inventory)
admin.site.register(Payment)
admin.site.register(Transaction)
admin.site.register(TemporarySession)
admin.site.register(Customization)
admin.site.register(Image)
admin.site.register(Cart)
admin.site.register(Receipt)
