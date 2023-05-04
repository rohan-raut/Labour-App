import django_filters
from api_services.models import Booking, Skill


class SkillFilter(django_filters.FilterSet):
    class Meta:
        model = Skill
        fields = ['skill']


class BookingFilter(django_filters.FilterSet):
    class Meta:
        model = Booking
        fields = ['booking_id', 'contractor_email', 'start_date', 'end_date', 'status']