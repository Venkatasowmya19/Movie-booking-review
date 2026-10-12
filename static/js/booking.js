/**
 * CineSphere - Interactive 5x8 Seat Selection & Real-Time Price Calculation
 */

document.addEventListener('DOMContentLoaded', function () {
    const seatGrid = document.getElementById('seat-grid');
    if (!seatGrid) return;

    // Configuration from DOM dataset
    const ticketPrice = parseFloat(seatGrid.dataset.ticketPrice || 0);
    const hiddenSeatsInput = document.getElementById('id_selected_seats');
    const selectedBadgeContainer = document.getElementById('selected-seats-badges');
    const seatCountDisplay = document.getElementById('selected-seats-count');
    const totalPriceDisplay = document.getElementById('total-price-display');
    const bookButton = document.getElementById('btn-confirm-booking');
    const bookingForm = document.getElementById('booking-form');

    // Selected seat set
    const selectedSeats = new Set();

    // Attach click handlers to all seat elements
    const seats = seatGrid.querySelectorAll('.cinema-seat');
    seats.forEach(seat => {
        seat.addEventListener('click', function () {
            // Ignore already-booked seats
            if (this.classList.contains('seat-booked')) {
                return;
            }

            const seatCode = this.dataset.seat;
            if (!seatCode) return;

            if (selectedSeats.has(seatCode)) {
                // Deselect seat
                selectedSeats.delete(seatCode);
                this.classList.remove('seat-selected');
                this.setAttribute('aria-checked', 'false');
            } else {
                // Select seat
                selectedSeats.add(seatCode);
                this.classList.add('seat-selected');
                this.setAttribute('aria-checked', 'true');
            }

            updateBookingState();
        });
    });

    /**
     * Updates the summary sidebar, input field, and total price
     */
    function updateBookingState() {
        const sortedSeats = Array.from(selectedSeats).sort();
        const count = sortedSeats.length;
        const total = (count * ticketPrice).toFixed(2);

        // Update hidden form input for Django POST submission
        if (hiddenSeatsInput) {
            hiddenSeatsInput.value = sortedSeats.join(', ');
        }

        // Update seat count display
        if (seatCountDisplay) {
            seatCountDisplay.textContent = count;
        }

        // Update total price display
        if (totalPriceDisplay) {
            totalPriceDisplay.textContent = `$${total}`;
        }

        // Update selected seats pills container
        if (selectedBadgeContainer) {
            if (count === 0) {
                selectedBadgeContainer.innerHTML = '<span class="text-secondary small fst-italic">No seats selected yet. Click available seats on the map.</span>';
            } else {
                selectedBadgeContainer.innerHTML = sortedSeats
                    .map(seat => `<span class="seat-pill"><i class="bi bi-ticket-perforated-fill me-1"></i>${seat}</span>`)
                    .join(' ');
            }
        }

        // Toggle confirm booking button
        if (bookButton) {
            bookButton.disabled = count === 0;
            if (count > 0) {
                bookButton.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i>Book ${count} Seat${count > 1 ? 's' : ''} ($${total})`;
            } else {
                bookButton.innerHTML = `<i class="bi bi-hand-index-thumb me-2"></i>Select Seats to Proceed`;
            }
        }
    }

    // Client-side form submission safety check
    if (bookingForm) {
        bookingForm.addEventListener('submit', function (e) {
            if (selectedSeats.size === 0) {
                e.preventDefault();
                alert('Please select at least one seat on the cinema grid before submitting.');
                return false;
            }
        });
    }

    // Initialize state on page load
    updateBookingState();
});
