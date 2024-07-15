from django.test import TestCase, RequestFactory
from django.urls import reverse
from .models import Product, Category
from .views import view_list

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
        self.factory = RequestFactory()
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name="Test Product", category=self.category, price=15.00)

    def test_view_list(self):
        request = self.factory.get(reverse('products:home'))
        request.htmx = False
        response = view_list(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_view_list_with_category_filter(self):
        request = self.factory.get(reverse('products:home'), {'category': self.category.slug})
        request.htmx = False
        response = view_list(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)


    def test_view_list_htmx(self):
        request = self.factory.get(reverse('products:home'))
        request.htmx = True
        response = view_list(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertNotContains(response, '<header class="max-w-7xl mx-auto">')  # Check that header is not included
        
        # Check for content specific to the HTMX template
        self.assertContains(response, '<div id="product-list"')
        self.assertNotContains(response, '<html')  # The HTMX response should not include a full HTML document

    def test_view_list_htmx_empty_response(self):
        Category.objects.all().delete()  # Clear all categories
        Product.objects.all().delete()  # Clear all products
        
        request = self.factory.get(reverse('products:home'))
        request.htmx = True
        response = view_list(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products available.")
        self.assertNotContains(response, '<header class="max-w-7xl mx-auto">')