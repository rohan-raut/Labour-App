from django.urls import path
from api_services.views import registration_view, user_info, skill_list, labour_list, booking_view, update_user_info, update_skill_list, update_labour_list, update_booking_view, delete_booking_view, delete_labour_list, delete_skill_list, change_password_view, send_email_view, verify_user_view, labour_allocation_view, public_holidays_view, forgot_password_view, reset_password_view, report_view, login_view, booking_preview
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('register', registration_view, name="registration_view"),
    path('verify-user/<str:pk>', verify_user_view, name="verify_user_view"),
    path('login', login_view, name="login_view"),
    path('forgot-password', forgot_password_view, name="forgot_password_view"),
    path('reset-password/<str:pk>', reset_password_view, name="reset_password_view"),
    path('user-info', user_info, name="user_info"),
    path('skill-list', skill_list, name="skill_list"),
    path('labour-list', labour_list, name="labour_list"),
    path('get-booking-preview', booking_preview, name="booking_preview"),
    path('booking', booking_view, name="booking_view"),
    path('public-holidays', public_holidays_view, name="public_holidays_view"),
    path('allocate-labour', labour_allocation_view, name="labour_allocation_view"),
    path('send-email', send_email_view, name="send_email_view"),
    path('change-password', change_password_view, name="change_password_view"),
    path('report', report_view, name="report_view"),
    path('update/user-info/<str:pk>', update_user_info, name="update_user_info"),
    path('update/skill-list/<str:pk>', update_skill_list, name="update_skill_list"),
    path('update/labour-list/<str:pk>', update_labour_list, name="update_labour_list"),
    path('update/booking/<int:pk>', update_booking_view, name="update_booking_view"),
    path('delete/skill-list/<str:pk>', delete_skill_list, name="delete_skill_list"),
    path('delete/labour-list/<str:pk>', delete_labour_list, name="delete_labour_list"),
    path('delete/booking/<int:pk>', delete_booking_view, name="delete_booking_view"),
]
