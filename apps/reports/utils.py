import csv
from datetime import datetime, timedelta
from django.http import HttpResponse
from apps.attendance.models import Attendance
from apps.assessments.models import Assessment

class ReportGenerator:
    @staticmethod
    def generate_attendance_report(school, start_date, end_date):
        attendance_data = Attendance.objects.filter(
            student__school=school,
            date__range=[start_date, end_date]
        ).select_related('student')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_report_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Tarix', 'Şagird ID', 'Ad', 'Soyad', 'Sinif', 'Səhər', 'Axşam', 'Qeydlər'])
        
        for attendance in attendance_data:
            writer.writerow([
                attendance.date,
                attendance.student.student_id,
                attendance.student.first_name,
                attendance.student.last_name,
                attendance.student.class_grade,
                attendance.get_morning_status_display(),
                attendance.get_afternoon_status_display(),
                attendance.notes
            ])
            
        return response
    
    @staticmethod
    def generate_assessment_report(school, semester, academic_year):
        assessments = Assessment.objects.filter(
            student__school=school,
            semester=semester,
            academic_year=academic_year
        ).select_related('student', 'subject', 'assessment_type')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="assessment_report_{academic_year}_sem{semester}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Şagird ID', 'Ad', 'Soyad', 'Sinif', 'Fənn', 'Qiymətləndirmə növü', 'Qiymət', 'Tarix'])
        
        for assessment in assessments:
            writer.writerow([
                assessment.student.student_id,
                assessment.student.first_name,
                assessment.student.last_name,
                assessment.student.class_grade,
                assessment.subject.name,
                assessment.assessment_type.name,
                assessment.grade,
                assessment.date
            ])
            
        return response 