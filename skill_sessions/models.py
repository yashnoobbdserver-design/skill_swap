from django.db import models
from django.contrib.auth.models import User
from skills.models import OfferedSkill, DesiredSkill
from django.utils import timezone
from datetime import timedelta

class SkillSwapRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    offered_skill = models.ForeignKey(OfferedSkill, on_delete=models.CASCADE, related_name='swap_requests')
    desired_skill = models.ForeignKey(DesiredSkill, on_delete=models.CASCADE, related_name='swap_requests', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Personal message from the requester")
    
    # Proposed session details
    proposed_duration = models.PositiveIntegerField(default=60, help_text="Proposed session duration in minutes")
    proposed_format = models.CharField(max_length=20, choices=[
        ('online', 'Online'),
        ('in_person', 'In-Person'),
        ('flexible', 'Flexible'),
    ], default='flexible')
    proposed_location = models.CharField(max_length=200, blank=True, help_text="For in-person sessions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    responded_at = models.DateTimeField(null=True, blank=True)
    response_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'swaprequest'
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)  # Requests expire after 7 days
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Request: {self.requester.username} → {self.recipient.username} ({self.offered_skill.skill.name})"
    
    def is_expired(self):
        return timezone.now() > self.expires_at and self.status == 'pending'
    
    def can_be_responded_to(self):
        return self.status == 'pending' and not self.is_expired()

class SkillSwapSession(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    request = models.OneToOneField(SkillSwapRequest, on_delete=models.CASCADE, related_name='session')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_sessions')
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_sessions')
    skill = models.ForeignKey('skills.Skill', on_delete=models.CASCADE, related_name='skill_sessions')
    
    # Session details
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    format = models.CharField(max_length=20, choices=[
        ('online', 'Online'),
        ('in_person', 'In-Person'),
    ])
    location = models.CharField(max_length=200, blank=True)
    meeting_link = models.URLField(blank=True, help_text="For online sessions")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Session tracking
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    actual_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Actual duration in minutes")
    
    # Notes and feedback
    teacher_notes = models.TextField(blank=True, help_text="Private notes for the teacher")
    learner_notes = models.TextField(blank=True, help_text="Private notes for the learner")
    session_summary = models.TextField(blank=True, help_text="What was covered in this session")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date']
        db_table = 'swapsession'
    
    def __str__(self):
        return f"Session: {self.teacher.username} teaching {self.skill.name} to {self.learner.username}"
    
    def is_upcoming(self):
        return self.status == 'scheduled' and self.scheduled_date > timezone.now()
    
    def is_ongoing(self):
        return self.status == 'in_progress'
    
    def can_start(self):
        now = timezone.now()
        return (self.status == 'scheduled' and 
                self.scheduled_date <= now <= self.scheduled_date + timedelta(minutes=self.duration_minutes))
    
    def get_end_time(self):
        return self.scheduled_date + timedelta(minutes=self.duration_minutes)

class SessionReview(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    session = models.ForeignKey(SkillSwapSession, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    
    # Ratings
    overall_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    communication_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    knowledge_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    punctuality_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    
    # Review content
    review_text = models.TextField(help_text="Share your experience")
    what_learned = models.TextField(blank=True, help_text="What did you learn or teach?")
    suggestions = models.TextField(blank=True, help_text="Any suggestions for improvement?")
    
    # Flags
    would_recommend = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False, help_text="Flagged for moderation")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['session', 'reviewer']
        db_table = 'review'
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username} ({self.overall_rating}/5)"

class SessionReminder(models.Model):
    session = models.ForeignKey(SkillSwapSession, on_delete=models.CASCADE, related_name='reminders')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['reminder_time']
        unique_together = ['session', 'user', 'reminder_time']
        db_table = 'reminder'
    
    def __str__(self):
        return f"Reminder for {self.user.username} - {self.session}"
