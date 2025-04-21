from django.contrib import admin

# Register your models here.
from .models import DoctorProfile, AppointmentTimeSlot, AppointmentDateSlot

admin.site.register(DoctorProfile)
admin.site.register(AppointmentDateSlot)
admin.site.register(AppointmentTimeSlot)