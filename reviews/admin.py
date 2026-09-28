from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "rating", "service", "station", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("customer__email", "customer__username", "comment", "service__name", "station__name")
    autocomplete_fields = ("customer", "booking", "ev_booking", "service", "station")
    readonly_fields = ("created_at", "updated_at")
