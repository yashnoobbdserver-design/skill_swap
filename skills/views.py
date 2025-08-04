from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Count, Avg
from django.contrib.auth.models import User

from .models import Skill, SkillCategory, OfferedSkill, DesiredSkill, SkillMatch
from .forms import OfferedSkillForm, DesiredSkillForm, SkillSearchForm

# Create your views here.

class SkillListView(ListView):
    model = Skill
    template_name = 'skills/skill_list.html'
    context_object_name = 'skills'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Skill.objects.filter(category__is_active=True).annotate(
            offered_count=Count('offered_by_users')
        )
        
        # Get filter parameters
        category = self.request.GET.get('category')
        skill = self.request.GET.get('skill')
        sort_by = self.request.GET.get('sort', 'name')
        
        # Apply filters
        if category:
            queryset = queryset.filter(category_id=category)
        
        if skill:
            queryset = queryset.filter(id=skill)
        
        # Apply sorting
        if sort_by == 'popular':
            queryset = queryset.order_by('-offered_count', 'name')
        elif sort_by == 'recent':
            queryset = queryset.order_by('-created_at', 'name')
        else:  # default to name
            queryset = queryset.order_by('name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Initialize the search form with GET data
        context['search_form'] = SkillSearchForm(self.request.GET)
        
        # Determine if any filters are applied
        has_filters = bool(self.request.GET.get('category') or self.request.GET.get('skill'))
        
        # Show trending skills by default when no filters are applied
        show_trending = not has_filters
        context['show_trending'] = show_trending
        
        # Show skills grid when someone searches or wants to find teachers
        show_skills_grid = has_filters or self.request.GET.get('find_teachers')
        context['show_skills_grid'] = show_skills_grid
        
        if show_trending:
            # Get trending skills based on most offered skills (limited to 15)
            trending_skills = (Skill.objects
                              .filter(category__is_active=True)
                              .annotate(offered_count=Count('offered_by_users'))
                              .filter(offered_count__gt=0)
                              .order_by('-offered_count', 'name')[:15])
            context['trending_skills'] = trending_skills
        
        # If showing skills grid, get teachers for the filtered skills
        if show_skills_grid and has_filters:
            from .models import OfferedSkill
            queryset = self.get_queryset()
            teachers_data = []
            
            for skill in queryset:
                offered_skills = OfferedSkill.objects.filter(
                    skill=skill, 
                    is_active=True
                ).select_related('user').annotate(
                    avg_rating=Avg('user__teaching_sessions__reviews__overall_rating')
                )
                
                skill_teachers = []
                for offered_skill in offered_skills:
                    skill_teachers.append({
                        'user': offered_skill.user,
                        'offered_skill': offered_skill,
                        'avg_rating': offered_skill.avg_rating or 0,
                    })
                
                if skill_teachers:
                    teachers_data.append({
                        'skill': skill,
                        'teachers': skill_teachers[:6]  # Limit to 6 teachers per skill
                    })
            
            context['teachers_data'] = teachers_data
        
        # Get all categories for browse section
        context['categories'] = SkillCategory.objects.filter(is_active=True).annotate(
            skill_count=Count('skills')
        )
        
        # Add filter information for display
        if self.request.GET.get('category'):
            try:
                selected_category = SkillCategory.objects.get(id=self.request.GET.get('category'))
                context['selected_category'] = selected_category
            except SkillCategory.DoesNotExist:
                pass
        
        if self.request.GET.get('skill'):
            try:
                selected_skill = Skill.objects.get(id=self.request.GET.get('skill'))
                context['selected_skill'] = selected_skill
            except Skill.DoesNotExist:
                pass
        
        context['show_more_url'] = 'skills:trending_skills_more'
        
        return context


class SkillCategoryListView(ListView):
    model = SkillCategory   
    template_name = 'skills/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return SkillCategory.objects.filter(is_active=True)


class SkillCategoryDetailView(DetailView):
    model = SkillCategory
    template_name = 'skills/category_detail.html'
    context_object_name = 'category'


class OfferedSkillListView(LoginRequiredMixin, ListView):
    model = OfferedSkill
    template_name = 'skills/offered_list.html'
    context_object_name = 'offered_skills'
    
    def get_queryset(self):
        return OfferedSkill.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['desired_skills'] = self.request.user.desired_skills.all()
        return context


class OfferedSkillCreateView(LoginRequiredMixin, CreateView):
    model = OfferedSkill
    form_class = OfferedSkillForm
    template_name = 'skills/offered_form.html'
    success_url = reverse_lazy('skills:offered_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Calculate updated skills completed count
        from skill_sessions.models import SkillSwapSession
        skills_completed = SkillSwapSession.objects.filter(
            learner=self.request.user,
            status='completed'
        ).values('skill').distinct().count()
        
        messages.success(
            self.request, 
            f'Skill added successfully! You have completed {skills_completed} skills so far.'
        )
        return response


class OfferedSkillUpdateView(LoginRequiredMixin, UpdateView):
    model = OfferedSkill
    form_class = OfferedSkillForm
    template_name = 'skills/offered_form.html'
    success_url = reverse_lazy('skills:offered_list')
    
    def get_queryset(self):
        return OfferedSkill.objects.filter(user=self.request.user)


class OfferedSkillDeleteView(LoginRequiredMixin, DeleteView):
    model = OfferedSkill
    template_name = 'skills/offered_confirm_delete.html'
    success_url = reverse_lazy('skills:offered_list')
    
    def get_queryset(self):
        return OfferedSkill.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        
        # Calculate updated skills completed count
        from skill_sessions.models import SkillSwapSession
        skills_completed = SkillSwapSession.objects.filter(
            learner=self.request.user,
            status='completed'
        ).values('skill').distinct().count()
        
        messages.success(
            self.request, 
            f'Skill removed successfully! You have completed {skills_completed} skills so far.'
        )
        return response


@login_required
def toggle_offered_skill(request, pk):
    offered_skill = get_object_or_404(OfferedSkill, pk=pk, user=request.user)
    offered_skill.is_active = not offered_skill.is_active
    offered_skill.save()
    return redirect('skills:offered_list')


class DesiredSkillListView(LoginRequiredMixin, ListView):
    model = DesiredSkill
    template_name = 'skills/desired_list.html'
    context_object_name = 'desired_skills'
    
    def get_queryset(self):
        return DesiredSkill.objects.filter(user=self.request.user)


class DesiredSkillCreateView(LoginRequiredMixin, CreateView):
    model = DesiredSkill
    form_class = DesiredSkillForm
    template_name = 'skills/desired_form.html'
    success_url = reverse_lazy('skills:desired_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Calculate updated skills completed count
        from skill_sessions.models import SkillSwapSession
        skills_completed = SkillSwapSession.objects.filter(
            learner=self.request.user,
            status='completed'
        ).values('skill').distinct().count()
        
        messages.success(
            self.request, 
            f'Skill goal added successfully! You have completed {skills_completed} skills so far.'
        )
        return response


class DesiredSkillUpdateView(LoginRequiredMixin, UpdateView):
    model = DesiredSkill
    form_class = DesiredSkillForm
    template_name = 'skills/desired_form.html'
    success_url = reverse_lazy('skills:desired_list')
    
    def get_queryset(self):
        return DesiredSkill.objects.filter(user=self.request.user)


class DesiredSkillDeleteView(LoginRequiredMixin, DeleteView):
    model = DesiredSkill
    template_name = 'skills/desired_confirm_delete.html'
    success_url = reverse_lazy('skills:desired_list')
    
    def get_queryset(self):
        return DesiredSkill.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        
        # Calculate updated skills completed count
        from skill_sessions.models import SkillSwapSession
        skills_completed = SkillSwapSession.objects.filter(
            learner=self.request.user,
            status='completed'
        ).values('skill').distinct().count()
        
        messages.success(
            self.request, 
            f'Skill goal removed successfully! You have completed {skills_completed} skills so far.'
        )
        return response


@login_required
def toggle_desired_skill(request, pk):
    desired_skill = get_object_or_404(DesiredSkill, pk=pk, user=request.user)
    desired_skill.is_active = not desired_skill.is_active
    desired_skill.save()
    return redirect('skills:desired_list')


class SkillMatchListView(LoginRequiredMixin, ListView):
    model = SkillMatch
    template_name = 'skills/match_list.html'
    context_object_name = 'matches'
    
    def get_queryset(self):
        from django.db.models import Q
        return SkillMatch.objects.filter(
            Q(teacher=self.request.user) | Q(learner=self.request.user),
            is_dismissed=False
        )


@login_required
def dismiss_skill_match(request, pk):
    match = get_object_or_404(SkillMatch, pk=pk)
    match.is_dismissed = True
    match.save()
    return redirect('skills:match_list')


class SkillAutocompleteView(LoginRequiredMixin, ListView):
    model = Skill
    
    def get_queryset(self):
        term = self.request.GET.get('term', '')
        return Skill.objects.filter(name__icontains=term)[:10]
    
    def get(self, request, *args, **kwargs):
        skills = self.get_queryset()
        data = [{'id': skill.id, 'text': skill.name} for skill in skills]
        return JsonResponse({'results': data})


class AddSkillView(LoginRequiredMixin, CreateView):
    model = OfferedSkill
    form_class = OfferedSkillForm
    template_name = 'skills/add_skill.html'
    success_url = '/skills/offered/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get trending skills (top 10 by offered count)
        trending_skills = (Skill.objects
                         .filter(category__is_active=True)
                         .annotate(offered_count=Count('offered_by_users'))
                         .filter(offered_count__gt=0)
                         .order_by('-offered_count', 'name')[:10])
        context['trending_skills'] = trending_skills
        return context


@login_required
def get_skills_by_category(request):
    """AJAX view to get skills by category"""
    category_id = request.GET.get('category_id')
    if category_id:
        skills = Skill.objects.filter(category_id=category_id).order_by('name')
        data = [{'id': skill.id, 'name': skill.name} for skill in skills]
        return JsonResponse({'skills': data})
    return JsonResponse({'skills': []})


def get_skills_by_category_public(request):
    """Public AJAX view to get skills by category for search form"""
    category_id = request.GET.get('category_id')
    if category_id:
        skills = Skill.objects.filter(category_id=category_id).order_by('name')
        data = [{'id': skill.id, 'name': skill.name} for skill in skills]
        return JsonResponse({'skills': data})
    return JsonResponse({'skills': []})


@login_required
def get_user_stats(request):
    """AJAX endpoint to get user's current dashboard stats"""
    from skill_sessions.models import SkillSwapSession, SkillSwapRequest
    from django.db.models import Q
    from datetime import datetime
    
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
    
    # Active requests
    active_requests = SkillSwapRequest.objects.filter(
        Q(requester=user) | Q(recipient=user),
        status='pending'
    ).count()
    
    return JsonResponse({
        'skills_completed': skills_completed,
        'sessions_this_month': sessions_this_month,
        'active_requests': active_requests,
    })


class TrendingSkillsMoreView(LoginRequiredMixin, ListView):
    """View to show more trending skills - requires login"""
    model = Skill
    template_name = 'skills/trending_skills_more.html'
    context_object_name = 'trending_skills'
    paginate_by = 10
    
    def get_queryset(self):
        from django.db.models import Count
        return (Skill.objects
                .filter(category__is_active=True)
                .annotate(offered_count=Count('offered_by_users'))
                .filter(offered_count__gt=0)
                .order_by('-offered_count', 'name'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'All Trending Skills'
        return context


class SkillDetailView(DetailView):
    """View to show skill details with tutors and find tutors option"""
    model = Skill
    template_name = 'skills/skill_detail.html'
    context_object_name = 'skill'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skill = self.get_object()
        
        # Get tutors offering this skill (top 3 by rating)
        top_tutors = (OfferedSkill.objects
                     .filter(skill=skill, is_active=True)
                     .select_related('user')
                     .order_by('-average_rating', '-total_sessions')[:3])
        
        context['top_tutors'] = top_tutors
        context['total_tutors'] = OfferedSkill.objects.filter(skill=skill, is_active=True).count()
        
        return context


class FindTutorsView(ListView):
    """View to show all tutors who offer a specific skill"""
    model = OfferedSkill
    template_name = 'skills/find_tutors.html'
    context_object_name = 'tutors'
    paginate_by = 12
    
    def get_queryset(self):
        skill_id = self.kwargs['skill_id']
        return (OfferedSkill.objects
                .filter(skill_id=skill_id, is_active=True)
                .select_related('user', 'skill')
                .order_by('-average_rating', '-total_sessions'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skill_id = self.kwargs['skill_id']
        context['skill'] = get_object_or_404(Skill, id=skill_id)
        return context


class TutorProfileView(DetailView):
    """View to show tutor profile with skills and rating"""
    model = User
    template_name = 'skills/tutor_profile.html'
    context_object_name = 'tutor'
    pk_url_kwarg = 'user_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tutor = self.get_object()
        
        # Get all skills offered by this tutor
        offered_skills = (OfferedSkill.objects
                         .filter(user=tutor, is_active=True)
                         .select_related('skill', 'skill__category')
                         .order_by('-average_rating', 'skill__name'))
        
        context['offered_skills'] = offered_skills
        
        # Calculate overall rating
        overall_rating = offered_skills.aggregate(
            avg_rating=Avg('average_rating'),
            total_sessions=Count('total_sessions')
        )
        context['overall_rating'] = overall_rating['avg_rating'] or 0
        context['total_sessions'] = sum([skill.total_sessions for skill in offered_skills])
        
        return context
