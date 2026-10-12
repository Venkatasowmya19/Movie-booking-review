/**
 * CineSphere - General Interactive Features (Star Rating Picker, Auto-dismiss Alerts, Ticket Print)
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-dismiss Bootstrap alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 2. Interactive Star Rating selector for review forms
    const starPicker = document.getElementById('interactive-star-picker');
    const ratingSelect = document.getElementById('review_rating');

    if (starPicker && ratingSelect) {
        const stars = starPicker.querySelectorAll('.star-btn');

        function setVisualStars(rating) {
            stars.forEach(star => {
                const val = parseInt(star.dataset.value);
                if (val <= rating) {
                    star.classList.remove('bi-star');
                    star.classList.add('bi-star-fill', 'text-warning');
                } else {
                    star.classList.remove('bi-star-fill', 'text-warning');
                    star.classList.add('bi-star', 'text-secondary');
                }
            });
        }

        // Set initial state from select value
        setVisualStars(parseInt(ratingSelect.value || 5));

        // Click on star to update value
        stars.forEach(star => {
            star.addEventListener('click', function () {
                const selectedVal = parseInt(this.dataset.value);
                ratingSelect.value = selectedVal;
                setVisualStars(selectedVal);
            });

            // Hover preview
            star.addEventListener('mouseenter', function () {
                const hoverVal = parseInt(this.dataset.value);
                setVisualStars(hoverVal);
            });
        });

        starPicker.addEventListener('mouseleave', function () {
            setVisualStars(parseInt(ratingSelect.value || 5));
        });

        ratingSelect.addEventListener('change', function () {
            setVisualStars(parseInt(this.value));
        });
    }

    // 3. Print ticket functionality
    const printBtn = document.getElementById('btn-print-ticket');
    if (printBtn) {
        printBtn.addEventListener('click', function () {
            window.print();
        });
    }
});
