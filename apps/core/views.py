from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Avg
from apps.accounts.models import School, Student, Teacher
from apps.assessments.models import Assessment
from apps.attendance.models import Attendance

def handler404(request, exception):
    """404 - Səhifə tapılmadı"""
    return render(request, '404.html', status=404)

def handler500(request):
    """500 - Server xətası"""
    return render(request, '500.html', status=500)

def handler403(request, exception):
    """403 - İcazə yoxdur"""
    return render(request, '403.html', status=403)

@login_required
def system_statistics(request):
    """Sistem üzrə ümumi statistika"""
    today = timezone.now().date()
    
    context = {
        'total_schools': School.objects.filter(is_active=True).count(),
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_teachers': Teacher.objects.filter(is_active=True).count(),
        
        'attendance_today': Attendance.objects.filter(
            date=today
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(morning_status='present')),
            absent=Count('id', filter=Q(morning_status='absent')),
            late=Count('id', filter=Q(morning_status='late')),
            excused=Count('id', filter=Q(morning_status='excused'))
        ),
        
        'assessment_stats': Assessment.objects.aggregate(
            total=Count('id'),
            avg_grade=Avg('grade')
        ),
        
        'school_stats': School.objects.annotate(
            student_count=Count('student', filter=Q(student__is_active=True)),
            teacher_count=Count('teacher', filter=Q(teacher__is_active=True)),
            avg_grade=Avg('student__assessment__grade')
        ).order_by('-student_count')[:10]
    }
    
    return render(request, 'core/statistics.html', context) 