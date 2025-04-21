from django.db import models
from django.contrib.auth.models import User
from mimetypes import guess_type

from account.models import Profile, MedicalInfo

from doctor.models import AppointmentTimeSlot, DoctorProfile



class Documents(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="patients_documents")
    nick_name = models.CharField(max_length=255, blank=True)
    doc_type = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank= True)
    from_our_clinic = models.BooleanField(default=False)

    file = models.FileField(upload_to='patients_documents/', blank=True)


    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f"{self.nick_name}"
    
    def is_image(self):
        mime_type, _ = guess_type(self.file.url)
        return mime_type and mime_type.startswith('image')
    
    def is_pdf(self):
        mime_type, _ = guess_type(self.file.url)
        return mime_type == 'application/pdf'
    


class Appointment(models.Model):
    APPOINTMENT_TYPES =  [
        ('general_consultation', 'General Consultation'),
        ('follow_up_visit', 'Follow-up Visit'),
        ('online_consultation', 'Online Consultation'),
        ('offline_consultation', 'Offline Consultation'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="patients_appointments")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, related_name="patients_appointments", blank=True, null=True)
    time_slot = models.ForeignKey(AppointmentTimeSlot, on_delete=models.SET_NULL, related_name="patients_appointments", blank=True, null=True)

    appointment_type = models.CharField(max_length=50, choices=APPOINTMENT_TYPES, default='general_consultation')
    appointment_date = models.DateField()
    appointment_time_str = models.CharField(max_length=50, blank=True)


    file = models.FileField(upload_to='appointment_files/', blank=True)
    reason = models.TextField(blank=True)


    STATUS_TYPE = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'),( 'completed', 'Completed')]

    status = models.CharField(max_length=50, default='pending', choices=STATUS_TYPE)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f"{self.profile} - {self.appointment_date} - {self.appointment_time_str}"