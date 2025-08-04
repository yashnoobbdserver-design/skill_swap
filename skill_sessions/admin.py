from django.contrib import admin
from .models import SkillSwapRequest, SkillSwapSession, SessionReview, SessionReminder

@admin.register(SkillSwapRequest)
class SkillSwapRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'recipient', 'offered_skill', 'status', 
                   'proposed_duration', 'proposed_format', 'created_at', 'expires_at')
    list_filter = ('status', 'proposed_format', 'created_at', 'expires_at')
    search_fields = ('requester__username', 'recipient__username', 
                    'offered_skill__skill__name', 'message')
    readonly_fields = ('created_at', 'updated_at', 'responded_at')
    
    fieldsets = (
        ('Request Details', {
            'fields': ('requester', 'recipient', 'offered_skill', 'desired_skill', 'status')
        }),
        ('Proposed Session', {
            'fields': ('proposed_duration', 'proposed_format', 'proposed_location')
        }),
        ('Messages', {
            'fields': ('message', 'response_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'expires_at', 'responded_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_expired']
    
    def mark_as_expired(self, request, queryset):
        queryset.filter(status='pending').update(status='expired')
    mark_as_expired.short_description = "Mark selected pending requests as expired"

@admin.register(SkillSwapSession)
class SkillSwapSessionAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'learner', 'skill', 'scheduled_date', 'duration_minutes', 
                   'format', 'status', 'actual_duration')
    list_filter = ('status', 'format', 'scheduled_date')
    search_fields = ('teacher__username', 'learner__username', 'skill__name')
    readonly_fields = ('created_at', 'updated_at', 'started_at', 'ended_at')
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Participants', {
            'fields': ('request', 'teacher', 'learner', 'skill')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'duration_minutes', 'format', 'location', 'meeting_link')
        }),
        ('Session Tracking', {
            'fields': ('status', 'started_at', 'ended_at', 'actual_duration')
        }),
        ('Notes', {
            'fields': ('teacher_notes', 'learner_notes', 'session_summary'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SessionReview)
class SessionReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewee', 'session', 'overall_rating', 
                   'would_recommend', 'is_public', 'is_flagged', 'created_at')
    list_filter = ('overall_rating', 'would_recommend', 'is_public', 'is_flagged', 
                  'is_anonymous', 'created_at')
    search_fields = ('reviewer__username', 'reviewee__username', 'review_text')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Review Details', {
            'fields': ('session', 'reviewer', 'reviewee')
        }),
        ('Ratings', {
            'fields': ('overall_rating', 'communication_rating', 'knowledge_rating', 'punctuality_rating')
        }),
        ('Review Content', {
            'fields': ('review_text', 'what_learned', 'suggestions')
        }),
        ('Settings', {
            'fields': ('would_recommend', 'is_anonymous', 'is_public', 'is_flagged')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['flag_for_moderation', 'unflag_reviews', 'make_public', 'make_private']
    
    def flag_for_moderation(self, request, queryset):
        queryset.update(is_flagged=True)
    flag_for_moderation.short_description = "Flag selected reviews for moderation"
    
    def unflag_reviews(self, request, queryset):
        queryset.update(is_flagged=False)
    unflag_reviews.short_description = "Remove moderation flag from selected reviews"
    
    def make_public(self, request, queryset):
        queryset.update(is_public=True)
    make_public.short_description = "Make selected reviews public"
    
    def make_private(self, request, queryset):
        queryset.update(is_public=False)
    make_private.short_description = "Make selected reviews private"

@admin.register(SessionReminder)
class SessionReminderAdmin(admin.ModelAdmin):
    list_display = ('session', 'user', 'reminder_time', 'is_sent', 'created_at')
    list_filter = ('is_sent', 'reminder_time', 'created_at')
    search_fields = ('session__teacher__username', 'session__learner__username', 'user__username')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session', 'user')
