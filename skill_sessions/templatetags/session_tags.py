from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def has_user_reviewed(session, user):
    """Check if user has already reviewed this session"""
    if not user or not user.is_authenticated:
        return False
    return session.reviews.filter(reviewer=user).exists()

@register.filter
def session_format_icon(session_format):
    """Return appropriate icon based on session format"""
    if session_format == 'online':
        return 'video'
    else:
        return 'map-marker-alt'