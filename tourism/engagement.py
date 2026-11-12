import calendar

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Destination, Preference, Review
from .services import cost_breakdown, recommend_destinations


# ---------------------------------------------------------------
# Review form
# ---------------------------------------------------------------
class ReviewForm(forms.Form):
    RATING_CHOICES = [
        (5, "5 - Excellent"),
        (4, "4 - Very good"),
        (3, "3 - Good"),
        (2, "2 - Fair"),
        (1, "1 - Poor"),
    ]
    rating = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int, label="Your rating")
    comment = forms.CharField(
        required=False,
        max_length=500,
        label="Your comment (optional)",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rating"].widget.attrs["class"] = "form-select"
        self.fields["comment"].widget.attrs["class"] = "form-control"

    def clean_comment(self):
        return self.cleaned_data["comment"].strip()


# ---------------------------------------------------------------
# Destination detail with reviews
# ---------------------------------------------------------------
def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk, is_active=True)
    stats = destination.reviews.aggregate(avg=Avg("rating"), count=Count("id"))

    my_review = None
    form = None
    if request.user.is_authenticated:
        my_review = destination.reviews.filter(user=request.user).first()
        initial = {}
        if my_review:
            initial = {"rating": my_review.rating, "comment": my_review.comment}
        form = ReviewForm(initial=initial)

    return render(request, "tourism/destination_detail.html", {
        "destination": destination,
        "avg_rating": stats["avg"],
        "review_count": stats["count"],
        "reviews": destination.reviews.select_related("user").order_by("-created_at"),
        "my_review": my_review,
        "form": form,
    })


@login_required
@require_POST
def review_submit(request, pk):
    destination = get_object_or_404(Destination, pk=pk, is_active=True)
    form = ReviewForm(request.POST)

    if form.is_valid():
        # One review per user per destination: a second submit updates the first
        _, created = Review.objects.update_or_create(
            user=request.user,
            destination=destination,
            defaults={
                "rating": form.cleaned_data["rating"],
                "comment": form.cleaned_data["comment"],
            },
        )
        messages.success(request, "Review saved." if created else "Your review was updated.")
    else:
        messages.error(request, "Please choose a rating from 1 to 5 (comment: max 500 characters).")

    return redirect("destination_detail", pk=pk)


@login_required
@require_POST
def review_delete(request, pk):
    # Only the owner can delete: filtering by user=request.user protects other people's reviews
    review = get_object_or_404(Review, destination_id=pk, user=request.user)
    review.delete()
    messages.success(request, "Your review was deleted.")
    return redirect("destination_detail", pk=pk)


# ---------------------------------------------------------------
# Destination comparison
# ---------------------------------------------------------------
def _days_from(request, default):
    try:
        value = int(request.GET.get("days", default))
    except (TypeError, ValueError):
        value = default
    return max(1, min(15, value))


def compare(request):
    raw_ids = [int(i) for i in request.GET.getlist("ids") if i.isdigit()]
    ids = list(dict.fromkeys(raw_ids))[:4]          # remove duplicates, keep max 4

    found = (Destination.objects.filter(pk__in=ids, is_active=True)
             .select_related("category")
             .annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews")))
    by_id = {d.pk: d for d in found}
    destinations = [by_id[i] for i in ids if i in by_id]

    if len(destinations) < 2:
        messages.error(request, "Please select at least 2 destinations to compare.")
        return redirect("destination_list")

    # A logged-in user with saved preferences also gets a recommendation score
    pref = None
    if request.user.is_authenticated:
        pref = Preference.objects.filter(user=request.user).first()

    days = _days_from(request, pref.days if pref else 2)

    scores = {}
    if pref:
        ranked = recommend_destinations(
            budget=pref.budget,
            days=days,
            month=pref.travel_month,
            interest_ids=list(pref.interests.values_list("id", flat=True)),
            limit=1000,
        )
        scores = {r["destination"].pk: r["score"] for r in ranked}

    rows = []
    for d in destinations:
        breakdown = cost_breakdown(d, days, 1)
        months = ", ".join(calendar.month_abbr[m] for m in d.best_months_list() if 1 <= m <= 12)
        rows.append({
            "d": d,
            "breakdown": breakdown,
            "cost": breakdown["per_person"],
            "months": months,
            "score": scores.get(d.pk),
            "season_ok": (pref.travel_month in d.best_months_list()) if pref else None,
        })

    cheapest = min(r["cost"] for r in rows)
    for r in rows:
        r["is_cheapest"] = r["cost"] == cheapest

    return render(request, "tourism/compare.html", {
        "rows": rows,
        "days": days,
        "pref": pref,
        "pref_month": calendar.month_name[pref.travel_month] if pref else "",
    })