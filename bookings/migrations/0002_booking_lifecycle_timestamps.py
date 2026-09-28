from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("bookings", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="started_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="started at"),
        ),
        migrations.AddField(
            model_name="booking",
            name="cancelled_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="cancelled at"),
        ),
    ]
