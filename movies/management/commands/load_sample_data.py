from datetime import time, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from movies.models import Movie, Showtime, SeatBooking, MovieReview


class Command(BaseCommand):
    help = 'Populates the database with realistic sample movies, showtimes, reviews, and bookings.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Clearing existing cinema data...'))
        SeatBooking.objects.all().delete()
        MovieReview.objects.all().delete()
        Showtime.objects.all().delete()
        Movie.objects.all().delete()

        today = timezone.now().date()

        self.stdout.write(self.style.NOTICE('Creating sample movies...'))

        movies_data = [
            {
                'title': 'Starlight Odyssey: Beyond the Nebula',
                'genre': 'Sci-Fi',
                'duration': 148,
                'release_date': today - timedelta(days=14),
                'poster_url': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80',
                'description': 'When a cosmic distortion threatens gravitational equilibrium across the solar system, Captain Elena Vance leads a deep-space reconnaissance crew through an uncharted nebula to find an ancient artificial construct capable of restoring harmony.'
            },
            {
                'title': 'Shadows of Neo-Tokyo',
                'genre': 'Action',
                'duration': 132,
                'release_date': today - timedelta(days=7),
                'poster_url': 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=800&q=80',
                'description': 'In a rain-drenched cyberpunk metropolis governed by sentient algorithms, an ex-detective turned cybernetic operative uncovers an underground syndicate orchestrating a total blackout to reset societal hierarchy.'
            },
            {
                'title': 'Whispers of the Emerald Vale',
                'genre': 'Animation',
                'duration': 105,
                'release_date': today - timedelta(days=21),
                'poster_url': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=800&q=80',
                'description': 'A spirited young forest sprite and a clockwork companion embark on a heartwarming pilgrimage to reignite the Great Canopy Tree before the frost spirits permanently freeze their sacred valley.'
            },
            {
                'title': 'The Quantum Cipher',
                'genre': 'Thriller',
                'duration': 122,
                'release_date': today - timedelta(days=3),
                'poster_url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80',
                'description': 'A reclusive mathematician deciphering encrypted radio signals discovers an anomaly predicting global market crashes seconds before they materialize, turning her into the target of high-stakes intelligence agencies.'
            },
            {
                'title': 'Symphony in the Rain',
                'genre': 'Drama',
                'duration': 118,
                'release_date': today - timedelta(days=30),
                'poster_url': 'https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=800&q=80',
                'description': 'An aging jazz pianist and an ambitious street violinist form an unexpected mentorship across the bohemian cafes of Paris, transforming personal tragedies into a timeless musical opus.'
            },
            {
                'title': 'Kingdom of Sands: The Djinn Crown',
                'genre': 'Fantasy',
                'duration': 140,
                'release_date': today - timedelta(days=2),
                'poster_url': 'https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=800&q=80',
                'description': 'Centuries after the Great Djinn Wars, an exiled nomad warrior must navigate shifting dunes, forgotten ruins, and mystical beasts to protect the last incandescent crown of the desert monarchs.'
            },
        ]

        created_movies = []
        for m_data in movies_data:
            movie = Movie.objects.create(**m_data)
            created_movies.append(movie)

        self.stdout.write(self.style.NOTICE('Creating showtimes for today and upcoming dates...'))

        screens = ['Screen 1 (IMAX 70mm)', 'Screen 2 (Dolby Cinema)', 'Screen 3 (Laser 4K)']
        times_schedule = [
            (time(13, 0), Decimal('14.50')),
            (time(16, 30), Decimal('16.00')),
            (time(19, 45), Decimal('18.50')),
            (time(22, 15), Decimal('15.00')),
        ]

        created_showtimes = []
        for day_offset in range(4):
            show_date = today + timedelta(days=day_offset)
            for idx, movie in enumerate(created_movies):
                # Pick a screen and 2 times per day for each movie
                screen = screens[idx % len(screens)]
                st_time_1, price_1 = times_schedule[idx % len(times_schedule)]
                st_time_2, price_2 = times_schedule[(idx + 2) % len(times_schedule)]

                st1 = Showtime.objects.create(
                    movie=movie,
                    show_date=show_date,
                    show_time=st_time_1,
                    ticket_price=price_1,
                    screen_number=screen
                )
                st2 = Showtime.objects.create(
                    movie=movie,
                    show_date=show_date,
                    show_time=st_time_2,
                    ticket_price=price_2,
                    screen_number=screen
                )
                created_showtimes.extend([st1, st2])

        self.stdout.write(self.style.NOTICE('Creating community reviews...'))

        sample_reviews = [
            (created_movies[0], 'Aria Chen', 5, 'Visually breathtaking! The interstellar sequences in IMAX were unlike anything I have experienced this decade. Outstanding score by the London Philharmonic.'),
            (created_movies[0], 'Marcus Vance', 4, 'Intriguing scientific premises combined with emotional weight. Pacing dragged slightly in the second act, but the climax blew me away.'),
            (created_movies[1], 'Kenji Sato', 5, 'A visceral cyberpunk tour de force. The neon lighting design, synth soundtrack, and kinetic fight choreography are top tier.'),
            (created_movies[1], 'Sarah Jenkins', 4, 'Stylish neo-noir atmosphere with deep world-building. Loved the complex morality of the protagonist.'),
            (created_movies[2], 'David Morales', 5, 'My whole family was spellbound! The hand-painted art style and emotional depth rival Studio Ghibli at its best.'),
            (created_movies[2], 'Chloe Bennett', 4, 'A charming and poetic tale. Beautiful soundtrack and lovable sidekick.'),
            (created_movies[3], 'Dr. Aris Thorne', 5, 'Electrifying cat-and-mouse thriller. The mathematical clues were surprisingly grounded and the tension never lets up for 2 hours.'),
            (created_movies[4], 'Sophie Laurent', 5, 'Heart-wrenching, authentic, and sublime. The musical performances gave me goosebumps from start to finish.'),
            (created_movies[5], 'Rami Al-Mansoor', 4, 'Grand epic fantasy with dazzling visual effects and a commanding lead performance. Can’t wait for the sequel!'),
        ]

        for movie, reviewer, rating, comment in sample_reviews:
            MovieReview.objects.create(
                movie=movie,
                reviewer_name=reviewer,
                rating=rating,
                comment=comment
            )

        self.stdout.write(self.style.NOTICE('Creating sample seat bookings...'))

        # Add sample booked seats to first couple of showtimes to demonstrate 5x8 grid occupied seats
        if created_showtimes:
            # Booking 1 for today's premiere show
            st_prime = created_showtimes[0]
            SeatBooking.objects.create(
                showtime=st_prime,
                customer_name='Alex Reynolds',
                customer_email='alex.reynolds@example.com',
                customer_phone='+1 (555) 349-8120',
                selected_seats='C4, C5',
                seat_count=2,
                total_paid=st_prime.ticket_price * 2
            )

            # Booking 2
            SeatBooking.objects.create(
                showtime=st_prime,
                customer_name='Jordan Lee',
                customer_email='jordan.lee@example.com',
                customer_phone='+1 (555) 782-9901',
                selected_seats='A1, A2',
                seat_count=2,
                total_paid=st_prime.ticket_price * 2
            )

            # Booking on second showtime
            if len(created_showtimes) > 1:
                st_second = created_showtimes[1]
                SeatBooking.objects.create(
                    showtime=st_second,
                    customer_name='Elena Rostova',
                    customer_email='elena.rostova@example.com',
                    customer_phone='+1 (555) 431-7729',
                    selected_seats='D3, D4, D5',
                    seat_count=3,
                    total_paid=st_second.ticket_price * 3
                )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully loaded {len(created_movies)} movies, {len(created_showtimes)} showtimes, '
            f'{len(sample_reviews)} reviews, and 3 sample bookings.'
        ))
