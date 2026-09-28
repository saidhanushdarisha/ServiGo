from datetime import date, time
from decimal import Decimal

from django.test import TestCase

from ev_charging.forms import EVBookingForm
from ev_charging.models import EVChargingBooking, EVChargingStation
from tests.accounts.factories import make_customer


class EVCapacityTests(TestCase):
    def setUp(self):
        self.customer = make_customer(email="ev@example.com", username="evcustomer")
        self.station = EVChargingStation.objects.create(
            name="Test Station", slug="test-station", address="1 Test Road", city="Bengaluru",
            state="Karnataka", pincode="560001", charging_speed_kw=60,
            price_per_kwh=Decimal("12.00"), total_ports=1, available_ports=1,
            opens_at=time(6, 0), closes_at=time(22, 0),
        )

    def test_overlapping_slot_is_rejected_when_all_ports_are_reserved(self):
        EVChargingBooking.objects.create(
            customer=self.customer, customer_name="Test", customer_email=self.customer.email,
            customer_phone="9999999999", station=self.station, booking_date=date.today(),
            start_time=time(10, 0), end_time=time(11, 0), estimated_kwh=Decimal("10"),
            estimated_cost=Decimal("120"), status=EVChargingBooking.Status.CONFIRMED,
        )
        form = EVBookingForm(
            data={"booking_date": date.today().isoformat(), "start_time": "10:30", "end_time": "11:30", "estimated_kwh": "10", "notes": ""},
            station=self.station,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("No charging port is available", str(form.errors))

    def test_non_overlapping_slot_is_allowed(self):
        EVChargingBooking.objects.create(
            customer=self.customer, customer_name="Test", customer_email=self.customer.email,
            customer_phone="9999999999", station=self.station, booking_date=date.today(),
            start_time=time(10, 0), end_time=time(11, 0), estimated_kwh=Decimal("10"),
            estimated_cost=Decimal("120"), status=EVChargingBooking.Status.CONFIRMED,
        )
        form = EVBookingForm(
            data={"booking_date": date.today().isoformat(), "start_time": "11:00", "end_time": "12:00", "estimated_kwh": "10", "notes": ""},
            station=self.station,
        )
        self.assertTrue(form.is_valid(), form.errors)
