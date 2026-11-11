from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Destination(models.Model):
    name = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="destinations")
    description = models.TextField()
    min_days = models.PositiveIntegerField(default=1)
    max_days = models.PositiveIntegerField(default=3)

    # All costs are estimates, per person, in rupees
    transport_cost = models.DecimalField(max_digits=8, decimal_places=2, help_text="Round trip, per person")
    stay_cost_per_day = models.DecimalField(max_digits=8, decimal_places=2, help_text="Per person per day")
    food_cost_per_day = models.DecimalField(max_digits=8, decimal_places=2, help_text="Per person per day")
    activity_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Total, per person")

    best_months = models.CharField(max_length=60, help_text="Month numbers separated by commas, e.g. 10,11,12,1,2")
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def best_months_list(self):
        return [int(m) for m in self.best_months.split(",") if m.strip().isdigit()]

    def estimated_cost(self, days, people=1):
        per_person = self.transport_cost + days * (self.stay_cost_per_day + self.food_cost_per_day) + self.activity_cost
        return per_person * people


class Preference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    budget = models.PositiveIntegerField(help_text="Budget per person in rupees")
    days = models.PositiveIntegerField()
    interests = models.ManyToManyField(Category, blank=True)
    travel_month = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])

    def __str__(self):
        return f"Preferences of {self.user.username}"


class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trips")
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    days = models.PositiveIntegerField()
    people = models.PositiveIntegerField(default=1)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def per_person_cost(self):
        return self.total_cost / self.people

    def __str__(self):
        return f"{self.user.username} - {self.destination.name}"


class TripDay(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="trip_days")
    day_number = models.PositiveIntegerField()
    plan_text = models.TextField()

    class Meta:
        ordering = ["day_number"]

    def __str__(self):
        return f"Day {self.day_number} of {self.trip}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "destination")  # one review per user per place

    def __str__(self):
        return f"{self.destination.name}: {self.rating}/5"