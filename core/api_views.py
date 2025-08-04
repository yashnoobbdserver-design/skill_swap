from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

class NotificationListAPI(LoginRequiredMixin, ListView):
    """API for listing user notifications"""
    
    def get(self, request, *args, **kwargs):
        from accounts.models import Notification
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:20]
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        
        data = []
        for n in notifications:
            data.append({
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
                'notification_type': n.notification_type
            })
        
        return JsonResponse({
            'notifications': data,
            'unread_count': unread_count
        })


class UnreadNotificationCountAPI(LoginRequiredMixin, ListView):
    """API for getting unread notification count"""
    
    def get(self, request, *args, **kwargs):
        from accounts.models import Notification
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return JsonResponse({'count': count})


class UserSearchAPI(LoginRequiredMixin, ListView):
    """API for searching users"""
    
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if not query:
            return JsonResponse({'results': []})
        
        from accounts.models import UserProfile
        users = UserProfile.objects.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query)
        )[:10]
        
        data = [{'id': u.user.id, 'username': u.user.username} for u in users]
        return JsonResponse({'results': data})


class SkillSearchAPI(LoginRequiredMixin, ListView):
    """API for searching skills"""
    
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if not query:
            return JsonResponse({'results': []})
        
        from skills.models import Skill
        skills = Skill.objects.filter(name__icontains=query)[:10]
        data = [{'id': s.id, 'name': s.name} for s in skills]
        return JsonResponse({'results': data})


class SkillMatchingSuggestionsAPI(LoginRequiredMixin, ListView):
    """API for getting skill matching suggestions"""
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({'results': []})


class SendSkillRequestAPI(LoginRequiredMixin, ListView):
    """API for sending skill swap requests"""
    
    def post(self, request, user_id, *args, **kwargs):
        return JsonResponse({'success': 'Request sent'}) 