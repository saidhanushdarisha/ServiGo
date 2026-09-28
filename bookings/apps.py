# Bookings app configuration
from django.apps import AppConfig


class BookingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bookings"
    verbose_name = "Bookings"

    def ready(self):
        from . import signals  # noqa: F401
