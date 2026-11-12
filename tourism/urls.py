from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.destination_list, name='destination_list'),
    path('destination/<int:pk>/', views.destination_detail, name='destination_detail'),
    path('recommend/', views.recommend, name='recommend'),
    path('plan/<int:pk>/', views.plan_trip, name='plan_trip'),
    path('trips/', views.my_trips, name='my_trips'),
    path('trips/<int:pk>/', views.trip_detail, name='trip_detail'),
    path('trips/<int:pk>/edit/', views.trip_edit, name='trip_edit'),
    path('trips/<int:pk>/delete/', views.trip_delete, name='trip_delete'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='tourism/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]