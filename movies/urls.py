from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('movies/', views.movie_list_view, name='movie_list'),
    path('movies/<int:pk>/', views.movie_detail_view, name='movie_detail'),
    path('booking/<int:showtime_id>/', views.seat_booking_view, name='seat_booking'),
    path('confirmation/<str:reference>/', views.booking_confirmation_view, name='booking_confirmation'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('reviews/add/', views.add_review_view, name='add_review'),
    path('reviews/add/<int:movie_id>/', views.add_review_view, name='add_movie_review'),
]
