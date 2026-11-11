from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q, Avg
from .models import Destination, Category


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