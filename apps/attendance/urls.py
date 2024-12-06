from django.urls import path
from .views import (
    AttendanceListView,
    AttendanceDetailView,
    AttendanceCreateView,
    AttendanceUpdateView,
    AttendanceReportListView,
    AttendanceReportDetailView,
    AttendanceReportCreateView,
    generate_daily_report,
    generate_weekly_report,
    generate_monthly_report,
)

urlpatterns = [
    # Gündəlik davamiyyət
    path('', AttendanceListView.as_view(), name='attendance_list'),
    path('<int:pk>/', AttendanceDetailView.as_view(), name='attendance_detail'),
    path('create/', AttendanceCreateView.as_view(), name='attendance_create'),
    path('<int:pk>/update/', AttendanceUpdateView.as_view(), name='attendance_update'),
    
    # Hesabatlar
    path('reports/', AttendanceReportListView.as_view(), name='attendance_report_list'),
    path('reports/<int:pk>/', AttendanceReportDetailView.as_view(), name='attendance_report_detail'),
    path('reports/create/', AttendanceReportCreateView.as_view(), name='attendance_report_create'),
    path('reports/generate/daily/', generate_daily_report, name='generate_daily_report'),
    path('reports/generate/weekly/', generate_weekly_report, name='generate_weekly_report'),
    path('reports/generate/monthly/', generate_monthly_report, name='generate_monthly_report'),
] 