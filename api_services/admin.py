from django.contrib import admin
from api_services.models import Account, Labour, Booking, Payment

# Register your models here.

admin.site.register(Account)
admin.site.register(Labour)
admin.site.register(Booking)
admin.site.register(Payment)
