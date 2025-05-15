from django.contrib import admin

# Register your models here.


from .models import *

admin.site.register(Documents)
admin.site.register(Appointment)





# -------------------------  Prescription & Medicine section   -----------------

# 1. Inline schedule entries in the Prescription admin
class PrescriptionScheduleInline(admin.TabularInline):
    model = PrescriptionSchedule
    extra = 1
    readonly_fields = ()
    fields = ('time',)
    verbose_name = "Dose Time"
    verbose_name_plural = "Dose Schedule"

# 2. Prescription admin
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'profile',
        'prescribing_doctor',
        'medicine',
        'update_dosage',
        'update_frequency',
        'status',
        'start_date',
        'end_date',
    )
    list_filter = (
        'status',
        'prescribing_doctor',
        'medicine',
        'start_date',
        'end_date',
    )
    search_fields = (
        'profile__user__username',
        'prescribing_doctor__user__first_name',
        'prescribing_doctor__user__last_name',
        'medicine__name',
    )
    date_hierarchy = 'start_date'
    inlines = [PrescriptionScheduleInline]
    fieldsets = (
        (None, {
            'fields': (
                'profile',
                'prescribing_doctor',
                'medicine',
                ('update_dosage', 'update_frequency'),
                'status',
                ('start_date', 'end_date'),
                'notes',
            ),
        }),
    )

# 3. Medicine admin
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'generic_name',
        'brand_name',
        'manufacturer',
        'default_dosage',
        'default_frequency',
        'created_at',
    )
    search_fields = ('name', 'generic_name', 'brand_name', 'manufacturer')
    list_filter = ('manufacturer',)
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': (
                'uuid',
                'name',
                ('generic_name', 'brand_name'),
                'manufacturer',
                'description',
            ),
        }),
        ('Defaults & Instructions', {
            'fields': (
                ('default_dosage', 'default_frequency'),
                'instructions',
                'side_effects',
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )










# -------------------------  Lab Report section   -----------------

class LabReportParameterInline(admin.TabularInline):
    model = LabReportParameter
    extra = 1
    fields = ('parameter_name', 'result', 'reference_range', 'status')
    readonly_fields = ()
    # you can add show_change_link = True if you want clickable links to each parameter

@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'report_date', 'doctor', 'status')
    list_filter = ('status', 'report_type', 'report_date')
    search_fields = ('report_type', 'doctor', 'patient_profile')
    date_hierarchy = 'report_date'
    inlines = [LabReportParameterInline]
    fieldsets = (
        (None, {
            'fields': ('uuid' , 'report_type', 'report_date', 'doctor', 'status', 'report_description', 'patient_profile')
        }),
    )