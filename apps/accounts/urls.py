from django.urls import path
from . import views

urlpatterns = [
    # Auth URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Student URLs
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/add/', views.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_update'),
    path('students/import/', views.ImportStudentsView.as_view(), name='import_students'),
    path('students/bulk-update/', views.BulkStudentUpdateView.as_view(), name='bulk_student_update'),
    path('students/promotion/', views.StudentPromotionView.as_view(), name='student_promotion'),
    path('students/graduation/', views.StudentGraduationView.as_view(), name='student_graduation'),
    
    # Teacher URLs
    path('teachers/', views.TeacherListView.as_view(), name='teacher_list'),
    path('teachers/<int:pk>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
    path('teachers/add/', views.TeacherCreateView.as_view(), name='teacher_create'),
    path('teachers/<int:pk>/edit/', views.TeacherUpdateView.as_view(), name='teacher_update'),
    path('teachers/subjects/', views.SubjectTeacherListView.as_view(), name='subject_teacher_list'),
    path('teachers/subjects/add/', views.SubjectTeacherCreateView.as_view(), name='subject_teacher_create'),
    path('teachers/subjects/<int:pk>/edit/', views.SubjectTeacherUpdateView.as_view(), name='subject_teacher_update'),
    
    # School URLs
    path('schools/', views.SchoolListView.as_view(), name='school_list'),
    path('schools/<int:pk>/', views.SchoolDetailView.as_view(), name='school_detail'),
    
    # Region Manager URLs
    path('region-manager/', views.RegionManagerView.as_view(), name='region_manager'),
    path('region-manager/import-users/', views.ImportUsersView.as_view(), name='import_users'),
    
    # History & Statistics
    path('history/', views.HistoryView.as_view(), name='history'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    
    # Templates
    path('templates/user/', views.download_template, name='user_template'),
    path('templates/student/', views.download_student_template, name='student_template'),
] 