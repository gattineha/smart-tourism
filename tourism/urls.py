from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.destination_list, name='destination_list'),
    path('destination/<int:pk>/', views.destination_detail, name='destination_detail'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='tourism/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]