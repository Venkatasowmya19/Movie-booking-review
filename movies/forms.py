import re
from django import forms
from .models import SeatBooking, MovieReview


VALID_SEAT_REGEX = re.compile(r'^[A-E][1-8]$')


class SeatBookingForm(forms.ModelForm):
    """
    Form for validating customer contact information and selected cinema seats.
    """
    selected_seats = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'id_selected_seats'}),
        error_messages={'required': 'Please select at least one seat on the cinema grid.'}
    )

    class Meta:
        model = SeatBooking
        fields = ['customer_name', 'customer_email', 'customer_phone', 'selected_seats']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. John Doe',
                'required': True,
                'id': 'customer_name',
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. john@example.com',
                'required': True,
                'id': 'customer_email',
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. +1 (555) 234-5678',
                'required': True,
                'id': 'customer_phone',
            }),
        }

    def clean_selected_seats(self):
        seats_raw = self.cleaned_data.get('selected_seats', '').strip()
        if not seats_raw:
            raise forms.ValidationError("Please select at least one seat before confirming your booking.")

        seat_list = [s.strip().upper() for s in seats_raw.split(',') if s.strip()]
        if not seat_list:
            raise forms.ValidationError("Invalid seat selection. Please choose seats from rows A-E and columns 1-8.")

        # Ensure no duplicate seats in submission
        if len(seat_list) != len(set(seat_list)):
            raise forms.ValidationError("Duplicate seat numbers were detected in your selection.")

        # Validate each seat matches 5x8 grid (Rows A-E, Cols 1-8)
        for seat in seat_list:
            if not VALID_SEAT_REGEX.match(seat):
                raise forms.ValidationError(f"Invalid seat code '{seat}'. Seats must be between A1 and E8.")

        return ','.join(seat_list)


class MovieReviewForm(forms.ModelForm):
    """
    Form for submitting movie ratings and community reviews.
    """
    rating = forms.ChoiceField(
        choices=[
            (5, '★★★★★ (5 - Masterpiece)'),
            (4, '★★★★☆ (4 - Great)'),
            (3, '★★★☆☆ (3 - Good)'),
            (2, '★★☆☆☆ (2 - Fair)'),
            (1, '★☆☆☆☆ (1 - Poor)'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'review_rating',
        }),
        initial=5,
    )

    class Meta:
        model = MovieReview
        fields = ['reviewer_name', 'rating', 'comment']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name or Cinephile Handle',
                'required': True,
                'id': 'reviewer_name',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts on the movie, direction, acting, visuals, or sound...',
                'rows': 4,
                'required': True,
                'id': 'review_comment',
            }),
        }
