from django.contrib import admin
from .models import Movie, Showtime, SeatBooking, MovieReview


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'duration_display', 'release_date', 'rating_display', 'review_count_display', 'showtimes_count')
    list_filter = ('genre', 'release_date')
    search_fields = ('title', 'genre', 'description')
    date_hierarchy = 'release_date'
    ordering = ('-release_date', 'title')

    def duration_display(self, obj):
        return obj.duration_formatted
    duration_display.short_description = "Duration"

    def rating_display(self, obj):
        avg = obj.average_rating
        return f"{avg} ★" if avg else "No reviews"
    rating_display.short_description = "Avg Rating"

    def review_count_display(self, obj):
        return obj.review_count
    review_count_display.short_description = "Reviews"

    def showtimes_count(self, obj):
        return obj.showtimes.count()
    showtimes_count.short_description = "Showtimes"


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'show_date', 'formatted_time', 'screen_number', 'ticket_price', 'booked_seats_display', 'available_seats_display')
    list_filter = ('show_date', 'screen_number', 'movie')
    search_fields = ('movie__title', 'screen_number')
    date_hierarchy = 'show_date'
    ordering = ('show_date', 'show_time')

    def formatted_time(self, obj):
        return obj.show_time.strftime('%I:%M %p')
    formatted_time.short_description = "Time"

    def booked_seats_display(self, obj):
        count = obj.booked_seats_count
        return f"{count} / 40 seats"
    booked_seats_display.short_description = "Booked"

    def available_seats_display(self, obj):
        return f"{obj.available_seats_count} remaining"
    available_seats_display.short_description = "Available"


@admin.register(SeatBooking)
class SeatBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'customer_name', 'customer_email', 'movie_title', 'show_info', 'selected_seats', 'seat_count', 'total_paid', 'booking_date')
    list_filter = ('showtime__show_date', 'showtime__screen_number', 'booking_date')
    search_fields = ('booking_reference', 'customer_name', 'customer_email', 'customer_phone', 'selected_seats')
    readonly_fields = ('booking_reference', 'booking_date')
    date_hierarchy = 'booking_date'
    ordering = ('-booking_date',)

    def movie_title(self, obj):
        return obj.showtime.movie.title
    movie_title.short_description = "Movie"

    def show_info(self, obj):
        return f"{obj.showtime.show_date} {obj.showtime.show_time.strftime('%I:%M %p')}"
    show_info.short_description = "Showtime"


@admin.register(MovieReview)
class MovieReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'reviewer_name', 'rating_stars', 'short_comment', 'created_date')
    list_filter = ('rating', 'movie', 'created_date')
    search_fields = ('reviewer_name', 'comment', 'movie__title')
    date_hierarchy = 'created_date'
    ordering = ('-created_date',)

    def rating_stars(self, obj):
        return "★" * obj.rating + "☆" * (5 - obj.rating)
    rating_stars.short_description = "Rating"

    def short_comment(self, obj):
        return (obj.comment[:60] + '...') if len(obj.comment) > 60 else obj.comment
    short_comment.short_description = "Comment Preview"
