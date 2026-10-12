import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Avg, Count
from django.utils import timezone

from .models import Movie, Showtime, SeatBooking, MovieReview
from .forms import SeatBookingForm, MovieReviewForm


def home_view(request):
    """
    Cinema-themed home page displaying hero banner, now showing movies,
    search & genre filtering, and cinema statistics.
    """
    query = request.GET.get('q', '').strip()
    selected_genre = request.GET.get('genre', '').strip()

    movies = Movie.objects.annotate(
        computed_rating=Avg('reviews__rating'),
        num_reviews=Count('reviews')
    ).order_by('-release_date')

    if query:
        movies = movies.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(genre__icontains=query)
        )

    if selected_genre and selected_genre.lower() != 'all':
        movies = movies.filter(genre__iexact=selected_genre)

    # Distinct genres available in database
    all_genres = Movie.objects.values_list('genre', flat=True).distinct()
    unique_genres = sorted(list(set(g.strip() for g in all_genres if g.strip())))

    # Featured Movie for Hero Banner
    hero_movie = movies.first() if movies.exists() else None

    # Overall Cinema Portal stats
    total_movies = Movie.objects.count()
    total_showtimes = Showtime.objects.count()
    total_reviews = MovieReview.objects.count()

    # Recent Community Reviews
    recent_reviews = MovieReview.objects.select_related('movie').order_by('-created_date')[:4]

    context = {
        'movies': movies,
        'hero_movie': hero_movie,
        'genres': unique_genres,
        'selected_genre': selected_genre or 'all',
        'query': query,
        'total_movies': total_movies,
        'total_showtimes': total_showtimes,
        'total_reviews': total_reviews,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'movies/home.html', context)


def movie_list_view(request):
    """
    Browse all movies with filtering, search, and sorting options.
    """
    query = request.GET.get('q', '').strip()
    genre = request.GET.get('genre', '').strip()
    sort = request.GET.get('sort', 'latest')

    movies = Movie.objects.annotate(
        computed_rating=Avg('reviews__rating'),
        num_reviews=Count('reviews')
    )

    if query:
        movies = movies.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(genre__icontains=query)
        )

    if genre and genre.lower() != 'all':
        movies = movies.filter(genre__iexact=genre)

    if sort == 'rating':
        movies = movies.order_by('-computed_rating', '-release_date')
    elif sort == 'title':
        movies = movies.order_by('title')
    else:  # default: latest
        movies = movies.order_by('-release_date')

    all_genres = sorted(list(set(Movie.objects.values_list('genre', flat=True).distinct())))

    context = {
        'movies': movies,
        'query': query,
        'selected_genre': genre or 'all',
        'genres': all_genres,
        'sort': sort,
    }
    return render(request, 'movies/movie_list.html', context)


def movie_detail_view(request, pk):
    """
    Detailed movie page displaying synopsis, duration, ratings,
    available showtimes grouped by date, and community reviews with review submission.
    """
    movie = get_object_or_404(
        Movie.objects.annotate(
            computed_rating=Avg('reviews__rating'),
            num_reviews=Count('reviews')
        ),
        pk=pk
    )

    # Showtimes for this movie
    showtimes = movie.showtimes.all().order_by('show_date', 'show_time')

    # Group showtimes by show_date
    showtimes_by_date = {}
    for st in showtimes:
        date_key = st.show_date
        if date_key not in showtimes_by_date:
            showtimes_by_date[date_key] = []
        showtimes_by_date[date_key].append(st)

    reviews = movie.reviews.all().order_by('-created_date')

    # Handle review submission directly on movie detail page
    if request.method == 'POST' and 'submit_review' in request.POST:
        review_form = MovieReviewForm(request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.movie = movie
            new_review.save()
            messages.success(request, "Thank you! Your movie review has been posted successfully.")
            return redirect('movie_detail', pk=movie.pk)
        else:
            messages.error(request, "Please check your review submission for errors.")
    else:
        review_form = MovieReviewForm()

    context = {
        'movie': movie,
        'showtimes_by_date': showtimes_by_date,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'movies/movie_detail.html', context)


def seat_booking_view(request, showtime_id):
    """
    Interactive 5x8 seat selection page and booking processor.
    Renders rows A-E and columns 1-8, checks booked seats,
    calculates prices, validates customer info, and handles reservations safely.
    """
    showtime = get_object_or_404(
        Showtime.objects.select_related('movie'),
        pk=showtime_id
    )
    booked_seats = showtime.get_booked_seats()

    # Define 5x8 grid rows & columns
    rows = ['A', 'B', 'C', 'D', 'E']
    columns = [1, 2, 3, 4, 5, 6, 7, 8]

    # Generate grid seat structure for template rendering
    grid = []
    for r in rows:
        row_seats = []
        for c in columns:
            seat_code = f"{r}{c}"
            row_seats.append({
                'code': seat_code,
                'is_booked': seat_code in booked_seats,
            })
        grid.append({'row_name': r, 'seats': row_seats})

    if request.method == 'POST':
        form = SeatBookingForm(request.POST)
        if form.is_valid():
            selected_seats_str = form.cleaned_data['selected_seats']
            seat_list = [s.strip().upper() for s in selected_seats_str.split(',') if s.strip()]

            with transaction.atomic():
                # Re-fetch latest booked seats inside transaction to prevent race conditions
                current_booked_seats = showtime.get_booked_seats()
                conflicts = [seat for seat in seat_list if seat in current_booked_seats]

                if conflicts:
                    conflict_str = ", ".join(conflicts)
                    messages.error(
                        request,
                        f"Seat(s) {conflict_str} were just booked by another customer. Please pick available seats."
                    )
                else:
                    seat_count = len(seat_list)
                    total_paid = Decimal(seat_count) * showtime.ticket_price

                    booking = form.save(commit=False)
                    booking.showtime = showtime
                    booking.seat_count = seat_count
                    booking.total_paid = total_paid
                    booking.save()

                    messages.success(
                        request,
                        f"Booking confirmed! Your seats ({', '.join(seat_list)}) have been reserved."
                    )
                    return redirect('booking_confirmation', reference=booking.booking_reference)
        else:
            messages.error(request, "Please correct the errors in the booking form.")
    else:
        form = SeatBookingForm()

    context = {
        'showtime': showtime,
        'grid': grid,
        'rows': rows,
        'columns': columns,
        'booked_seats_json': json.dumps(list(booked_seats)),
        'form': form,
        'ticket_price': float(showtime.ticket_price),
    }
    return render(request, 'movies/seat_booking.html', context)


def booking_confirmation_view(request, reference):
    """
    Displays the confirmation page and cinema e-ticket receipt for a confirmed booking.
    """
    booking = get_object_or_404(
        SeatBooking.objects.select_related('showtime__movie'),
        booking_reference=reference
    )
    context = {
        'booking': booking,
        'showtime': booking.showtime,
        'movie': booking.showtime.movie,
        'seats': booking.get_seats_list(),
    }
    return render(request, 'movies/booking_confirmation.html', context)


def reviews_view(request):
    """
    Community review hub displaying reviews across all movies with movie filtering.
    """
    movie_id = request.GET.get('movie')
    reviews = MovieReview.objects.select_related('movie').order_by('-created_date')

    if movie_id:
        reviews = reviews.filter(movie_id=movie_id)

    movies = Movie.objects.all().order_by('title')

    context = {
        'reviews': reviews,
        'movies': movies,
        'selected_movie': int(movie_id) if movie_id and movie_id.isdigit() else None,
    }
    return render(request, 'movies/reviews.html', context)


def add_review_view(request, movie_id=None):
    """
    Dedicated view for submitting a new movie review.
    """
    movie = None
    if movie_id:
        movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        selected_movie_id = request.POST.get('movie_id') or movie_id
        target_movie = get_object_or_404(Movie, pk=selected_movie_id)

        if form.is_valid():
            review = form.save(commit=False)
            review.movie = target_movie
            review.save()
            messages.success(request, f"Your review for '{target_movie.title}' was submitted successfully!")
            return redirect('movie_detail', pk=target_movie.pk)
        else:
            messages.error(request, "Failed to submit review. Please check the form fields.")
    else:
        form = MovieReviewForm()

    all_movies = Movie.objects.all().order_by('title')
    context = {
        'form': form,
        'movie': movie,
        'all_movies': all_movies,
    }
    return render(request, 'movies/add_review.html', context)
