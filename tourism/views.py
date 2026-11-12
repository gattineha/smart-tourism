import calendar
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Q, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import PreferenceForm
from .models import Destination, Category, Preference, Trip, TripDay
from .services import recommend_destinations, cost_breakdown


# ---------------------------------------------------------------
# Destinations, login and register
# ---------------------------------------------------------------
def destination_list(request):
    destinations = Destination.objects.filter(is_active=True).select_related('category')

    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')

    if q:
        destinations = destinations.filter(Q(name__icontains=q) | Q(district__icontains=q))
    if category_id.isdigit():
        destinations = destinations.filter(category_id=int(category_id))

    context = {
        'destinations': destinations,
        'categories': Category.objects.all(),
        'q': q,
        'selected_category': category_id,
    }
    return render(request, 'tourism/destination_list.html', context)


def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk, is_active=True)
    avg_rating = destination.reviews.aggregate(avg=Avg('rating'))['avg']
    return render(request, 'tourism/destination_detail.html', {
        'destination': destination,
        'avg_rating': avg_rating,
        'reviews': destination.reviews.select_related('user'),
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('destination_list')
    else:
        form = UserCreationForm()
    return render(request, 'tourism/register.html', {'form': form})


# ---------------------------------------------------------------
# Recommendation
# ---------------------------------------------------------------
@login_required
def recommend(request):
    results = None
    searched = False
    context_extra = {}

    if request.method == 'POST':
        form = PreferenceForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            pref, _ = Preference.objects.update_or_create(
                user=request.user,
                defaults={
                    'budget': data['budget'],
                    'days': data['days'],
                    'travel_month': data['travel_month'],
                },
            )
            pref.interests.set(data['interests'])

            results = recommend_destinations(
                budget=data['budget'],
                days=data['days'],
                month=data['travel_month'],
                interest_ids=[c.id for c in data['interests']],
                people=data['people'],
            )
            searched = True
            context_extra = {
                'people': data['people'],
                'month_name': calendar.month_name[data['travel_month']],
            }
    else:
        initial = {}
        saved = Preference.objects.filter(user=request.user).first()
        if saved:
            initial = {
                'budget': saved.budget,
                'days': saved.days,
                'travel_month': saved.travel_month,
                'interests': saved.interests.all(),
            }
        form = PreferenceForm(initial=initial)

    context = {'form': form, 'results': results, 'searched': searched}
    context.update(context_extra)
    return render(request, 'tourism/recommend.html', context)


# ---------------------------------------------------------------
# Budget and itinerary (trips)
# ---------------------------------------------------------------
def _to_int(value, default, low, high):
    """Turns text into a whole number kept between low and high."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def _plan_context(destination, days, people, texts):
    rows = [{'number': n, 'text': texts.get(n, '')} for n in range(1, days + 1)]
    return {
        'destination': destination,
        'days': days,
        'people': people,
        'rows': rows,
        'breakdown': cost_breakdown(destination, days, people),
    }


def _save_days(trip, days, source):
    """Replaces the day-wise plan of a trip with the text entered in the form."""
    trip.trip_days.all().delete()
    TripDay.objects.bulk_create([
        TripDay(trip=trip, day_number=n, plan_text=source.get(f'day_{n}', '').strip())
        for n in range(1, days + 1)
    ])


@login_required
def plan_trip(request, pk):
    destination = get_object_or_404(Destination, pk=pk, is_active=True)
    source = request.POST if request.method == 'POST' else request.GET
    days = _to_int(source.get('days'), destination.min_days, 1, 15)
    people = _to_int(source.get('people'), 1, 1, 50)

    if request.method == 'POST' and 'save' in request.POST:
        breakdown = cost_breakdown(destination, days, people)
        with transaction.atomic():
            trip = Trip.objects.create(
                user=request.user,
                destination=destination,
                days=days,
                people=people,
                total_cost=Decimal(str(round(breakdown['total'], 2))),
            )
            _save_days(trip, days, request.POST)
        messages.success(request, 'Trip saved successfully.')
        return redirect('trip_detail', pk=trip.pk)

    texts = {n: source.get(f'day_{n}', '') for n in range(1, days + 1)}
    return render(request, 'tourism/plan_trip.html',
                  _plan_context(destination, days, people, texts))


@login_required
def my_trips(request):
    trips = (Trip.objects.filter(user=request.user)
             .select_related('destination')
             .order_by('-created_at'))
    return render(request, 'tourism/my_trips.html', {'trips': trips})


@login_required
def trip_detail(request, pk):
    # user=request.user means nobody can open someone else's trip
    trip = get_object_or_404(Trip, pk=pk, user=request.user)
    breakdown = cost_breakdown(trip.destination, trip.days, trip.people)
    return render(request, 'tourism/trip_detail.html', {'trip': trip, 'breakdown': breakdown})


@login_required
def trip_edit(request, pk):
    trip = get_object_or_404(Trip, pk=pk, user=request.user)
    destination = trip.destination

    if request.method == 'POST':
        days = _to_int(request.POST.get('days'), trip.days, 1, 15)
        people = _to_int(request.POST.get('people'), trip.people, 1, 50)

        if 'save' in request.POST:
            breakdown = cost_breakdown(destination, days, people)
            with transaction.atomic():
                trip.days = days
                trip.people = people
                trip.total_cost = Decimal(str(round(breakdown['total'], 2)))
                trip.save()
                _save_days(trip, days, request.POST)
            messages.success(request, 'Trip updated.')
            return redirect('trip_detail', pk=trip.pk)

        texts = {n: request.POST.get(f'day_{n}', '') for n in range(1, days + 1)}
    else:
        days, people = trip.days, trip.people
        texts = {td.day_number: td.plan_text for td in trip.trip_days.all()}

    context = _plan_context(destination, days, people, texts)
    context['trip'] = trip
    return render(request, 'tourism/plan_trip.html', context)


@login_required
@require_POST
def trip_delete(request, pk):
    trip = get_object_or_404(Trip, pk=pk, user=request.user)
    trip.delete()
    messages.success(request, 'Trip deleted.')
    return redirect('my_trips')