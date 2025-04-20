from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User
from django.core.validators import RegexValidator



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


USER_ROLES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('admin', 'Admin'),
    )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=USER_ROLES, default='patient')

    # personal information
    profile_pic = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default.jpg')

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ph_number = models.CharField(validators=[phone_regex], max_length=16, blank=True) # validators should be a list
    address = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)


    email_notification = models.BooleanField(default=True)
    sms_notification = models.BooleanField(default=True)
    reminders = models.BooleanField(default=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username



class MedicalInfo(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="medical_info")
    blood_group = models.CharField(max_length=3, blank=True)
    allergies = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)
    on_going_medications = models.TextField(blank=True)


    # emergency contact
    emg_contact_name = models.CharField(max_length=255, blank=True)
    emg_contact_number = models.CharField(max_length=16, blank=True)
    emg_contact_relation = models.CharField(max_length=255, blank=True)
    emg_contact_address = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
  
    def __str__(self):
        return f"{self.profile.user.username}'s Medical Info"

