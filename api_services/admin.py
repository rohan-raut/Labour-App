from django.contrib import admin
from api_services.models import Account, Skill, Labour, Booking, Payment, LaboursAllocated, PublicHoliday, Notification

# Register your models here.

admin.site.register(Account)
admin.site.register(Skill)
# admin.site.register(Labour)
# admin.site.register(Booking)
# admin.site.register(Payment)
# admin.site.register(LaboursAllocated)
admin.site.register(PublicHoliday)
admin.site.register(Notification)
