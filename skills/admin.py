from django.contrib import admin
from .models import SkillCategory, Skill, OfferedSkill, DesiredSkill, SkillMatch

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color', 'is_active', 'skills_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    
    def skills_count(self, obj):
        return obj.skills.count()
    skills_count.short_description = 'Number of Skills'

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_popular', 'offered_count', 'desired_count', 'created_at')
    list_filter = ('category', 'is_popular', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    readonly_fields = ('created_at',)
    
    def offered_count(self, obj):
        return obj.offered_by_users.filter(is_active=True).count()
    offered_count.short_description = 'Offered By'
    
    def desired_count(self, obj):
        return obj.desired_by_users.filter(is_active=True).count()
    desired_count.short_description = 'Desired By'

@admin.register(OfferedSkill)
class OfferedSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'proficiency_level', 'teaching_preference', 
                   'years_of_experience', 'average_rating', 'total_sessions', 'is_active')
    list_filter = ('proficiency_level', 'teaching_preference', 'is_active', 'created_at')
    search_fields = ('user__username', 'skill__name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'total_sessions', 'average_rating')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'skill', 'proficiency_level', 'years_of_experience', 'is_active')
        }),
        ('Teaching Details', {
            'fields': ('description', 'teaching_preference', 'max_students_per_session')
        }),
        ('Statistics', {
            'fields': ('total_sessions', 'average_rating'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DesiredSkill)
class DesiredSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'urgency', 'current_level', 'target_level', 
                   'learning_preference', 'is_active')
    list_filter = ('urgency', 'current_level', 'target_level', 'learning_preference', 
                  'is_active', 'created_at')
    search_fields = ('user__username', 'skill__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'skill', 'urgency', 'is_active')
        }),
        ('Learning Details', {
            'fields': ('description', 'current_level', 'target_level', 'learning_preference')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SkillMatch)
class SkillMatchAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'learner', 'offered_skill', 'desired_skill', 
                   'compatibility_score', 'is_mutual', 'is_dismissed', 'created_at')
    list_filter = ('is_mutual', 'is_dismissed', 'created_at')
    search_fields = ('teacher__username', 'learner__username', 
                    'offered_skill__skill__name', 'desired_skill__skill__name')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'teacher', 'learner', 'offered_skill__skill', 'desired_skill__skill'
        )
