from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Attendance, AttendanceReport

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student', 
        'date', 
        'get_morning_status_display', 
        'get_afternoon_status_display',
        'school',
        'recorded_by'
    )
    list_filter = (
        'student__school__sector__region',
        'student__school__sector',
        'student__school',
        'date',
        'morning_status',
        'afternoon_status'
    )
    search_fields = (
        'student__first_name',
        'student__last_name',
        'student__utis_code',
        'recorded_by__first_name',
        'recorded_by__last_name'
    )
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('student', 'recorded_by')
    autocomplete_fields = ['student', 'recorded_by']
    date_hierarchy = 'date'
    
    fieldsets = (
        (None, {
            'fields': ('student', 'date')
        }),
        (_('Davamiyyət'), {
            'fields': ('morning_status', 'afternoon_status')
        }),
        (_('Qeydiyyat'), {
            'fields': ('recorded_by', 'excuse_document', 'notes')
        }),
        (_('Tarixlər'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def school(self, obj):
        return obj.student.school
    school.short_description = _('Məktəb')
    
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

@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = (
        'school',
        'report_type',
        'start_date',
        'end_date',
        'total_students',
        'present_count',
        'attendance_rate',
        'generated_by'
    )
    list_filter = (
        'school__sector__region',
        'school__sector',
        'school',
        'report_type',
        'start_date'
    )
    search_fields = (
        'school__name',
        'generated_by__first_name',
        'generated_by__last_name'
    )
    readonly_fields = (
        'total_students',
        'present_count',
        'absent_count',
        'late_count',
        'excused_count',
        'attendance_rate',
        'created_at'
    )
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (None, {
            'fields': ('school', 'report_type', 'start_date', 'end_date')
        }),
        (_('Statistika'), {
            'fields': (
                'total_students',
                'present_count',
                'absent_count',
                'late_count',
                'excused_count',
                'attendance_rate'
            )
        }),
        (_('Qeydiyyat'), {
            'fields': ('generated_by', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.user_type == 'school':
            return qs.filter(school=request.user.managed_school)
        elif request.user.user_type == 'sector':
            return qs.filter(school__sector=request.user.managed_sector)
        elif request.user.user_type == 'region':
            return qs.filter(school__sector__region=request.user.managed_region)
        return qs.none()
    
    def attendance_rate(self, obj):
        return f"{obj.attendance_rate:.1f}%"
    attendance_rate.short_description = _('Davamiyyət faizi') 