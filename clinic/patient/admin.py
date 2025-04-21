from django.contrib import admin

# Register your models here.


from .models import *

admin.site.register(Documents)
admin.site.register(Appointment)

admin.site.register(Medicine)
admin.site.register(Prescription)
admin.site.register(PrescriptionSchedule)
