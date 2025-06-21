from django.contrib import admin
from .models import *

admin.site.register(Profile)
admin.site.register(MedicalInfo)
admin.site.register(ActivityLog)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    fields = ('sender', 'content', 'timestamp', 'read')
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