from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile
from a_cart.models import Cart
from a_products.models import Product, Category

class UserProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            price=10.00,
            category=self.category
        )

    def test_profile_creation(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.email, 'test@example.com')

    def test_profile_email_update(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        user.profile.email = 'newemail@example.com'
        user.profile.save()
        user.refresh_from_db()
        self.assertEqual(user.email, 'newemail@example.com')

    def test_profile_deletion(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        user_id = user.id
        user.delete()
        self.assertFalse(Profile.objects.filter(user_id=user_id).exists())

    def test_anonymous_user_cart(self):
        response = self.client.post(reverse('cart:add_to_cart'), {'product_id': self.product.id, 'quantity': 1})
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        cart = Cart.objects.get(session_key=session.session_key)
        self.assertEqual(cart.items.count(), 1)

    def test_retain_cart_on_login(self):
        # Add item to cart as anonymous user
        self.client.post(reverse('cart:add_to_cart'), {'product_id': self.product.id, 'quantity': 1})
        session_key = self.client.session.session_key

        # Create user and log in
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

        # Check if cart is retained
        cart = Cart.objects.get(user=user)
        self.assertEqual(cart.items.count(), 1)
        self.assertIsNone(cart.session_key)

        # Ensure old session cart is deleted
        self.assertFalse(Cart.objects.filter(session_key=session_key).exists())

    def test_clear_cart_on_logout(self):
        # Create user, log in, and add item to cart
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('cart:add_to_cart'), {'product_id': self.product.id, 'quantity': 1})

        # Logout
        self.client.logout()

        # Check if cart is cleared
        self.assertFalse(Cart.objects.filter(user=user).exists())