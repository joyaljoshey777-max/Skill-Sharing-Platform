from django.test import TestCase, Client
from django.urls import reverse
from core.models import User, ProviderProfile, Skill, Booking

class FlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Provider
        self.provider_user = User.objects.create_user(username='provider1', password='password123', is_provider=True)
        self.provider_profile = ProviderProfile.objects.create(user=self.provider_user, experience=5, price_per_service=50.0, contact_details='test@test.com', id_proof='test.pdf')
        self.provider_profile.status = 'Approved'
        self.provider_profile.save()
        self.skill = Skill.objects.create(provider=self.provider_profile, name='Plumbing')
        
        # Create Customer
        self.customer_user = User.objects.create_user(username='customer1', password='password123', is_customer=True)

    def test_pages_load_successfully(self):
        urls_to_test = [
            '/',
            '/skills/',
            '/register/customer/',
            '/register/provider/',
            '/login/',
        ]
        for url in urls_to_test:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"URL {url} failed to load.")
            
    def test_provider_profile_load(self):
        response = self.client.get(reverse('provider_profile', args=[self.provider_profile.id]))
        self.assertEqual(response.status_code, 200)

    def test_customer_login_redirect(self):
        response = self.client.post('/login/', {'username': 'customer1', 'password': 'password123'})
        self.assertEqual(response.status_code, 302, f"Failed Customer Login Redirect, got {response.status_code}")
        
    def test_provider_login_redirect(self):
        response = self.client.post('/login/', {'username': 'provider1', 'password': 'password123'})
        self.assertEqual(response.status_code, 302, f"Failed Provider Login Redirect, got {response.status_code}")

    def test_book_provider(self):
        self.client.login(username='customer1', password='password123')
        response = self.client.get(reverse('book_provider', args=[self.provider_profile.id]))
        self.assertEqual(response.status_code, 200)
        
        # Test posting booking
        post_response = self.client.post(reverse('book_provider', args=[self.provider_profile.id]), {
            'skill': self.skill.id,
            'date': '2026-10-10',
            'time': '10:00:00',
            'message': 'Need help'
        })
        self.assertEqual(post_response.status_code, 302)
        
    def test_dashboards(self):
        self.client.login(username='customer1', password='password123')
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        self.client.login(username='provider1', password='password123')
        response = self.client.get(reverse('provider_dashboard'))
        self.assertEqual(response.status_code, 200)
