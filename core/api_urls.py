from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # Notification APIs
    path('notifications/', api_views.NotificationListAPI.as_view(), name='notification_list'),
    path('notifications/unread-count/', api_views.UnreadNotificationCountAPI.as_view(), name='unread_count'),
    
    # Search APIs
    path('search/users/', api_views.UserSearchAPI.as_view(), name='user_search'),
    path('search/skills/', api_views.SkillSearchAPI.as_view(), name='skill_search'),
    
    # Skill matching API
    path('matching/suggestions/', api_views.SkillMatchingSuggestionsAPI.as_view(), name='matching_suggestions'),
    
    # Quick actions
    path('user/<int:user_id>/send-request/', api_views.SendSkillRequestAPI.as_view(), name='send_request'),
]