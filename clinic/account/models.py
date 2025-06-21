from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
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

    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True)

    email_notification = models.BooleanField(default=True)
    sms_notification = models.BooleanField(default=True)
    reminders = models.BooleanField(default=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} -- {self.role} -- {self.user.first_name}" 


    




class Conversation(models.Model):
    participants = models.ManyToManyField(Profile, related_name='conversations')
    uuid = models.UUIDField(unique=True, editable=True, null=True, blank=True)

    status_choices = (
        ('initiated', 'Initiated'),
        ('active', 'Active'),
        ('requested', 'Requested'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )

    conv_type_choices = (
        ('audio', 'Audio'),
        ('video', 'Video'),
    )
    
    status = models.CharField(max_length=10, choices=status_choices, default='requested')
    conv_type = models.CharField(max_length=10, choices=conv_type_choices, default='audio')

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Conv Participants: {', '.join([p.user.username for p in self.participants.all()])}"


class Calls(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, null=True, blank=True)

    appointment = models.ForeignKey('patient.Appointment', on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    connection = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='convosation_calls')
    caller = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='calls_made')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='calls_received')

    last_req = models.DateTimeField(null=True, blank=True)

    status_choices = (
        ('requested', 'Requested'),
        ('active', 'Active'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    status = models.CharField(max_length=10, choices=status_choices, default='requested')

    def __str__(self):
        return f"Call {self.pk} - Caller: {self.caller.user.username} - Receiver: {self.receiver.user.username}"



class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender       = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_messages')
    content      = models.TextField()
    file        = models.FileField(upload_to='conversation_files/', blank=True, null=True)  
    timestamp    = models.DateTimeField(auto_now_add=True)
    read         = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Msg {self.pk} in Conv {self.conversation_id}"





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
    

class ActivityLog(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="activity_logs")

    action = models.CharField(max_length=50)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    viewed = models.BooleanField(default=False)
    
    

    # optional link to any object
    target_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey("target_content_type", "target_object_id")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.profile.user.username} - {self.action} - {self.timestamp}"
    def get_action_display(self):
        return dict(USER_ROLES).get(self.action, self.action)
    def get_target_display(self):
        if self.target_content_type:
            return f"{self.target_content_type.model} - {self.target}"
        return "No target"