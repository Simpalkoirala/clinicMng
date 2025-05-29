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
            'fields': ('participants',),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('participants')
