from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from a_products.models import Product, Category
from a_cart.models import Cart
from .models import Order

class OrderCheckoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', price=10.00, category=self.category)
        self.cart = Cart.objects.create(user=self.user)
        self.cart.add_product(self.product, quantity=2)

    def test_order_creation_from_cart(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        
        order = Order.objects.get(user=self.user, status='PENDING')
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product, self.product)
        self.assertEqual(order.items.first().quantity, 2)
        self.assertEqual(order.total_price, Decimal('20.00'))
        self.assertIsNotNone(order.order_number)

    def test_order_status_change(self):
        order = Order.objects.create(user=self.user, status='PENDING', total_price=Decimal('20.00'))
        order.status = 'PROCESSING'
        order.save()
        self.assertEqual(Order.objects.get(id=order.id).status, 'PROCESSING')

    # def test_checkout_process(self):
    #     self.client.login(username='testuser', password='12345')
    #     response = self.client.get(reverse('orders:checkout'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'orders/checkout.html')

    #     # Test form submission (you'll need to adjust this based on your actual form fields)
    #     checkout_data = {
    #         'shipping_address': '123 Test St',
    #         'shipping_city': 'Test City',
    #         'shipping_country': 'Test Country',
    #         'shipping_zip': '12345',
    #     }
    #     response = self.client.post(reverse('orders:checkout'), checkout_data)
    #     self.assertEqual(response.status_code, 302)  # Assuming a redirect after successful checkout

    def test_order_number_generation(self):
        order1 = Order.objects.create(user=self.user, status='PENDING', total_price=Decimal('20.00'))
        order2 = Order.objects.create(user=self.user, status='PENDING', total_price=Decimal('30.00'))
        self.assertNotEqual(order1.order_number, order2.order_number)
        self.assertEqual(len(order1.order_number), 6)
        self.assertEqual(len(order2.order_number), 6)

    def test_order_items_creation(self):
        order = Order.objects.create(user=self.user, status='PENDING', total_price=Decimal('0.00'))
        order.sync_with_cart(self.cart)
        self.assertEqual(order.items.count(), 1)
        order_item = order.items.first()
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, self.product.price)

    def test_anonymous_user_checkout(self):
        # go to the homepage first to create a cart
        self.client.get(reverse('products:home'))
        # go to the checkout page
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(Order.objects.first().user)
        self.assertIsNotNone(self.client.session.get('order_id'))

    def test_authenticated_user_checkout(self):
        # go to the homepage first to create a cart
        self.client.get(reverse('products:home'))
        # go to the checkout page
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.first().user, self.user)

    def test_order_total_price_calculation(self):
        order = Order.objects.create(user=self.user, status='PENDING', total_price=Decimal('0.00'))
        order.sync_with_cart(self.cart)
        self.assertEqual(order.total_price, Decimal('20.00'))

    def test_order_syncing_with_cart(self):
        order = Order.objects.create(user=self.user, status='PENDING', total_price=Decimal('0.00'))
        order.sync_with_cart(self.cart)
        self.cart.add_product(self.product, quantity=1)
        order.sync_with_cart(self.cart)
        self.assertEqual(order.items.first().quantity, 3)
        self.assertEqual(order.total_price, Decimal('30.00'))

    # def test_payment_method_selection(self):
    #     self.client.login(username='testuser', password='12345')
    #     checkout_data = {
    #         'shipping_address': '123 Test St',
    #         'shipping_city': 'Test City',
    #         'shipping_country': 'Test Country',
    #         'shipping_zip': '12345',
    #         'payment_method': 'CREDIT_CARD'
    #     }
    #     response = self.client.post(reverse('orders:checkout'), checkout_data)
    #     self.assertEqual(response.status_code, 302)
    #     order = Order.objects.get(user=self.user)
    #     self.assertEqual(order.payment_method, 'CREDIT_CARD')