from django.contrib import admin

# Register your models here.
from .models import DoctorProfile, AppointmentTimeSlot, AppointmentDateSlot

admin.site.register(DoctorProfile)




class AppointmentTimeSlotInline(admin.TabularInline):
    model = AppointmentTimeSlot
    extra = 1
    fields = ('from_time', 'to_time', 'duration', 'appointment_type', 'is_booked')
    readonly_fields = ()
    verbose_name = "Time Slot"
    verbose_name_plural = "Time Slots"

@admin.register(AppointmentDateSlot)
class AppointmentDateSlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'date', 'created_at', 'updated_at')
    list_filter = ('doctor', 'date', 'created_at')
    search_fields = (
        'doctor__user__first_name',
        'doctor__user__last_name',
        'date',
    )
    date_hierarchy = 'date'
    inlines = [AppointmentTimeSlotInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('doctor', 'date'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

