from django.db import models

# Create your models here.

class Department(models.Model):
    """Model for university departments"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Department code (e.g., CSE, ECE)")
    description = models.TextField(blank=True, help_text="Brief description of the department")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        db_table = 'core_department'
    
    def __str__(self):
        return self.name

class Branch(models.Model):
    """Model for department branches/specializations"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, help_text="Branch code (e.g., AI, ML, VLSI)")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='branches')
    description = models.TextField(blank=True, help_text="Brief description of the branch")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = [['department', 'name'], ['department', 'code']]
        db_table = 'core_branch'
    
    def __str__(self):
        return f"{self.department.code} - {self.name}"
