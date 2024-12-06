from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Subject, AssessmentType, Assessment, SubjectTeacher

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'is_active')
        }),
        (_('Tarixlər'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AssessmentType)
class AssessmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'weight', 'is_active')
    list_filter = ('school__sector__region', 'school__sector', 'school', 'is_active')
    search_fields = ('name', 'school__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'school', 'weight', 'is_active')
        }),
        (_('Tarixlər'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'grade', 'assessment_type', 'semester', 'academic_year', 'teacher')
    list_filter = (
        'student__school__sector__region',
        'student__school__sector',
        'student__school',
        'subject',
        'assessment_type',
        'semester',
        'academic_year'
    )
    search_fields = (
        'student__first_name',
        'student__last_name',
        'student__utis_code',
        'teacher__first_name',
        'teacher__last_name'
    )
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('student', 'teacher')
    autocomplete_fields = ['student', 'teacher']
    fieldsets = (
        (None, {
            'fields': ('student', 'subject', 'assessment_type', 'grade')
        }),
        (_('Tədris dövrü'), {
            'fields': ('semester', 'academic_year')
        }),
        (_('Müəllim və qeydlər'), {
            'fields': ('teacher', 'notes')
        }),
        (_('Tarixlər'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.user_type == 'school':
            return qs.filter(student__school=request.user.managed_school)
        elif request.user.user_type == 'sector':
            return qs.filter(student__school__sector=request.user.managed_sector)
        elif request.user.user_type == 'region':
            return qs.filter(student__school__sector__region=request.user.managed_region)
        return qs.none()

@admin.register(SubjectTeacher)
class SubjectTeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'class_grade', 'school', 'is_active')
    list_filter = (
        'teacher__school__sector__region',
        'teacher__school__sector',
        'teacher__school',
        'subject',
        'class_grade',
        'is_active'
    )
    search_fields = (
        'teacher__first_name',
        'teacher__last_name',
        'teacher__utis_code',
        'subject__name'
    )
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('teacher',)
    autocomplete_fields = ['teacher']
    
    def school(self, obj):
        return obj.teacher.school
    school.short_description = _('Məktəb')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.user_type == 'school':
            return qs.filter(teacher__school=request.user.managed_school)
        elif request.user.user_type == 'sector':
            return qs.filter(teacher__school__sector=request.user.managed_sector)
        elif request.user.user_type == 'region':
            return qs.filter(teacher__school__sector__region=request.user.managed_region)
        return qs.none() 