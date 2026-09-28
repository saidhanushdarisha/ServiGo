from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("service/<int:booking_pk>/new/", views.ServiceReviewCreateView.as_view(), name="service_create"),
    path("service/<int:booking_pk>/edit/", views.ServiceReviewUpdateView.as_view(), name="service_edit"),
    path("ev/<int:booking_pk>/new/", views.EVReviewCreateView.as_view(), name="ev_create"),
    path("ev/<int:booking_pk>/edit/", views.EVReviewUpdateView.as_view(), name="ev_edit"),
]
