from django.contrib import admin
from .models import Category, Destination, Preference, Trip, TripDay, Review


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "district", "category", "min_days", "max_days", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "district")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("destination", "user", "rating", "created_at")
    list_filter = ("rating", "destination")
    search_fields = ("comment", "user__username", "destination__name")


admin.site.register(Category)
admin.site.register(Preference)
admin.site.register(Trip)
admin.site.register(TripDay)