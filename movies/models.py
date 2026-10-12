import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Movie(models.Model):
    """
    Represents a movie available for viewing and community reviews.
    """
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    release_date = models.DateField()
    poster_url = models.URLField(max_length=500, help_text="Direct link to movie poster image")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-release_date', 'title']

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        """Calculates average rating from community reviews rounded to 1 decimal place."""
        avg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 1) if avg is not None else None

    @property
    def review_count(self):
        """Returns total count of community reviews."""
        return self.reviews.count()

    @property
    def duration_formatted(self):
        """Formats duration from minutes into hours and minutes (e.g., 2h 25m)."""
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        return f"{minutes}m"


class Showtime(models.Model):
    """
    Represents a specific movie screening with date, time, screen, and pricing.
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    show_date = models.DateField()
    show_time = models.TimeField()
    ticket_price = models.DecimalField(max_digits=6, decimal_places=2, default=12.50)
    screen_number = models.CharField(max_length=50, default="Screen 1")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['show_date', 'show_time']
        unique_together = ('movie', 'show_date', 'show_time', 'screen_number')

    def __str__(self):
        return f"{self.movie.title} | {self.show_date} {self.show_time.strftime('%I:%M %p')} ({self.screen_number})"

    def get_booked_seats(self):
        """
        Returns a set of all booked seat identifiers (e.g., {'A1', 'A2', 'C4'})
        for this particular showtime.
        """
        booked = set()
        for booking in self.bookings.all():
            for seat in booking.get_seats_list():
                booked.add(seat)
        return booked

    @property
    def booked_seats_count(self):
        """Total number of booked seats."""
        return len(self.get_booked_seats())

    @property
    def available_seats_count(self):
        """Total available seats (total capacity is 40 seats in a 5x8 grid)."""
        total_capacity = 40  # 5 rows x 8 columns
        return max(0, total_capacity - self.booked_seats_count)

    def is_seat_booked(self, seat_code):
        """Checks if a given seat code is already booked."""
        return seat_code.strip().upper() in self.get_booked_seats()


class SeatBooking(models.Model):
    """
    Stores customer reservations for a specific showtime.
    """
    booking_reference = models.CharField(max_length=16, unique=True, editable=False)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    selected_seats = models.CharField(
        max_length=255,
        help_text="Comma-separated seat codes, e.g. A1, A2, B5"
    )
    seat_count = models.PositiveIntegerField(default=1)
    total_paid = models.DecimalField(max_digits=8, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"Booking #{self.booking_reference} - {self.customer_name} ({self.selected_seats})"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate clean cinema-style booking reference (e.g., CINE-9FA2B1)
            self.booking_reference = f"CNM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_seats_list(self):
        """Returns normalized list of seat identifiers."""
        if not self.selected_seats:
            return []
        return [s.strip().upper() for s in self.selected_seats.split(',') if s.strip()]


class MovieReview(models.Model):
    """
    Community review and 1-5 star rating submitted for a movie.
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.reviewer_name} on {self.movie.title} ({self.rating}★)"
