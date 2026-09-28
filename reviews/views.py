from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, UpdateView
from django.urls import reverse

from bookings.models import Booking
from ev_charging.models import EVChargingBooking
from services.models import Service
from .forms import ReviewForm
from .models import Review


class ServiceReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.booking = get_object_or_404(Booking, pk=kwargs["booking_pk"], customer=request.user)
        if self.booking.status != Booking.Status.COMPLETED:
            messages.error(request, "You can review a service only after it is completed.")
            return redirect("bookings:detail", pk=self.booking.pk)
        if Review.objects.filter(booking=self.booking).exists():
            return redirect("reviews:service_edit", booking_pk=self.booking.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        review = form.save(commit=False)
        review.customer = self.request.user
        review.booking = self.booking
        review.service = Service.objects.filter(name=self.booking.service_name).first()
        review.save()
        messages.success(self.request, "Thank you! Your service review has been submitted.")
        return redirect("bookings:detail", pk=self.booking.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"review_type": "Service", "booking": self.booking, "title": "Review your service"})
        return context


class ServiceReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/form.html"
    context_object_name = "review"

    def get_object(self, queryset=None):
        return get_object_or_404(Review, booking_id=self.kwargs["booking_pk"], customer=self.request.user)

    def get_success_url(self):
        return reverse("bookings:detail", kwargs={"pk": self.object.booking_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"review_type": "Service", "booking": self.object.booking, "title": "Edit your service review"})
        return context


class EVReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.booking = get_object_or_404(EVChargingBooking, pk=kwargs["booking_pk"], customer=request.user)
        if self.booking.status != EVChargingBooking.Status.COMPLETED:
            messages.error(request, "You can review an EV charging session only after it is completed.")
            return redirect("ev_charging:booking_detail", pk=self.booking.pk)
        if Review.objects.filter(ev_booking=self.booking).exists():
            return redirect("reviews:ev_edit", booking_pk=self.booking.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        review = form.save(commit=False)
        review.customer = self.request.user
        review.ev_booking = self.booking
        review.station = self.booking.station
        review.save()
        messages.success(self.request, "Thank you! Your EV station review has been submitted.")
        return redirect("ev_charging:booking_detail", pk=self.booking.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"review_type": "EV charging", "booking": self.booking, "title": "Review your EV charging session"})
        return context


class EVReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/form.html"
    context_object_name = "review"

    def get_object(self, queryset=None):
        return get_object_or_404(Review, ev_booking_id=self.kwargs["booking_pk"], customer=self.request.user)

    def get_success_url(self):
        return reverse("ev_charging:booking_detail", kwargs={"pk": self.object.ev_booking_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"review_type": "EV charging", "booking": self.object.ev_booking, "title": "Edit your EV station review"})
        return context
