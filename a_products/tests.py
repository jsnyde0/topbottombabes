from django.test import TestCase, Client
from django.urls import reverse
from .models import Product, Category
from a_cart.models import Cart

class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            price=9.99,
            category=self.category,
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, 9.99)
        self.assertEqual(self.product.category, self.category)

    def test_product_str_method(self):
        self.assertEqual(str(self.product), "Test Product")

class ProductQuerySetTests(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")
        self.category3 = Category.objects.create(name="Category 3")
        self.product1 = Product.objects.create(name="Product 1", category=self.category1, price=10.00)
        self.product2 = Product.objects.create(name="Product 2", category=self.category2, price=20.00)
        self.product3 = Product.objects.create(name="Product 3", category=self.category3, price=30.00)

    def test_filter_by_params_category(self):
        filtered_products = Product.objects.filter_by_params(category=self.category1.slug)
        self.assertIn(self.product1, filtered_products)
        self.assertNotIn(self.product2, filtered_products)
        self.assertNotIn(self.product3, filtered_products)

    def test_filter_by_params_multiple_categories(self):
        filtered_products = Product.objects.filter_by_params(category=[self.category1.slug, self.category2.slug])
        self.assertIn(self.product1, filtered_products)
        self.assertIn(self.product2, filtered_products)
        self.assertNotIn(self.product3, filtered_products)

class ProductViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name="Test Product", category=self.category, price=15.00)

    def test_view_list(self):
        response = self.client.get(reverse('products:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_view_list_with_category_filter(self):
        response = self.client.get(reverse('products:home'), {'category': self.category.slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_view_list_htmx(self):
        response = self.client.get(reverse('products:home'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertNotContains(response, '<header class="max-w-7xl mx-auto">')
        self.assertContains(response, '<div id="product-list"')
        self.assertNotContains(response, '<html')

    def test_view_list_htmx_empty_response(self):
        Category.objects.all().delete()
        Product.objects.all().delete()
        
        response = self.client.get(reverse('products:home'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products available.")
        self.assertNotContains(response, '<header class="max-w-7xl mx-auto">')

    def test_cart_creation_for_anonymous_user(self):
        response = self.client.get(reverse('products:home'))
        self.assertEqual(response.status_code, 200)
        
        # Check if a cart was created for the session TODO: This will fail because we removed session_key field from Cart!
        session_key = self.client.session.session_key
        self.assertTrue(Cart.objects.filter(session_key=session_key).exists())