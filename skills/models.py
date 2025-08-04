from django.db import models
from django.contrib.auth.models import User

class SkillCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Skill Categories"
        db_table = 'category'
    
    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    description = models.TextField(blank=True)
    is_popular = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category__name', 'name']
        unique_together = ['name', 'category']
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"

class OfferedSkill(models.Model):
    PROFICIENCY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offered_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='offered_by_users')
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    description = models.TextField(blank=True, help_text="Describe your experience with this skill")
    years_of_experience = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    teaching_preference = models.CharField(max_length=20, choices=[
        ('online', 'Online Only'),
        ('in_person', 'In-Person Only'),
        ('both', 'Both Online and In-Person'),
    ], default='both')
    max_students_per_session = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Rating for this specific skill teaching
    total_sessions = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'skill']
        db_table = 'offeredskill'
    
    def __str__(self):
        return f"{self.user.username} offers {self.skill.name}"

class DesiredSkill(models.Model):
    URGENCY_LEVELS = [
        ('low', 'Low - Whenever convenient'),
        ('medium', 'Medium - Within a month'),
        ('high', 'High - Within a week'),
        ('urgent', 'Urgent - ASAP'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='desired_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='desired_by_users')
    urgency = models.CharField(max_length=20, choices=URGENCY_LEVELS, default='medium')
    description = models.TextField(blank=True, help_text="What would you like to learn about this skill?")
    current_level = models.CharField(max_length=20, choices=OfferedSkill.PROFICIENCY_LEVELS, default='beginner')
    target_level = models.CharField(max_length=20, choices=OfferedSkill.PROFICIENCY_LEVELS, default='intermediate')
    learning_preference = models.CharField(max_length=20, choices=[
        ('online', 'Online Only'),
        ('in_person', 'In-Person Only'),
        ('both', 'Both Online and In-Person'),
    ], default='both')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'skill']
        db_table = 'desiredskill'
    
    def __str__(self):
        return f"{self.user.username} wants to learn {self.skill.name}"

class SkillMatch(models.Model):
    """Model to track potential skill matches for the matching algorithm"""
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_matches')
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_matches')
    offered_skill = models.ForeignKey(OfferedSkill, on_delete=models.CASCADE)
    desired_skill = models.ForeignKey(DesiredSkill, on_delete=models.CASCADE)
    compatibility_score = models.FloatField(default=0.0, help_text="Algorithm calculated compatibility (0-100)")
    is_mutual = models.BooleanField(default=False, help_text="True if both users can teach each other something")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_dismissed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-compatibility_score', '-created_at']
        unique_together = ['teacher', 'learner', 'offered_skill', 'desired_skill']
        db_table = 'match'
    
    def __str__(self):
        return f"Match: {self.teacher.username} → {self.learner.username} ({self.offered_skill.skill.name})"
