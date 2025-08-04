from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_email
from core.models import Department, Branch
import re

class UserProfile(models.Model):
    YEAR_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
        ('graduate', 'Graduate'),
        ('phd', 'PhD'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    university_email = models.EmailField(unique=True, help_text="Use your university email address")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    year = models.CharField(max_length=20, choices=YEAR_CHOICES, blank=True)
    bio = models.TextField(max_length=500, blank=True, help_text="Tell others about yourself")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    availability = models.TextField(blank=True, help_text="Describe your general availability for skill-swap sessions")
    is_verified = models.BooleanField(default=False, help_text="University email verification status")
    date_joined = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Rating system
    total_sessions_taught = models.PositiveIntegerField(default=0)
    total_sessions_learned = models.PositiveIntegerField(default=0)
    average_rating_as_teacher = models.FloatField(default=0.0)
    average_rating_as_learner = models.FloatField(default=0.0)
    
    # Preferences
    prefer_in_person = models.BooleanField(default=True)
    prefer_online = models.BooleanField(default=True)
    notification_email = models.BooleanField(default=True)
    notification_in_app = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date_joined']
        db_table = 'userprofile'
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"
    
    def clean(self):
        # Validate university email format
        if self.university_email:
            if not (self.university_email.endswith('.edu') or 
                   '@university.' in self.university_email or
                   '@college.' in self.university_email):
                from django.core.exceptions import ValidationError
                raise ValidationError('Please use a valid university email address.')
        
        # Validate branch belongs to department
        if self.branch and self.department and self.branch.department != self.department:
            from django.core.exceptions import ValidationError
            raise ValidationError('Selected branch does not belong to the selected department.')
    
    def get_full_name(self):
        return self.user.get_full_name() or self.user.username
    
    def get_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = ['university_email', 'department', 'branch', 'year', 'bio', 'availability']
        completed = sum(1 for field in fields if getattr(self, field))
        return int((completed / len(fields)) * 100)

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('skill_request', 'Skill Swap Request'),
        ('request_accepted', 'Request Accepted'),
        ('request_declined', 'Request Declined'),
        ('session_scheduled', 'Session Scheduled'),
        ('session_reminder', 'Session Reminder'),
        ('session_completed', 'Session Completed'),
        ('new_review', 'New Review'),
        ('system', 'System Notification'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications')
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'notification'
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
