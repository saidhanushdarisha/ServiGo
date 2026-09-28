from datetime import date, time

from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from bookings.models import Booking
from tests.accounts.factories import make_customer


class BookingLifecycleTests(TestCase):
    def setUp(self):
        self.customer = make_customer(email="lifecycle@example.com", username="lifecycle")

    def test_status_transitions_set_lifecycle_timestamps(self):
        booking = Booking.objects.create(
            customer=self.customer,
            customer_name="Lifecycle User",
            customer_email=self.customer.email,
            customer_phone="9999999999",
            service_name="Electrician Visit",
            service_price=349,
            location="Bengaluru",
            address="Test address",
            preferred_date=date.today(),
            preferred_time=time(10, 0),
        )
        self.assertIsNone(booking.confirmed_at)
        booking.status = Booking.Status.CONFIRMED
        booking.save()
        booking.refresh_from_db()
        self.assertIsNotNone(booking.confirmed_at)
        booking.status = Booking.Status.IN_PROGRESS
        booking.save()
        booking.refresh_from_db()
        self.assertIsNotNone(booking.started_at)
        booking.status = Booking.Status.COMPLETED
        booking.save()
        booking.refresh_from_db()
        self.assertIsNotNone(booking.completed_at)
