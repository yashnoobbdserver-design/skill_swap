from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Notification

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('university_email', 'department', 'year', 'bio', 'profile_picture', 
              'availability', 'is_verified', 'prefer_in_person', 'prefer_online')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_university_email', 'get_department')
    list_filter = BaseUserAdmin.list_filter + ('profile__is_verified', 'profile__department')
    
    def get_university_email(self, obj):
        return obj.profile.university_email if hasattr(obj, 'profile') else '-'
    get_university_email.short_description = 'University Email'
    
    def get_department(self, obj):
        return obj.profile.department if hasattr(obj, 'profile') else '-'
    get_department.short_description = 'Department'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university_email', 'department', 'year', 'is_verified', 'date_joined')
    list_filter = ('is_verified', 'department', 'year', 'date_joined')
    search_fields = ('user__username', 'user__email', 'university_email', 'department')
    readonly_fields = ('date_joined', 'last_active', 'total_sessions_taught', 
                      'total_sessions_learned', 'average_rating_as_teacher', 
                      'average_rating_as_learner')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'university_email', 'is_verified')
        }),
        ('Academic Details', {
            'fields': ('department', 'year', 'bio', 'profile_picture', 'availability')
        }),
        ('Preferences', {
            'fields': ('prefer_in_person', 'prefer_online', 'notification_email', 'notification_in_app')
        }),
        ('Statistics', {
            'fields': ('total_sessions_taught', 'total_sessions_learned', 
                      'average_rating_as_teacher', 'average_rating_as_learner'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('date_joined', 'last_active'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected notifications as unread"
