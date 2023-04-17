import django_filters
from api_services.models import Booking, Labour


class LabourFilter(django_filters.FilterSet):
    class Meta:
        model = Labour
        fields = ['skill']


class BookingFilter(django_filters.FilterSet):
    class Meta:
        model = Booking
        fields = ['booking_id', 'contractor_email', 'date_of_booking']