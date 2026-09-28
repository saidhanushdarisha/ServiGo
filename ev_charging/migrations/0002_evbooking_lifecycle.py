from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("ev_charging", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="evchargingbooking",
            name="cancelled_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="cancelled at"),
        ),
    ]
