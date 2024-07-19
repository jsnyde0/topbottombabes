from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile
from a_cart.models import Cart
from a_products.models import Product, Category
import logging

logger = logging.getLogger(__name__)

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
        session_cart_id = session['cart_id']
        cart = Cart.objects.get(id=session_cart_id)
        self.assertEqual(cart.items.count(), 1)
        self.assertIsNone(cart.user)

    def test_retain_cart_on_login(self):
        # Add item to cart as anonymous user
        response = self.client.post(reverse('cart:add_to_cart'), {'product_id': self.product.id, 'quantity': 1})
        self.assertEqual(response.status_code, 200)
        # check the id of the pre-login cart
        cart_id_pre_login = self.client.session['cart_id']
        logger.debug(f"Pre-login cart ID: {cart_id_pre_login}")

        # check that the pre-login cart has 1 item
        cart_pre_login = Cart.objects.get(id=cart_id_pre_login)
        self.assertEqual(cart_pre_login.items.count(), 1)
        logger.debug(f"Pre-login cart items count: {cart_pre_login.items.count()}")
        logger.debug(f"Pre-login cart user: {cart_pre_login.user}")

        # Create user
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        logger.debug(f"Created user: {user.username}")

        # Simulate login process
        login_successful = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_successful)
        logger.debug(f"Login successful: {login_successful}")

        # Force session save and refresh
        self.client.session.save()
        logger.debug(f"Session after login: {dict(self.client.session)}")

        # Make a request to trigger any pending signals and ensure the cart is processed
        response = self.client.get(reverse('products:home'))
        self.assertEqual(response.status_code, 200)
        logger.debug(f"Made request to home page. Status: {response.status_code}")

        # Refresh the user instance
        user.refresh_from_db()
        logger.debug(f"Refreshed user: {user.username}")

        # Check if cart is retained
        try:
            user_cart = Cart.objects.get(user=user)
            n_cart_items = user_cart.items.count()
            logger.debug(f"User cart found. ID: {user_cart.id}")
            logger.debug(f"User cart items count: {n_cart_items}")
        except Cart.DoesNotExist:
            logger.error("User cart not found!")
            user_cart = None

        self.assertEqual(n_cart_items, 1)

        # Check if old cart still exists
        try:
            old_cart = Cart.objects.get(id=cart_id_pre_login)
            logger.warning(f"Old cart still exists. ID: {old_cart.id}")
        except Cart.DoesNotExist:
            logger.debug("Old cart successfully deleted")

        # Ensure old session cart is deleted (trying to get the pre-login cart should raise a Cart.DoesNotExist error)
        with self.assertRaises(Cart.DoesNotExist):
            Cart.objects.get(id=cart_id_pre_login)

        # Double-check the cart in the session
        self.assertEqual(self.client.session['cart_id'], user_cart.id)

    def test_clear_cart_on_logout(self):
        # Create user, log in, and add item to cart
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('cart:add_to_cart'), {'product_id': self.product.id, 'quantity': 1})

        # Logout and redirect to homepage
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        # Check if a new cart is created after logout that's empty
        cart_id = self.client.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        self.assertIsNotNone(cart)
        self.assertEqual(cart.items.count(), 0)