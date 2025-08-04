from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import UserProfile
from core.models import Department, Branch

class UserRegistrationForm(UserCreationForm):
    """Custom registration form with additional fields"""
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    university_email = forms.EmailField(required=True, help_text="Required. Enter your university email address.")
    first_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        empty_label="Select Department",
        help_text="Optional. Your department or major.",
        widget=forms.Select(attrs={
            'class': 'form-control text-lg py-3 px-4 h-14 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 w-full bg-white',
            'id': 'id_department'
        })
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.none(),  # Initially empty, will be populated via AJAX
        required=False,
        empty_label="Select Branch",
        help_text="Optional. Your specialization/branch.",
        widget=forms.Select(attrs={
            'class': 'form-control text-lg py-3 px-4 h-14 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 w-full bg-white',
            'id': 'id_branch',
            'disabled': True  # Initially disabled until department is selected
        })
    )
    year = forms.ChoiceField(choices=UserProfile.YEAR_CHOICES, required=False, help_text="Optional. Your current year of study.")
    bio = forms.CharField(
        max_length=500, required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell others about yourself...'}),
        help_text="Optional. Short bio about yourself."
    )
    availability = forms.CharField(
        max_length=200, required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Describe your general availability...'}),
        help_text="Optional. Your general availability for sessions."
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'university_email', 'department', 'branch', 'year', 'bio', 'availability', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing profile and department is set, populate branches
        if 'department' in self.data:
            try:
                department_value = self.data.get('department')
                if department_value and department_value.strip() and department_value.isdigit():
                    department_id = int(department_value)
                    self.fields['branch'].queryset = Branch.objects.filter(department_id=department_id, is_active=True)
                    self.fields['branch'].widget.attrs.pop('disabled', None)
            except (ValueError, TypeError):
                pass
        elif self.instance and hasattr(self.instance, 'profile') and self.instance.profile.department:
            self.fields['branch'].queryset = self.instance.profile.department.branches.filter(is_active=True)
            self.fields['branch'].widget.attrs.pop('disabled', None)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered.')
        return email
    
    def clean_university_email(self):
        university_email = self.cleaned_data.get('university_email')
        if UserProfile.objects.filter(university_email=university_email).exists():
            raise ValidationError('This university email address is already registered.')
        
        # Validate university email format
        if university_email:
            if not (university_email.endswith('.edu') or 
                   '@university.' in university_email or
                   '@college.' in university_email):
                raise ValidationError('Please use a valid university email address.')
        
        return university_email
    
    def clean(self):
        cleaned_data = super().clean()
        department = cleaned_data.get('department')
        branch = cleaned_data.get('branch')
        
        # Validate branch belongs to department
        if branch and department and branch.department != department:
            raise ValidationError('Selected branch does not belong to the selected department.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        empty_label="Select Department",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_department'
        })
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.none(),
        required=False,
        empty_label="Select Branch",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_branch'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'university_email', 'department', 'branch', 'year', 'bio', 
            'availability', 'profile_picture', 'prefer_in_person', 
            'prefer_online', 'notification_email', 'notification_in_app'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell others about yourself...'}),
            'availability': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your general availability...'}),
            'university_email': forms.EmailInput(attrs={'placeholder': 'your.email@university.edu'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If instance has department, populate branches
        if self.instance and self.instance.department:
            self.fields['branch'].queryset = self.instance.department.branches.filter(is_active=True)
    
    def clean_university_email(self):
        email = self.cleaned_data.get('university_email')
        if email:
            # Check if it's a university email
            if not (email.endswith('.edu') or 
                   '@university.' in email or
                   '@college.' in email):
                raise ValidationError('Please use a valid university email address.')
            
            # Check if email is already used by another user
            if UserProfile.objects.filter(university_email=email).exclude(user=self.instance.user).exists():
                raise ValidationError('This university email is already registered.')
        
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        department = cleaned_data.get('department')
        branch = cleaned_data.get('branch')
        
        # Validate branch belongs to department
        if branch and department and branch.department != department:
            raise ValidationError('Selected branch does not belong to the selected department.')
        
        return cleaned_data


class EmailVerificationForm(forms.Form):
    """Form for email verification"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'your.email@university.edu'}),
        help_text="Enter your university email address"
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not (email.endswith('.edu') or 
               '@university.' in email or
               '@college.' in email):
            raise ValidationError('Please use a valid university email address.')
        return email


class PasswordResetRequestForm(forms.Form):
    """Form for requesting password reset"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'your.email@university.edu'}),
        help_text="Enter your registered university email address"
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user_profile = UserProfile.objects.get(university_email=email)
            if not user_profile.user.is_active:
                raise ValidationError('This account is inactive.')
        except UserProfile.DoesNotExist:
            raise ValidationError('No account found with this email address.')
        return email 

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="University Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control text-lg py-3 px-4 h-14 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 w-full bg-white',
            'placeholder': 'Enter your university email',
            'autocomplete': 'email',
            'required': True,
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No user found with this email address.')
        return email

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        label="Enter OTP",
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-lg py-3 px-4 h-14 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 w-full bg-white',
            'placeholder': 'Enter the OTP sent to your email',
            'autocomplete': 'one-time-code',
            'required': True,
        })
    )

class PasswordResetForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control text-lg py-3 px-4 h-14 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 w-full bg-white',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password',
            'required': True,
        })
    )
    confirm_password = forms.CharField(
        label="Re-enter Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control text-lg py-3 px-4 h-14 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 w-full bg-white',
            'placeholder': 'Re-enter new password',
            'autocomplete': 'new-password',
            'required': True,
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get('new_password')
        pw2 = cleaned_data.get('confirm_password')
        if pw1 and pw2 and pw1 != pw2:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data 