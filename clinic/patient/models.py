from django.db import models

from django.contrib.auth.models import User
from mimetypes import guess_type

from account.models import Profile, MedicalInfo

from doctor.models import AppointmentTimeSlot, DoctorProfile
import uuid



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

    uuid = models.UUIDField(default=uuid.uuid4, editable=True)

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="patients_appointments")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, related_name="patients_appointments", blank=True, null=True)
    time_slot = models.ForeignKey(AppointmentTimeSlot, on_delete=models.SET_NULL, related_name="patients_appointments", blank=True, null=True)

    appointment_type = models.CharField(max_length=50, choices=APPOINTMENT_TYPES, default='general_consultation')
    appointment_date = models.DateField()
    appointment_time_str = models.CharField(max_length=50, blank=True)


    file = models.FileField(upload_to='appointment_files/', blank=True)
    reason = models.TextField(blank=True)


    STATUS_TYPE = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ]
    status = models.CharField(max_length=50,  choices=STATUS_TYPE, default='pending')

    cancled_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, related_name="cancelled_appointments", blank=True, null=True) 
    cancel_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f"{self.profile} - {self.appointment_date} - {self.appointment_time_str} - {self.status}"
    



class Medicine(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name               = models.CharField(max_length=255)
    generic_name       = models.CharField(max_length=255, blank=True)
    brand_name         = models.CharField(max_length=255, blank=True)
    manufacturer        = models.CharField(max_length=255, blank=True)
    description        = models.TextField(blank=True)


    default_dosage     = models.CharField(max_length=50, blank=True)
    default_frequency  = models.CharField(max_length=100, blank=True)
    instructions       = models.TextField(blank=True,
                                help_text="E.g. 'Take with food…'")
    side_effects = models.TextField(blank=True,
                                help_text="E.g. 'May cause dizziness…'")
    

    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Medicine'
        verbose_name_plural = 'Medicines'

    def __str__(self):
        return self.name



class Prescription(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="prescriptions")
    prescribing_doctor  = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="prescriptions")
    medicine            = models.ForeignKey(
                              Medicine,
                              on_delete=models.PROTECT,
                              related_name='prescriptions'
                          )

    update_dosage = models.CharField(
        max_length=50,
        help_text='e.g. "10mg", "500mg".'
    )
    update_frequency = models.CharField(
        max_length=100,
        help_text='Descriptive frequency, e.g. "Once daily", "Three times daily".'
    )

    notes = models.TextField(
        blank=True,
        help_text='Additional notes or instructions for the medication.'
    )


    STATUS_CHOICES = [
        ('active',    'Running'),
        ('completed', 'Completed'),
        ('discontinued', 'Discontinued'),
        ('break', 'In Break'),
    ]

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='active',
        help_text='Current status of the medication.')



    start_date = models.DateField(help_text='When the patient should start this medication.')
    end_date   = models.DateField(help_text='When the course ends or next review is due.')




    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f"{self.medicine.name} ({self.update_dosage}) for {self.profile.user.username}"



class PrescriptionSchedule(models.Model):
    """
    If you prefer a relational schedule rather than JSON/ArrayField,
    use this model instead of the above schedule field.
    """
    prescription = models.ForeignKey(
                       Prescription,
                       on_delete=models.CASCADE,
                       related_name='timeschedule'
                   )
    time         = models.TimeField()

    class Meta:
        unique_together = ('prescription', 'time')
        ordering = ['time']

    def __str__(self):
        return f"{self.prescription} @ {self.time}"