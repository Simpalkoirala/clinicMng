from django.contrib import admin
from .models import *
from django.utils.html import format_html


# Profile Admin
class MedicalInfoInline(admin.StackedInline):
    model = MedicalInfo
    can_delete = False
    verbose_name_plural = 'Medical Information'
    fk_name = 'profile'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user_username',
        'user_full_name',
        'role',
        'profile_image_tag',
        'ph_number',
        'gender',
        'is_active',
        'is_verified',
        'created_at',
        'updated_at',
        'blood_group_display',
    )
    list_filter = ('role', 'gender', 'is_active', 'is_verified', 'created_at')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name', 'ph_number', 'address',
        'medical_info__blood_group', 'medical_info__allergies', 'medical_info__medical_conditions'
    )
    readonly_fields = ('created_at', 'updated_at', 'profile_image_tag')
    fieldsets = (
        ('User & Role', {
            'fields': ('user', 'role')
        }),
        ('Personal Info', {
            'fields': ('profile_pic', 'profile_image_tag', 'ph_number', 'address', 'date_of_birth', 'gender')
        }),
        ('Token Info', {
            'fields': ('token', 'token_expiry', )
        }),
        ('Notifications', {
            'fields': ('email_notification', 'sms_notification', 'reminders')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'created_at', 'updated_at')
        }),
    )
    inlines = [MedicalInfoInline]

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'
    user_username.admin_order_field = 'user__username'

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_full_name.short_description = 'Full Name'

    def profile_image_tag(self, obj):
        if obj.profile_pic:
            return format_html('<img src="{}" style="height: 40px; width: 40px; border-radius: 5px;" />', obj.profile_pic.url)
        return "-"
    profile_image_tag.short_description = "Profile Picture"

    def blood_group_display(self, obj):
        if hasattr(obj, 'medical_info') and obj.medical_info.blood_group:
            return obj.medical_info.blood_group
        return "-"
    blood_group_display.short_description = "Blood Group"



# MedicalInfo separately as well (optional):
@admin.register(MedicalInfo)
class MedicalInfoAdmin(admin.ModelAdmin):
    list_display = (
        'profile',
        'blood_group',
        'allergies',
        'medical_conditions',
        'on_going_medications',
        'emg_contact_name',
        'emg_contact_number',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'profile__user__username', 'allergies', 'medical_conditions', 'on_going_medications', 'emg_contact_name'
    )
    readonly_fields = ('created_at', 'updated_at')


# ActivityLog Admin
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "profile_username",
        "action",
        "title",
        "short_description",
        "timestamp",
        "viewed",
        "get_target_display",
    )
    list_filter = ("action", "timestamp", "viewed", "profile__user__username")
    search_fields = (
        "profile__user__username",
        "action",
        "title",
        "description",
        "target_content_type__model",
    )
    readonly_fields = ("timestamp", "get_target_display")

    fieldsets = (
        (None, {
            "fields": ("profile", "action", "title", "description", "timestamp", "viewed")
        }),
        ("Target Object", {
            "fields": ("target_content_type", "target_object_id", "get_target_display"),
            "classes": ("collapse",)
        }),
    )

    def profile_username(self, obj):
        return obj.profile.user.username
    profile_username.short_description = "Username"
    profile_username.admin_order_field = "profile__user__username"

    def short_description(self, obj):
        return (obj.description[:40] + '...') if obj.description and len(obj.description) > 40 else obj.description
    short_description.short_description = "Description"

    def get_target_display(self, obj):
        if obj.target_content_type and obj.target_object_id:
            return f"{obj.target_content_type.model} - {obj.target}"
        return "No target"
    get_target_display.short_description = "Target"


# Conversation and Message Admin
class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    fields = ('sender', 'content', 'timestamp', 'read', 'message_type')
    readonly_fields = ['timestamp']
    verbose_name = "Message"
    verbose_name_plural = "Messages"


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    search_fields = ('participants__user__username', 'participants__user__first_name')
    readonly_fields = ('created_at',)
    inlines = [MessageInline]
    list_filter = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('participants','status', 'uuid'),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('participants')


class CallsAdmin(admin.ModelAdmin):
    list_display = ('id', 'caller', 'receiver', 'started_at', 'ended_at', 'status')
    search_fields = ('caller__user__username', 'receiver__user__username')
    readonly_fields = ('started_at', 'ended_at')
    list_filter = ('status', 'started_at')
    fieldsets = (
        (None, {
            'fields': ('caller', 'receiver', 'status', 'uuid'),
        }),
        ('Timestamps', {
            'fields': ('started_at', 'ended_at'),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('caller', 'receiver')


admin.site.register(Calls)



# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "profile_username",
        "doctor_username",
        "rating",
        "short_comment",
        "created_at",
        "updated_at",
    )
    list_filter = ("rating", "created_at", "updated_at")
    search_fields = (
        "profile__user__username",
        "doctor__profile__user__username",
        "comment",
    )
    readonly_fields = ("created_at", "updated_at")

    def profile_username(self, obj):
        return obj.profile.user.username
    profile_username.short_description = "Reviewer"

    def doctor_username(self, obj):
        if obj.doctor and obj.doctor.profile and obj.doctor.profile.user:
            return obj.doctor.profile.user.username
        return "-"
    doctor_username.short_description = "Doctor"

    def short_comment(self, obj):
        if obj.comment:
            return (obj.comment[:40] + '...') if len(obj.comment) > 40 else obj.comment
        return ""
    short_comment.short_description = "Comment"