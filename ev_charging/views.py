"""
Views for the EV charging app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.db import transaction
from django.db.models import Avg, Count
from reviews.models import Review
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import EVChargingStation, EVChargingBooking
from .forms import EVStationSearchForm, EVBookingForm


class EVStationListView(ListView):
    """List EV charging stations with search and filtering."""
    model = EVChargingStation
    template_name = "ev_charging/station_list.html"
    context_object_name = "stations"
    paginate_by = 12

    def get_queryset(self):
        queryset = EVChargingStation.objects.filter(is_active=True)

        # Search by location
        location = self.request.GET.get("location")
        if location:
            queryset = queryset.filter(
                Q(name__icontains=location) |
                Q(address__icontains=location) |
                Q(city__icontains=location) |
                Q(state__icontains=location) |
                Q(pincode__icontains=location)
            )

        # Filter by charger type
        charger_type = self.request.GET.get("charger_type")
        if charger_type:
            queryset = queryset.filter(charger_type=charger_type)

        # Filter by max price
        max_price = self.request.GET.get("max_price")
        if max_price:
            queryset = queryset.filter(price_per_kwh__lte=max_price)

        # Available only
        if self.request.GET.get("available_only") == "on":
            queryset = queryset.filter(status=EVChargingStation.Status.AVAILABLE, available_ports__gt=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = EVStationSearchForm(self.request.GET)
        context["charger_types"] = EVChargingStation.ChargerType.choices
        return context


class EVStationDetailView(DetailView):
    """EV charging station detail view."""
    model = EVChargingStation
    template_name = "ev_charging/station_detail.html"
    context_object_name = "station"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return EVChargingStation.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = self.object
        # Check if station is open now
        context["is_open_now"] = station.is_open_now()
        review_qs = Review.objects.filter(station=station).select_related("customer")
        context["reviews"] = review_qs[:10]
        summary = review_qs.aggregate(average=Avg("rating"), count=Count("id"))
        context["review_average"] = summary["average"]
        context["review_count"] = summary["count"] or 0
        return context


class EVBookingCreateView(LoginRequiredMixin, CreateView):
    """Create an EV charging booking."""
    model = EVChargingBooking
    form_class = EVBookingForm
    template_name = "ev_charging/booking_create.html"

    def dispatch(self, request, *args, **kwargs):
        self.station = get_object_or_404(EVChargingStation, slug=kwargs.get("slug"), is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["station"] = self.station
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["station"] = self.station
        context["is_open_now"] = self.station.is_open_now()
        return context

    def form_valid(self, form):
        # Re-check capacity inside a transaction immediately before writing. This prevents
        # normal double-booking races and keeps port capacity consistent.
        with transaction.atomic():
            station = EVChargingStation.objects.select_for_update().get(pk=self.station.pk)
            available = station.get_available_ports_for_slot(
                form.cleaned_data["booking_date"],
                form.cleaned_data["start_time"],
                form.cleaned_data["end_time"],
            )
            if available < 1:
                form.add_error(None, "No charging port is available for the selected date and time. Please choose another slot.")
                return self.form_invalid(form)

            booking = form.save(commit=False)
            booking.customer = self.request.user
            booking.customer_name = self.request.user.get_full_name() or self.request.user.username
            booking.customer_email = self.request.user.email
            booking.customer_phone = self.request.user.phone
            booking.station = station
            booking.save()
            self._sync_station_current_ports(station)

        self.send_confirmation_email(booking)
        messages.success(self.request, "EV charging slot booked successfully! A charging port has been reserved for your selected time.")
        return redirect("ev_charging:booking_confirmation", pk=booking.pk)

    @staticmethod
    def _sync_station_current_ports(station):
        station.sync_current_available_ports()
        station.save(update_fields=["available_ports", "updated_at"])

    def send_confirmation_email(self, booking):
        """Send booking confirmation email."""
        try:
            subject = f"EV Charging Booking Confirmation - {booking.station.name} - ServiGo"
            message = f"""
Dear {booking.customer_name},

Your EV charging slot has been booked with ServiGo!

Booking Details:
- Station: {booking.station.name}
- Address: {booking.station.address}, {booking.station.city}
- Charger Type: {booking.station.get_charger_type_display()}
- Charging Speed: {booking.station.charging_speed_kw} kW
- Price: ₹{booking.station.price_per_kwh:,.2f}/kWh
- Date: {booking.booking_date.strftime('%B %d, %Y')}
- Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
- Estimated Energy: {booking.estimated_kwh} kWh
- Estimated Cost: ₹{booking.estimated_cost:,.2f}

Your booking is currently {booking.get_status_display()}. Please arrive at the station during your booked time slot.

For any queries, contact us at support@servigo.com

Thank you for choosing ServiGo!
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.customer_email],
                fail_silently=True,
            )
        except Exception:
            pass


class EVBookingConfirmationView(LoginRequiredMixin, DetailView):
    """EV booking confirmation page."""
    model = EVChargingBooking
    template_name = "ev_charging/booking_confirmation.html"
    context_object_name = "booking"

    def get_queryset(self):
        return EVChargingBooking.objects.filter(customer=self.request.user).select_related("station")


class EVBookingListView(LoginRequiredMixin, ListView):
    """List user's EV bookings."""
    model = EVChargingBooking
    template_name = "ev_charging/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        queryset = EVChargingBooking.objects.filter(customer=self.request.user).select_related("station")

        # Status filter
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = EVChargingBooking.Status.choices
        context["current_status"] = self.request.GET.get("status", "")
        return context


class EVBookingDetailView(LoginRequiredMixin, DetailView):
    """EV booking detail view."""
    model = EVChargingBooking
    template_name = "ev_charging/booking_detail.html"
    context_object_name = "booking"

    def get_queryset(self):
        user = self.request.user
        if user.is_staff_user or user.is_admin_user:
            return EVChargingBooking.objects.all().select_related("customer", "station")
        return EVChargingBooking.objects.filter(customer=user).select_related("station")


@login_required
def ev_booking_cancel(request, pk):
    """Cancel an EV booking."""
    booking = get_object_or_404(EVChargingBooking, pk=pk, customer=request.user)

    if booking.status in [EVChargingBooking.Status.COMPLETED, EVChargingBooking.Status.CANCELLED]:
        messages.error(request, "This booking cannot be cancelled.")
        return redirect("ev_charging:booking_detail", pk=pk)

    if request.method == "POST":
        with transaction.atomic():
            station = EVChargingStation.objects.select_for_update().get(pk=booking.station_id)
            booking.status = EVChargingBooking.Status.CANCELLED
            booking.save()
            EVBookingCreateView._sync_station_current_ports(station)
        messages.success(request, "EV charging booking cancelled successfully. The reserved port is available again.")
        return redirect("ev_charging:booking_list")

    return render(request, "ev_charging/booking_cancel.html", {"booking": booking})


# Staff/Admin views
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require staff or admin role."""
    def test_func(self):
        return self.request.user.is_staff_user or self.request.user.is_admin_user


class StaffEVStationListView(StaffRequiredMixin, ListView):
    """Staff view of EV stations."""
    model = EVChargingStation
    template_name = "ev_charging/staff_station_list.html"
    context_object_name = "stations"
    paginate_by = 20

    def get_queryset(self):
        queryset = EVChargingStation.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query)
            )
        return queryset


class StaffEVBookingListView(StaffRequiredMixin, ListView):
    """Staff view of EV bookings."""
    model = EVChargingBooking
    template_name = "ev_charging/staff_booking_list.html"
    context_object_name = "bookings"
    paginate_by = 20

    def get_queryset(self):
        queryset = EVChargingBooking.objects.all().select_related("customer", "station")

        # Filter by status
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Search
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(customer_name__icontains=query) |
                Q(customer_email__icontains=query) |
                Q(station__name__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = EVChargingBooking.Status.choices
        context["current_status"] = self.request.GET.get("status", "")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class StaffEVBookingDetailView(StaffRequiredMixin, DetailView):
    """Staff EV booking detail with status update."""
    model = EVChargingBooking
    template_name = "ev_charging/staff_booking_detail.html"
    context_object_name = "booking"

    def post(self, request, *args, **kwargs):
        booking = self.get_object()
        new_status = request.POST.get("status")
        if new_status in dict(EVChargingBooking.Status.choices):
            with transaction.atomic():
                station = EVChargingStation.objects.select_for_update().get(pk=booking.station_id)
                booking.status = new_status
                booking.save()
                EVBookingCreateView._sync_station_current_ports(station)
            messages.success(request, f"Booking status updated to {booking.get_status_display()}.")
        return redirect("ev_charging:staff_booking_detail", pk=booking.pk)