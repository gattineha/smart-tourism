from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q
from django.shortcuts import render

from .models import Category, Destination, Preference, Review, Trip


@staff_member_required
def dashboard(request):
    # 1. Active destinations in each category
    by_category = Category.objects.annotate(
        n=Count('destinations', filter=Q(destinations__is_active=True))
    ).order_by('-n', 'name')

    # 2. Most frequently saved destinations (top 5)
    most_saved = (Destination.objects.annotate(n=Count('trip'))
                  .filter(n__gt=0).order_by('-n', 'name')[:5])

    # 3. Interests chosen by users in their preferences
    interests = (Category.objects.annotate(n=Count('preference'))
                 .filter(n__gt=0).order_by('-n', 'name'))

    # 4. How many trips were planned for 1 day, 2 days, 3 days...
    durations = Trip.objects.values('days').annotate(n=Count('id')).order_by('days')

    # 5. Average estimated cost per person across saved trips
    per_person = [float(t.total_cost) / t.people for t in Trip.objects.all()]
    avg_trip_budget = round(sum(per_person) / len(per_person)) if per_person else 0

    avg_pref_budget = Preference.objects.aggregate(a=Avg('budget'))['a']

    cards = {
        'destinations': Destination.objects.filter(is_active=True).count(),
        'users': User.objects.filter(is_staff=False).count(),
        'trips': Trip.objects.count(),
        'reviews': Review.objects.count(),
        'avg_trip_budget': avg_trip_budget,
        'avg_pref_budget': round(avg_pref_budget) if avg_pref_budget else 0,
    }

    chart_data = {
        'category': {'labels': [c.name for c in by_category],
                     'values': [c.n for c in by_category]},
        'saved': {'labels': [d.name for d in most_saved],
                  'values': [d.n for d in most_saved]},
        'interests': {'labels': [c.name for c in interests],
                      'values': [c.n for c in interests]},
        'durations': {'labels': [f"{d['days']} day(s)" for d in durations],
                      'values': [d['n'] for d in durations]},
    }

    return render(request, 'tourism/dashboard.html', {'cards': cards, 'chart_data': chart_data})