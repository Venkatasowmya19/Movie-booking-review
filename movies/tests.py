from datetime import date, time
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from movies.models import Movie, Showtime, SeatBooking, MovieReview
from movies.forms import SeatBookingForm, MovieReviewForm


class CinemaPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.movie = Movie.objects.create(
            title="Interstellar Voyage",
            genre="Sci-Fi",
            duration=150,
            release_date=date(2026, 1, 15),
            poster_url="https://images.unsplash.com/photo-1518709268805-4e9042af9f23",
            description="A journey across distant star clusters."
        )
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            show_date=date(2026, 10, 15),
            show_time=time(19, 30),
            ticket_price=Decimal("15.00"),
            screen_number="Screen 1 (IMAX)"
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Interstellar Voyage")
        self.assertContains(response, "CineSphere")

    def test_movie_list_and_filter(self):
        response = self.client.get(reverse('movie_list') + '?genre=Sci-Fi')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Interstellar Voyage")

    def test_movie_detail_view(self):
        response = self.client.get(reverse('movie_detail', args=[self.movie.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Screen 1 (IMAX)")
        self.assertContains(response, "Select Seats")

    def test_seat_booking_view_get(self):
        response = self.client.get(reverse('seat_booking', args=[self.showtime.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Interactive 5 × 8 Cinema Seat Grid")
        self.assertContains(response, "A1")
        self.assertContains(response, "E8")

    def test_seat_booking_successful_post(self):
        post_data = {
            'customer_name': 'Jane Doe',
            'customer_email': 'jane.doe@example.com',
            'customer_phone': '+1 555-4321',
            'selected_seats': 'B3, B4'
        }
        response = self.client.post(reverse('seat_booking', args=[self.showtime.pk]), post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify booking in database
        booking = SeatBooking.objects.get(customer_email='jane.doe@example.com')
        self.assertEqual(booking.seat_count, 2)
        self.assertEqual(booking.total_paid, Decimal("30.00"))
        self.assertIn("B3", booking.selected_seats)
        self.assertIn("B4", booking.selected_seats)
        
        # Verify booked seats for showtime
        self.assertTrue(self.showtime.is_seat_booked('B3'))
        self.assertTrue(self.showtime.is_seat_booked('B4'))
        self.assertFalse(self.showtime.is_seat_booked('B5'))

    def test_duplicate_seat_booking_prevention(self):
        # First booking for seat C4
        SeatBooking.objects.create(
            showtime=self.showtime,
            customer_name='Original Booker',
            customer_email='first@example.com',
            customer_phone='1234567890',
            selected_seats='C4',
            seat_count=1,
            total_paid=Decimal("15.00")
        )
        
        # Attempt to book seat C4 again
        post_data = {
            'customer_name': 'Second Booker',
            'customer_email': 'second@example.com',
            'customer_phone': '9876543210',
            'selected_seats': 'C4'
        }
        response = self.client.post(reverse('seat_booking', args=[self.showtime.pk]), post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify no second booking was created
        self.assertEqual(SeatBooking.objects.filter(selected_seats__contains='C4').count(), 1)
        self.assertContains(response, "booked by another customer")

    def test_movie_review_creation_and_average(self):
        # Post first review
        MovieReview.objects.create(
            movie=self.movie,
            reviewer_name="Alice",
            rating=5,
            comment="Magnificent film!"
        )
        # Post second review
        MovieReview.objects.create(
            movie=self.movie,
            reviewer_name="Bob",
            rating=3,
            comment="Good visuals, average plot."
        )
        self.assertEqual(self.movie.average_rating, 4.0)
        self.assertEqual(self.movie.review_count, 2)
