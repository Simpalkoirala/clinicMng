from django.contrib import admin

# Register your models here.
from .models import DoctorProfile, AppointmentTimeSlot, AppointmentDateSlot

# Doctor Profile Admin
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "doctor_name",
        "specialization",
        "experience_years",
        "license_number",
        "board_certified",
        "star_rating",
        "total_reviews",
        "fees",
        "accepts_new_patients",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "profile__user__username",
        "profile__user__first_name",
        "profile__user__last_name",
        "specialization",
        "license_number",
        "qualifications",
        "languages_spoken",
        "slug",
    )
    list_filter = (
        "specialization",
        "board_certified",
        "accepts_new_patients",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at", "slug")
    fieldsets = (
        ("Profile Link", {
            "fields": ("profile",)
        }),
        ("Professional Information", {
            "fields": (
                "specialization",
                "qualifications",
                "experience_years",
                "license_number",
                "board_certified",
                "languages_spoken",
            )
        }),
        ("Reviews & Ratings", {
            "fields": (
                "star_rating",
                "total_reviews",
            )
        }),
        ("Practice Info", {
            "fields": (
                "fees",
                "accepts_new_patients",
                "slug",
            )
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    def doctor_name(self, obj):
        return f"{obj.profile.user.first_name} {obj.profile.user.last_name}"
    doctor_name.short_description = "Doctor Name"
    doctor_name.admin_order_field = "profile__user__first_name"





class AppointmentTimeSlotInline(admin.TabularInline):
    model = AppointmentTimeSlot
    extra = 1
    fields = ('unique_id','from_time', 'to_time', 'duration', 'appointment_type', 'status')
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

