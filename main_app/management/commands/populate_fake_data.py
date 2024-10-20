import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from main_app.models import (
    Tenant, User, SocialAccount, Table, Category, MenuItem, Order, OrderItem,
    Inventory, Payment, Transaction, TemporarySession, Customization, Image, Cart, Receipt
)
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate the database with fake data for testing'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # Create Tenants (Restaurants)
        self.stdout.write('Creating Tenants...')
        tenants = []
        for _ in range(5):
            tenant = Tenant.objects.create(
                name=fake.company(),
                address=fake.address(),
                contact_info=fake.phone_number(),
                tenant_identifier=fake.uuid4()
            )
            tenants.append(tenant)

        # Create Users
        self.stdout.write('Creating Users...')
        users = []
        for _ in range(20):
            user = User.objects.create(
                restaurant=random.choice(tenants),
                name=fake.name(),
                email=fake.email(),
                role=random.choice(['admin', 'staff', 'customer']),
                username=fake.user_name()
            )
            user.set_password(fake.password())
            user.save()
            users.append(user)

        # Create SocialAccounts
        self.stdout.write('Creating SocialAccounts...')
        for _ in range(10):
            user = random.choice(users)
            provider = random.choice(['google', 'facebook', 'twitter'])
            if not SocialAccount.objects.filter(user=user, provider=provider).exists():
                SocialAccount.objects.create(
                    user=user,
                    provider=provider,
                    uid=fake.uuid4(),
                    extra_data={}
                )

        # Create Tables
        self.stdout.write('Creating Tables...')
        tables = []
        for tenant in tenants:
            for i in range(10):
                table = Table.objects.create(
                    restaurant=tenant,
                    table_number=str(i + 1),
                    seating_capacity=random.randint(2, 8),
                    link=fake.url()
                )
                tables.append(table)

        # Create Categories
        self.stdout.write('Creating Categories...')
        categories = []
        for tenant in tenants:
            for _ in range(5):
                category = Category.objects.create(
                    restaurant=tenant,
                    name=fake.word(),
                    description=fake.sentence()
                )
                categories.append(category)

        # Create MenuItems
        self.stdout.write('Creating MenuItems...')
        menu_items = []
        for category in categories:
            for _ in range(10):
                menu_item = MenuItem.objects.create(
                    restaurant=category.restaurant,
                    category=category,
                    name=fake.word(),  # Changed from fake.food() to fake.word()
                    description=fake.sentence(),
                    price=round(random.uniform(5, 50), 2),
                    availability=random.choice([True, False])
                )
                menu_items.append(menu_item)

        # Create Orders
        self.stdout.write('Creating Orders...')
        orders = []
        for _ in range(50):
            tenant = random.choice(tenants)
            order = Order.objects.create(
                restaurant=tenant,
                table=random.choice(Table.objects.filter(restaurant=tenant)),
                user=random.choice(users),
                total_price=0,
                status=random.choice(['pending', 'processing', 'completed', 'cancelled'])
            )
            orders.append(order)

        # Create OrderItems
        self.stdout.write('Creating OrderItems...')
        for order in orders:
            total_price = 0
            for _ in range(random.randint(1, 5)):
                menu_item = random.choice(MenuItem.objects.filter(restaurant=order.restaurant))
                quantity = random.randint(1, 3)
                price = menu_item.price * quantity
                OrderItem.objects.create(
                    order=order,
                    item=menu_item,
                    quantity=quantity,
                    price=price
                )
                total_price += price
            order.total_price = total_price
            order.save()

        # Create Inventory
        self.stdout.write('Creating Inventory...')
        for menu_item in menu_items:
            Inventory.objects.create(
                restaurant=menu_item.restaurant,
                item=menu_item,
                quantity_in_stock=random.randint(0, 100),
                reorder_level=random.randint(10, 30),
                last_restocked_at=fake.date_time_this_year()
            )

        # Create Payments
        self.stdout.write('Creating Payments...')
        for order in orders:
            Payment.objects.create(
                order=order,
                restaurant=order.restaurant,
                payment_method=random.choice(['cash', 'credit_card', 'debit_card', 'mobile_payment']),
                payment_status=random.choice(['pending', 'completed', 'failed']),
                amount=order.total_price,
                transaction_id=fake.uuid4()
            )

        # Create Transactions
        self.stdout.write('Creating Transactions...')
        for payment in Payment.objects.all():
            Transaction.objects.create(
                order=payment.order,
                payment=payment,
                restaurant=payment.restaurant,
                transaction_type=random.choice(['payment', 'refund']),
                amount=payment.amount,
                status=random.choice(['pending', 'completed', 'failed'])
            )

        # Create TemporarySessions
        self.stdout.write('Creating TemporarySessions...')
        for _ in range(20):
            TemporarySession.objects.create(
                session_token=fake.uuid4(),
                restaurant=random.choice(tenants),
                cart_data={},
                expires_at=timezone.now() + timedelta(hours=random.randint(1, 24))
            )

        # Create Customizations
        self.stdout.write('Creating Customizations...')
        for tenant in tenants:
            Customization.objects.create(
                restaurant=tenant,
                theme_color=fake.hex_color(),
                font_style=random.choice(['serif', 'sans-serif', 'monospace'])
            )

        # Create Images
        self.stdout.write('Creating Images...')
        for tenant in tenants:
            for _ in range(5):
                Image.objects.create(
                    restaurant=tenant,
                    image_file='path/to/fake/image.jpg',
                    image_type=random.choice(['menu', 'logo', 'background'])
                )

        
        # Create Receipts
        self.stdout.write('Creating Receipts...')
        for order in orders:
            Receipt.objects.create(
                order=order,
                restaurant=order.restaurant,
                user=order.user,
                total_amount=order.total_price,
                payment_method=random.choice(['cash', 'credit_card', 'debit_card', 'mobile_payment']),
                receipt_data={}
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with fake data'))
