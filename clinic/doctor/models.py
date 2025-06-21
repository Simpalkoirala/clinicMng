from django.db import models
from django.utils.text import slugify
from account.models import Profile
from multiselectfield import MultiSelectField


class DoctorProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='doctor_profile')

    SPECIALIZATIONS = [
        ('general_medicine', 'General Medicine'),
        ('cardiology', 'Cardiology'),
        ('dermatology', 'Dermatology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('psychiatry', 'Psychiatry'),
        ('radiology', 'Radiology'),
        ('surgery', 'Surgery'),
        ('other', 'Other'),
    ]

   

    specialization = models.CharField(max_length=100, choices=SPECIALIZATIONS)

    qualifications = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField()
    license_number = models.CharField(max_length=100, blank=True)
    board_certified = models.BooleanField(default=False)
    languages_spoken = models.JSONField(blank=True, null=True)

    #rating & reviews
    star_rating = models.FloatField(null=True, blank=True, default=3)
    total_reviews =  models.IntegerField(null=True)



    fees = models.DecimalField(max_digits=10, decimal_places=2)
    accepts_new_patients = models.BooleanField(default=True)


    slug = models.SlugField(unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            full_name = f"{self.profile.user.first_name}-{self.specialization}"
            self.slug = slugify(full_name)
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Dr. {self.profile.user.first_name} ({self.specialization})"
    


class AppointmentDateSlot(models.Model):
    doctor = models.ForeignKey( DoctorProfile, on_delete=models.CASCADE, related_name='datetime_slots'
    )
  
    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.doctor} – @ {self.date}"



class AppointmentTimeSlot(models.Model):

    unique_id = models.CharField(max_length=100, unique=True, blank=True, null=True)

    appointment_date_slot = models.ForeignKey(AppointmentDateSlot, on_delete=models.CASCADE, related_name='appointment_times')
    from_time = models.TimeField()
    to_time = models.TimeField()

    durations = [
        ('15', '15 minutes'),
        ('30', '30 minutes'),
        ('45', '45 minutes'),
        ('60', '60 minutes'),
    ]
    duration = models.CharField(max_length=3, choices=durations, default='60')

    APPOINTMENT_TYPES =  [
        ('general_consultation', 'General Consultation'),
        ('follow_up_visit', 'Follow-up Visit'),
        ('online_consultation', 'Online Consultation'),
        ('offline_consultation', 'Offline Consultation'),
    ]
    appointment_type = MultiSelectField(choices=APPOINTMENT_TYPES, max_length=100, blank=True, null=True)
    # is_booked = models.BooleanField(default=False)

    status = models.CharField(max_length=20, default='available', choices=[
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('unavailable', 'Unavailable'),
        ('break', 'Break'),
    ])

    def save(self, *args, **kwargs):
        # if not self.unique_id:
        self.unique_id = f"{self.pk}--{self.appointment_date_slot.id}-{self.from_time.strftime('%H:%M')}-{self.to_time.strftime('%H:%M')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.appointment_date_slot} – {self.from_time}--{self.to_time}"