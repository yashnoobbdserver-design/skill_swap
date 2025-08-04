from django.urls import path
from . import views

app_name = 'skill_sessions'

urlpatterns = [
    # Request management
    path('requests/', views.RequestListView.as_view(), name='request_list'),
    path('requests/sent/', views.SentRequestListView.as_view(), name='sent_requests'),
    path('requests/received/', views.ReceivedRequestListView.as_view(), name='received_requests'),
    path('requests/create/', views.CreateRequestView.as_view(), name='create_request'),
    path('requests/create/<int:user_id>/', views.CreateRequestView.as_view(), name='create_request'),
    path('requests/send/<int:user_id>/', views.SendRequestView.as_view(), name='send_request'),
    path('requests/<int:pk>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('requests/<int:pk>/respond/', views.RequestResponseView.as_view(), name='request_respond'),
    path('requests/<int:pk>/cancel/', views.cancel_request, name='request_cancel'),
    
    # New comprehensive request management
    path('requests/management/', views.session_requests_management, name='request_management'),
    path('request/<int:request_id>/<str:action>/', views.handle_request_action, name='handle_request_action'),
    path('request/<int:request_id>/cancel/', views.cancel_request, name='cancel_request'),
    
    # My Sessions page
    path('my-sessions/', views.my_sessions_view, name='my_sessions'),
    
    # Session management
    path('', views.SessionListView.as_view(), name='session_list'),
    path('manage/', views.SessionManagementView.as_view(), name='session_management'),
    path('approve/<int:session_id>/', views.approve_session, name='approve_session'),
    path('reject/<int:session_id>/', views.reject_session, name='reject_session'),
    path('upcoming/', views.UpcomingSessionListView.as_view(), name='upcoming_sessions'),
    path('history/', views.SessionHistoryView.as_view(), name='session_history'),
    path('<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('<int:pk>/edit/', views.SessionUpdateView.as_view(), name='session_edit'),
    path('<int:pk>/cancel/', views.cancel_session, name='session_cancel'),
    path('<int:pk>/start/', views.start_session_simple, name='session_start'),
    path('<int:pk>/end/', views.end_session, name='session_end'),
    
    # Session details and actions
    path('session/<int:session_id>/reschedule/', views.SessionUpdateView.as_view(), name='reschedule_session'),
    
    # Reviews
    path('<int:session_id>/review/', views.SessionReviewCreateView.as_view(), name='review_create'),
    path('session/<int:session_id>/leave-review/', views.SessionReviewCreateView.as_view(), name='leave_review'),
    path('reviews/<int:pk>/edit/', views.SessionReviewUpdateView.as_view(), name='review_edit'),
    path('reviews/', views.ReviewListView.as_view(), name='review_list'),
    
    # Calendar and scheduling
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('schedule/<int:request_id>/', views.ScheduleSessionView.as_view(), name='schedule_session'),
    
    # AJAX endpoints for dynamic functionality
    path('sessions/<int:session_id>/start/', views.start_session, name='start_session_ajax'),
]