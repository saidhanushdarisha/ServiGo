from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save

from accounts.models import CustomerProfile
from .models import Booking


def sync_customer_profile(user_id):
    """Keep denormalized customer booking totals synchronized with bookings."""
    if not user_id:
        return
    profile, _ = CustomerProfile.objects.get_or_create(user_id=user_id)
    qs = Booking.objects.filter(customer_id=user_id)
    profile.total_bookings = qs.count()
    profile.total_spent = qs.filter(status=Booking.Status.COMPLETED).aggregate(total=Sum("service_price"))["total"] or 0
    profile.save(update_fields=["total_bookings", "total_spent", "updated_at"])


@receiver(post_save, sender=Booking)
def booking_saved(sender, instance, **kwargs):
    sync_customer_profile(instance.customer_id)


@receiver(post_delete, sender=Booking)
def booking_deleted(sender, instance, **kwargs):
    sync_customer_profile(instance.customer_id)
