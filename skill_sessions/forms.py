from django import forms
from django.contrib.auth.models import User
from .models import SkillSwapRequest, SkillSwapSession, SessionReview
from skills.models import OfferedSkill, DesiredSkill

class SkillSwapRequestForm(forms.ModelForm):
    """Form for creating skill swap requests"""
    offered_skill = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Select a skill to learn",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = SkillSwapRequest
        fields = ['offered_skill', 'message', 'proposed_format', 'proposed_location']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Introduce yourself and explain why you\'d like to learn this skill...'
            }),
            'proposed_location': forms.TextInput(attrs={
                'placeholder': 'e.g., Library, Coffee Shop, Online'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.requester = kwargs.pop('requester', None)
        self.recipient = kwargs.pop('recipient', None)
        self.show_skill_selection = kwargs.pop('show_skill_selection', False)
        super().__init__(*args, **kwargs)
        
        # Set up offered_skill queryset if recipient is provided
        if self.recipient and self.show_skill_selection:
            from skills.models import OfferedSkill
            self.fields['offered_skill'].queryset = OfferedSkill.objects.filter(
                user=self.recipient, is_active=True
            )
            self.fields['offered_skill'].required = True
        else:
            # Hide the field if not needed
            self.fields['offered_skill'].widget = forms.HiddenInput()
            self.fields['offered_skill'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        if self.requester and self.recipient:
            # Check if there's already a pending request
            existing = SkillSwapRequest.objects.filter(
                requester=self.requester,
                recipient=self.recipient,
                status='pending'
            )
            if existing.exists():
                raise forms.ValidationError('You already have a pending request with this user.')
        
        return cleaned_data


class RequestResponseForm(forms.Form):
    """Form for responding to skill swap requests"""
    response_message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Optional message to the requester...'
        }),
        required=False
    )
    proposed_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        help_text="If accepting, propose a date and time"
    )
    proposed_location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Meeting location'})
    )


class SessionScheduleForm(forms.ModelForm):
    """Form for scheduling sessions"""
    
    class Meta:
        model = SkillSwapSession
        fields = ['scheduled_date', 'duration_minutes', 'format', 'location', 'meeting_link']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-input'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '15',
                'max': '480',
                'step': '15'
            }),
            'format': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={
                'placeholder': 'Meeting location',
                'class': 'form-input'
            }),
            'meeting_link': forms.URLInput(attrs={
                'placeholder': 'https://meet.google.com/...',
                'class': 'form-input'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        scheduled_date = cleaned_data.get('scheduled_date')
        duration_minutes = cleaned_data.get('duration_minutes')
        format_type = cleaned_data.get('format')
        meeting_link = cleaned_data.get('meeting_link')
        
        if scheduled_date:
            from django.utils import timezone
            from datetime import timedelta
            
            if scheduled_date <= timezone.now():
                raise forms.ValidationError('Session must be scheduled for a future date and time.')
            
            # Check for overlapping sessions if we have both date and duration
            if duration_minutes:
                session_end_time = scheduled_date + timedelta(minutes=duration_minutes)
                
                # Import here to avoid circular imports
                from .models import SkillSwapSession
                from django.db.models import Q
                
                # Get user from form instance (if available) or from the view
                user = getattr(self, 'user', None)
                if hasattr(self, 'instance') and hasattr(self.instance, 'teacher'):
                    user = self.instance.teacher
                elif hasattr(self, 'instance') and hasattr(self.instance, 'learner'):
                    user = self.instance.learner
                
                if user:
                    # Check for overlapping sessions where user is either teacher or learner
                    overlapping_sessions = SkillSwapSession.objects.filter(
                        Q(teacher=user) | Q(learner=user),
                        status__in=['scheduled', 'in_progress'],
                        scheduled_date__lt=session_end_time,
                        scheduled_date__gte=scheduled_date - timedelta(minutes=480)  # Check 8 hours before to account for long sessions
                    )
                    
                    # Filter sessions that actually overlap
                    for session in overlapping_sessions:
                        existing_end = session.scheduled_date + timedelta(minutes=session.duration_minutes)
                        
                        # Check if the time ranges overlap
                        if (scheduled_date < existing_end and session_end_time > session.scheduled_date):
                            # Exclude the current session if we're editing
                            if not (hasattr(self, 'instance') and self.instance.pk == session.pk):
                                raise forms.ValidationError(
                                    f'You already have a session scheduled from {session.scheduled_date.strftime("%b %d, %Y at %I:%M %p")} '
                                    f'to {existing_end.strftime("%I:%M %p")}. Please choose a different time.'
                                )
        
        if format_type == 'online' and not meeting_link:
            raise forms.ValidationError('Meeting link is required for online sessions.')
        
        return cleaned_data


class SessionReviewForm(forms.ModelForm):
    """Form for creating session reviews"""
    
    class Meta:
        model = SessionReview
        fields = [
            'overall_rating', 'communication_rating', 'knowledge_rating', 
            'punctuality_rating', 'review_text', 'what_learned', 'suggestions',
            'would_recommend', 'is_anonymous', 'is_public'
        ]
        widgets = {
            'review_text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your experience with this session...'
            }),
            'what_learned': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'What did you learn or teach?'
            }),
            'suggestions': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Any suggestions for improvement?'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        overall_rating = cleaned_data.get('overall_rating')
        review_text = cleaned_data.get('review_text')
        
        if overall_rating and overall_rating < 3 and not review_text:
            raise forms.ValidationError('Please provide feedback when giving a low rating.')
        
        return cleaned_data


class SessionFilterForm(forms.Form):
    """Form for filtering sessions"""
    status = forms.ChoiceField(
        choices=[
            ('', 'All Statuses'),
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        required=False
    )
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    format_type = forms.ChoiceField(
        choices=[
            ('', 'All Formats'),
            ('online', 'Online'),
            ('in_person', 'In-Person'),
        ],
        required=False
    ) 