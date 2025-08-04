# Generated manually to fix existing empty university_email values

from django.db import migrations
from django.core.exceptions import ValidationError


def fix_empty_university_emails(apps, schema_editor):
    """
    Fix any existing UserProfile records with empty university_email values
    by setting them to a temporary unique value based on the user's email
    """
    UserProfile = apps.get_model('accounts', 'UserProfile')
    User = apps.get_model('auth', 'User')
    
    # Find all UserProfile records with empty university_email
    empty_profiles = UserProfile.objects.filter(
        university_email__in=['', None]
    )
    
    for profile in empty_profiles:
        if profile.user.email:
            # Use the user's regular email as a fallback, but make it unique
            base_email = profile.user.email
            university_email = base_email
            counter = 1
            
            # Ensure uniqueness by appending a number if needed
            while UserProfile.objects.filter(university_email=university_email).exists():
                name, domain = base_email.split('@', 1)
                university_email = f"{name}+{counter}@{domain}"
                counter += 1
            
            profile.university_email = university_email
            profile.save()
        else:
            # If no email available, create a placeholder
            placeholder_email = f"user{profile.user.id}@placeholder.edu"
            counter = 1
            university_email = placeholder_email
            
            while UserProfile.objects.filter(university_email=university_email).exists():
                university_email = f"user{profile.user.id}+{counter}@placeholder.edu"
                counter += 1
            
            profile.university_email = university_email
            profile.save()


def reverse_fix_empty_university_emails(apps, schema_editor):
    """
    Reverse migration - not safe to implement as we can't know which
    emails were originally empty
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_notification_table_alter_userprofile_table'),
    ]

    operations = [
        migrations.RunPython(
            fix_empty_university_emails,
            reverse_fix_empty_university_emails,
        ),
    ]