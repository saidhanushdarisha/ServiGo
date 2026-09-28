from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("bookings", "0002_booking_lifecycle_timestamps"),
        ("ev_charging", "0002_evbooking_lifecycle"),
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ("comment", models.TextField(blank=True, max_length=1000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("booking", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="review", to="bookings.booking")),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to=settings.AUTH_USER_MODEL)),
                ("ev_booking", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="review", to="ev_charging.evchargingbooking")),
                ("service", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="services.service")),
                ("station", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="ev_charging.evchargingstation")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="review",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(("booking__isnull", False), ("ev_booking__isnull", True))
                    | models.Q(("booking__isnull", True), ("ev_booking__isnull", False))
                ),
                name="review_exactly_one_booking_type",
            ),
        ),
    ]
