from django.urls import path
from api_services.views import registration_view, user_info, skill_list, labour_list, booking_view
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('register', registration_view, name="registration_view"),
    path('login', obtain_auth_token, name="login"),
    path('user-info', user_info, name="user_info"),
    path('skill-list', skill_list, name="skill_list"),
    path('labour-list', labour_list, name="labour_list"),
    path('booking', booking_view, name="booking_view"),
]
