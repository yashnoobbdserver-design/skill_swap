from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import models
from skill_sessions.models import SkillSwapRequest, SkillSwapSession

def home(request):
    from django.contrib.auth.models import User
    from skills.models import Skill, OfferedSkill
    from skill_sessions.models import SkillSwapSession
    from accounts.models import UserProfile
    
    # Calculate dynamic stats
    stats = {
        'total_users': User.objects.filter(is_active=True).count(),
        'total_skills': Skill.objects.count(),
        'total_offered_skills': OfferedSkill.objects.count(),
        'total_sessions': SkillSwapSession.objects.filter(status='completed').count(),
        'active_sessions': SkillSwapSession.objects.filter(status__in=['scheduled', 'in_progress']).count(),
    }
    
    context = {
        'stats': stats
    }
    
    return render(request, "core/home.html", context)

class HomeView:
    @classmethod
    def as_view(cls):
        return home

class DashboardView:
    @classmethod
    def as_view(cls):
        @login_required
        def dashboard_view(request):
            from skills.models import DesiredSkill, OfferedSkill
            from skill_sessions.models import SkillSwapSession
            from django.db.models import Q, Count
            from datetime import datetime, timedelta
            
            # Calculate user-specific stats
            user = request.user
            
            # Skills completed - count sessions where user was learner and status is completed
            skills_completed = SkillSwapSession.objects.filter(
                learner=user,
                status='completed'
            ).values('skill').distinct().count()
            
            # Sessions this month
            first_day_of_month = datetime.now().replace(day=1)
            sessions_this_month = SkillSwapSession.objects.filter(
                Q(teacher=user) | Q(learner=user),
                created_at__gte=first_day_of_month,
                status='completed'
            ).count()
            
            # Active requests - pending requests where user is involved
            from skill_sessions.models import SkillSwapRequest
            active_requests = SkillSwapRequest.objects.filter(
                Q(requester=user) | Q(recipient=user),
                status='pending'
            ).count()
            
            # Recent requests for the user (both sent and received)
            recent_requests_received = SkillSwapRequest.objects.filter(
                recipient=user
            ).select_related('requester', 'offered_skill__skill')[:5]
            
            recent_requests_sent = SkillSwapRequest.objects.filter(
                requester=user
            ).select_related('recipient', 'offered_skill__skill')[:5]
            
            # Combine and format recent requests
            recent_requests = []
            for req in recent_requests_received:
                recent_requests.append({
                    'skill_name': req.offered_skill.skill.name,
                    'request_type': 'Received',
                    'date': req.created_at,
                    'status': req.get_status_display(),
                    'detail_url': f'/skill-sessions/requests/{req.id}/'
                })
            
            for req in recent_requests_sent:
                recent_requests.append({
                    'skill_name': req.offered_skill.skill.name,
                    'request_type': 'Sent',
                    'date': req.created_at,
                    'status': req.get_status_display(),
                    'detail_url': f'/skill-sessions/requests/{req.id}/'
                })
            
            # Sort by date and limit to 10 most recent
            recent_requests.sort(key=lambda x: x['date'], reverse=True)
            recent_requests = recent_requests[:10]
            
            # Progress data
            completed_courses = SkillSwapSession.objects.filter(
                learner=user,
                status='completed'
            ).count()
            
            stats = {
                'skills_completed': skills_completed,
                'sessions_this_month': sessions_this_month,
                'active_requests': active_requests,
            }
            
            progress = {
                'completed_courses': completed_courses,
            }
            
            context = {
                'stats': stats,
                'recent_requests': recent_requests,
                'progress': progress,
            }
            
            return render(request, "core/dashboard.html", context)
            
        return dashboard_view

class RequestsView:
    @classmethod
    def as_view(cls):
        @login_required
        def requests_view(request):
            # Get received requests for the current user
            received_requests = SkillSwapRequest.objects.filter(
                recipient=request.user
            ).select_related(
                'requester', 'offered_skill__skill'
            ).order_by('-created_at')
            
            # Get sent requests by the current user
            sent_requests = SkillSwapRequest.objects.filter(
                requester=request.user
            ).select_related(
                'recipient', 'offered_skill__skill'
            ).order_by('-created_at')
            
            # Get active sessions for the current user
            active_sessions = SkillSwapSession.objects.filter(
                models.Q(teacher=request.user) | models.Q(learner=request.user),
                status__in=['scheduled', 'in_progress']
            ).select_related(
                'teacher', 'learner', 'skill'
            ).order_by('scheduled_date')
            
            # Calculate stats
            stats = {
                'total_requests': received_requests.count() + sent_requests.count(),
                'pending_requests': received_requests.filter(status='pending').count() + sent_requests.filter(status='pending').count(),
                'accepted_requests': received_requests.filter(status='accepted').count() + sent_requests.filter(status='accepted').count(),
                'active_sessions': active_sessions.count(),
            }
            
            context = {
                'received_requests': received_requests,
                'sent_requests': sent_requests,
                'active_sessions': active_sessions,
                'stats': stats,
            }
            
            return render(request, "core/requests.html", context)
            
        return requests_view

class UserProfileView:
    @classmethod
    def as_view(cls):
        return lambda r, user_id: render(r, "core/user_profile.html")

class SearchView:
    @classmethod
    def as_view(cls):
        return lambda r: render(r, "core/search.html")

class NotificationListView:
    @classmethod
    def as_view(cls):
        @login_required
        def notification_view(request):
            from accounts.models import Notification
            from django.core.paginator import Paginator
            
            # Get all notifications for the current user
            notifications = Notification.objects.filter(
                recipient=request.user
            ).order_by('-created_at')
            
            # Pagination - limit to 10 notifications per page
            paginator = Paginator(notifications, 10)
            page_number = request.GET.get('page')
            notifications_page = paginator.get_page(page_number)
            
            # Mark all unread notifications as read when viewing the page
            unread_notifications = notifications.filter(is_read=False)
            unread_notifications.update(is_read=True)
            
            context = {
                'notifications': notifications_page,
                'unread_count': 0,  # Now 0 since we marked them as read
            }
            
            return render(request, "core/notifications.html", context)
            
        return notification_view

def mark_notification_read(request, notification_id):
    from accounts.models import Notification
    from django.shortcuts import get_object_or_404
    
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({"status": "success"})

def mark_all_notifications_read(request):
    from accounts.models import Notification
    
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"status": "success"})
