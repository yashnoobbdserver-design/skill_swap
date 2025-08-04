from django.contrib import admin
from .models import Department, Branch

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    ordering = ['name']

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'is_active', 'created_at']
    list_filter = ['department', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'department__name']
    list_editable = ['is_active']
    ordering = ['department__name', 'name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department')
