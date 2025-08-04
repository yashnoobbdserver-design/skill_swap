from django import forms
from .models import Skill, SkillCategory, OfferedSkill, DesiredSkill

class OfferedSkillForm(forms.ModelForm):
    """Form for creating/editing offered skills"""
    skill_category = forms.ModelChoiceField(
        queryset=SkillCategory.objects.filter(is_active=True),
        required=True,
        label="Skill Category",
        help_text="Select the category for your skill",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    skill = forms.ModelChoiceField(
        queryset=Skill.objects.none(),
        required=True,
        label="Skill",
        help_text="Select a skill from the list",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = OfferedSkill
        fields = ['skill_category', 'skill', 'proficiency_level', 'description', 'years_of_experience', 'teaching_preference']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'proficiency_level': forms.Select(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'teaching_preference': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If form has data (like from POST), filter skills by category
        if 'skill_category' in self.data:
            try:
                category_id = int(self.data.get('skill_category'))
                self.fields['skill'].queryset = Skill.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass
        # If instance exists (editing), set the category and filter skills
        elif self.instance.pk and hasattr(self.instance, 'skill') and self.instance.skill:
            self.fields['skill_category'].initial = self.instance.skill.category
            self.fields['skill'].queryset = Skill.objects.filter(category=self.instance.skill.category).order_by('name')
        
    def clean(self):
        cleaned_data = super().clean()
        skill = cleaned_data.get('skill')
        skill_category = cleaned_data.get('skill_category')
        user = getattr(self.instance, 'user', None)
        
        # Validate that skill belongs to selected category
        if skill and skill_category and skill.category != skill_category:
            raise forms.ValidationError('Selected skill does not belong to the selected category.')
        
        # Check for duplicate skills for the user
        if skill and user:
            existing = OfferedSkill.objects.filter(user=user, skill=skill).exclude(pk=self.instance.pk if self.instance.pk else None)
            if existing.exists():
                raise forms.ValidationError(f'You already offer {skill.name}.')
        
        return cleaned_data


class DesiredSkillForm(forms.ModelForm):
    """Form for creating/editing desired skills"""
    skill_category = forms.ModelChoiceField(
        queryset=SkillCategory.objects.filter(is_active=True),
        required=True,
        label="Skill Category",
        help_text="Select the category for the skill you want to learn",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    skill = forms.ModelChoiceField(
        queryset=Skill.objects.none(),
        required=True,
        label="Skill",
        help_text="Select a skill you want to learn",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = DesiredSkill
        fields = ['skill_category', 'skill', 'urgency', 'description', 'current_level', 'target_level', 'learning_preference']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
            'current_level': forms.Select(attrs={'class': 'form-control'}),
            'target_level': forms.Select(attrs={'class': 'form-control'}),
            'learning_preference': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If form has data (like from POST), filter skills by category
        if 'skill_category' in self.data:
            try:
                category_id = int(self.data.get('skill_category'))
                self.fields['skill'].queryset = Skill.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass
        # If instance exists (editing), set the category and filter skills
        elif self.instance.pk and hasattr(self.instance, 'skill') and self.instance.skill:
            self.fields['skill_category'].initial = self.instance.skill.category
            self.fields['skill'].queryset = Skill.objects.filter(category=self.instance.skill.category).order_by('name')
    
    def clean(self):
        cleaned_data = super().clean()
        skill = cleaned_data.get('skill')
        skill_category = cleaned_data.get('skill_category')
        user = getattr(self.instance, 'user', None)
        
        # Validate that skill belongs to selected category
        if skill and skill_category and skill.category != skill_category:
            raise forms.ValidationError('Selected skill does not belong to the selected category.')
        
        if skill and user:
            existing = DesiredSkill.objects.filter(user=user, skill=skill).exclude(pk=self.instance.pk if self.instance.pk else None)
            if existing.exists():
                raise forms.ValidationError(f'You already want to learn {skill.name}.')
        
        return cleaned_data


class SkillSearchForm(forms.Form):
    """Form for searching and filtering skills"""
    category = forms.ModelChoiceField(
        queryset=SkillCategory.objects.filter(is_active=True), 
        required=False, 
        empty_label="Select Category...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    skill = forms.ModelChoiceField(
        queryset=Skill.objects.none(),
        required=False,
        empty_label="Select Skill...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If form has data, filter skills by category
        if 'category' in self.data and self.data.get('category'):
            try:
                category_id = int(self.data.get('category'))
                self.fields['skill'].queryset = Skill.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass 