from django.urls import path
from . import views

app_name = 'skills'

urlpatterns = [
    # Skill browsing
    path('', views.SkillListView.as_view(), name='skill_list'),
    path('trending/more/', views.TrendingSkillsMoreView.as_view(), name='trending_skills_more'),
    path('categories/', views.SkillCategoryListView.as_view(), name='category_list'),
    path('category/<int:category_id>/', views.SkillCategoryDetailView.as_view(), name='category_detail'),
    path('<int:pk>/', views.SkillDetailView.as_view(), name='skill_detail'),
    
    # Add Skill
    path('add/', views.AddSkillView.as_view(), name='add_skill'),
    
    # Offered skills management
    path('offered/', views.OfferedSkillListView.as_view(), name='offered_list'),
    path('offered/add/', views.OfferedSkillCreateView.as_view(), name='offered_add'),
    path('offered/<int:pk>/edit/', views.OfferedSkillUpdateView.as_view(), name='offered_edit'),
    path('offered/<int:pk>/delete/', views.OfferedSkillDeleteView.as_view(), name='offered_delete'),
    path('offered/<int:pk>/toggle/', views.toggle_offered_skill, name='offered_toggle'),
    
    # Desired skills management
    path('desired/', views.DesiredSkillListView.as_view(), name='desired_list'),
    path('desired/add/', views.DesiredSkillCreateView.as_view(), name='desired_add'),
    path('desired/<int:pk>/edit/', views.DesiredSkillUpdateView.as_view(), name='desired_edit'),
    path('desired/<int:pk>/delete/', views.DesiredSkillDeleteView.as_view(), name='desired_delete'),
    path('desired/<int:pk>/toggle/', views.toggle_desired_skill, name='desired_toggle'),
    
    # Skill matching
    path('matches/', views.SkillMatchListView.as_view(), name='match_list'),
    path('matches/<int:pk>/dismiss/', views.dismiss_skill_match, name='match_dismiss'),
    
    # Find tutors
    path('<int:skill_id>/find-tutors/', views.FindTutorsView.as_view(), name='find_tutors'),
    path('tutor/<int:user_id>/', views.TutorProfileView.as_view(), name='tutor_profile'),
    
    # AJAX endpoints
    path('ajax/skill-autocomplete/', views.SkillAutocompleteView.as_view(), name='skill_autocomplete'),
    path('ajax/get-skills-by-category/', views.get_skills_by_category, name='get_skills_by_category'),
    path('ajax/get-skills-by-category-public/', views.get_skills_by_category_public, name='get_skills_by_category_public'),
    path('ajax/get-user-stats/', views.get_user_stats, name='get_user_stats'),
]