from django import forms
from django.utils import timezone
from .models import EVChargingStation, EVChargingBooking


class EVStationSearchForm(forms.Form):
    """Form for searching EV charging stations."""

    location = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Search by city, area, or address..."}))
    charger_type = forms.ChoiceField(required=False, choices=[("", "All Types")] + list(EVChargingStation.ChargerType.choices), widget=forms.Select(attrs={"class": "form-select"}))
    max_price = forms.DecimalField(required=False, max_digits=6, decimal_places=2, widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Max ₹/kWh", "step": "0.50", "min": "0"}))
    available_only = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))


class EVBookingForm(forms.ModelForm):
    """Form for creating an EV charging booking with time/capacity validation."""

    booking_date = forms.DateField(widget=forms.DateInput(attrs={"class": "form-control", "type": "date", "min": timezone.now().date().isoformat()}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={"class": "form-control", "type": "time"}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={"class": "form-control", "type": "time"}))
    estimated_kwh = forms.DecimalField(max_digits=6, decimal_places=2, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": "1", "placeholder": "Estimated kWh needed"}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Any special instructions (optional)"}))

    class Meta:
        model = EVChargingBooking
        fields = ("booking_date", "start_time", "end_time", "estimated_kwh", "notes")

    def __init__(self, *args, **kwargs):
        self.station = kwargs.pop("station", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        booking_date = cleaned_data.get("booking_date")

        if booking_date and booking_date < timezone.now().date():
            raise forms.ValidationError("Booking date cannot be in the past.")
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
        if not self.station or not booking_date or not start_time or not end_time:
            return cleaned_data

        if self.station.status in {EVChargingStation.Status.MAINTENANCE, EVChargingStation.Status.OFFLINE}:
            raise forms.ValidationError("This charging station is currently unavailable for bookings.")

        # Validate operating hours, including overnight schedules such as 22:00-06:00.
        if not self.station.is_24_hours:
            opens_at, closes_at = self.station.opens_at, self.station.closes_at
            if opens_at and closes_at:
                if opens_at <= closes_at:
                    within_hours = opens_at <= start_time and end_time <= closes_at
                else:
                    within_hours = (start_time >= opens_at and end_time > start_time) or (end_time <= closes_at and start_time < closes_at)
                if not within_hours:
                    raise forms.ValidationError(f"Station operates from {opens_at.strftime('%H:%M')} to {closes_at.strftime('%H:%M')}.")

        available = self.station.get_available_ports_for_slot(booking_date, start_time, end_time, exclude_booking_id=self.instance.pk if self.instance.pk else None)
        if available < 1:
            raise forms.ValidationError("No charging port is available for the selected date and time. Please choose another slot.")
        return cleaned_data

    def save(self, commit=True):
        booking = super().save(commit=False)
        if self.station:
            booking.station = self.station
            booking.estimated_cost = self.cleaned_data.get("estimated_kwh", 0) * self.station.price_per_kwh
        if commit:
            booking.save()
        return booking
