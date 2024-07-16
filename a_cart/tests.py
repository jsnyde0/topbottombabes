from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from a_products.models import Product, Category
from .models import Cart, CartItem

class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', price=10.00, category=self.category)
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        self.assertTrue(isinstance(self.cart, Cart))
        self.assertEqual(self.cart.__str__(), "testuser's cart")

    def test_add_product(self):
        self.cart.add_product(self.product, quantity=2)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart.items.first().quantity, 2)

    def test_remove_product(self):
        self.cart.add_product(self.product)
        self.cart.remove_product(self.product.id)
        self.assertEqual(self.cart.items.count(), 0)

    def test_update_quantity(self):
        self.cart.add_product(self.product)
        self.cart.update_quantity(self.product.id, 3)
        self.assertEqual(self.cart.items.first().quantity, 3)

    def test_get_total_price(self):
        self.cart.add_product(self.product, quantity=2)
        self.assertEqual(self.cart.get_total_price(), 20.00)

    def test_get_num_items(self):
        self.cart.add_product(self.product, quantity=2)
        self.assertEqual(self.cart.get_num_items(), 2)

class CartViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', price=10.00, category=self.category)
        self.client.login(username='testuser', password='12345')

    def test_view_cart(self):
        response = self.client.get(reverse('cart:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart.html')

    def test_add_to_cart(self):
        response = self.client.post(reverse('cart:add_to_cart'), {'product_id': self.product.id, 'quantity': 1})
        self.assertEqual(response.status_code, 200)
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)

    def test_remove_from_cart(self):
        cart = Cart.objects.create(user=self.user)
        cart.add_product(self.product)
        response = self.client.post(reverse('cart:remove_from_cart'), {'product_id': self.product.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cart.items.count(), 0)

    def test_update_quantity(self):
        cart = Cart.objects.create(user=self.user)
        cart.add_product(self.product)
        response = self.client.post(reverse('cart:update_quantity'), {'product_id': self.product.id, 'quantity': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cart.items.first().quantity, 3)

    def test_add_to_cart_htmx(self):
        response = self.client.post(reverse('cart:add_to_cart'), {'product_id': self.product.id, 'quantity': 1}, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart_content.html')

    def test_remove_from_cart_htmx(self):
        cart = Cart.objects.create(user=self.user)
        cart.add_product(self.product)
        response = self.client.post(reverse('cart:remove_from_cart'), {'product_id': self.product.id}, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart_content.html')

    def test_update_quantity_htmx(self):
        cart = Cart.objects.create(user=self.user)
        cart.add_product(self.product)
        response = self.client.post(reverse('cart:update_quantity'), {'product_id': self.product.id, 'quantity': 3}, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart_content.html')