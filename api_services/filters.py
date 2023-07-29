import django_filters
from api_services.models import Booking, Skill, Labour, LaboursAllocated


class SkillFilter(django_filters.FilterSet):
    class Meta:
        model = Skill
        fields = ['skill']


class BookingFilter(django_filters.FilterSet):
    class Meta:
        model = Booking
        fields = ['booking_id', 'contractor_email', 'labour_gender', 'start_date', 'end_date', 'status']


class LabourFilter(django_filters.FilterSet):
    class Meta:
        model = Labour
        fields = ['email', 'gender']


class LaboursAllocatedFilter(django_filters.FilterSet):
    class Meta:
        model = LaboursAllocated
        fields = ['allocation_id', 'booking_id', 'labour_email']