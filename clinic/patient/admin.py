from django.contrib import admin

# Register your models here.


from .models import Documents, Appointment

admin.site.register(Documents)
admin.site.register(Appointment)
