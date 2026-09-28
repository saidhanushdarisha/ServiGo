from datetime import date, time
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from bookings.models import Booking
from reviews.models import Review
from services.models import Service, ServiceCategory
from tests.accounts.factories import make_customer


class ReviewTests(TestCase):
    def setUp(self):
        self.customer = make_customer(email="review@example.com", username="reviewcustomer")
        category = ServiceCategory.objects.create(name="Electrical", slug="electrical", icon="bi-lightning")
        self.service = Service.objects.create(
            category=category, name="Electrician Visit", slug="electrician-visit",
            short_description="Test", description="Test service", price=Decimal("349.00"),
            estimated_duration=60,
        )
        self.booking = Booking.objects.create(
            customer=self.customer, customer_name="Review Customer", customer_email=self.customer.email,
            customer_phone="9999999999", service_name=self.service.name, service_price=self.service.price,
            location="Bengaluru", address="Test", preferred_date=date.today(), preferred_time=time(10),
            status=Booking.Status.COMPLETED,
        )

    def test_customer_can_submit_one_review_for_completed_booking(self):
        self.client.force_login(self.customer)
        response = self.client.post(reverse("reviews:service_create", args=[self.booking.pk]), {"rating": "5", "comment": "Great service"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(booking=self.booking).count(), 1)
        self.assertEqual(Review.objects.get(booking=self.booking).rating, 5)
