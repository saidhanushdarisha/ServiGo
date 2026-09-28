from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """A customer rating/review for a completed service or EV booking."""
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    booking = models.OneToOneField(
        "bookings.Booking", on_delete=models.CASCADE, null=True, blank=True, related_name="review"
    )
    ev_booking = models.OneToOneField(
        "ev_charging.EVChargingBooking", on_delete=models.CASCADE, null=True, blank=True, related_name="review"
    )
    service = models.ForeignKey(
        "services.Service", on_delete=models.CASCADE, null=True, blank=True, related_name="reviews"
    )
    station = models.ForeignKey(
        "ev_charging.EVChargingStation", on_delete=models.CASCADE, null=True, blank=True, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(booking__isnull=False, ev_booking__isnull=True)
                    | models.Q(booking__isnull=True, ev_booking__isnull=False)
                ),
                name="review_exactly_one_booking_type",
            ),
        ]

    def __str__(self):
        target = self.service or self.station or "Booking"
        return f"{self.rating}/5 - {target} by {self.customer}"

    @property
    def stars(self):
        return "★" * self.rating + "☆" * (5 - self.rating)
