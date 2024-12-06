from django.urls import path
from .views import (
    AssessmentListView,
    AssessmentDetailView,
    AssessmentCreateView,
    AssessmentUpdateView,
    AssessmentTypeListView,
    AssessmentTypeCreateView,
    AssessmentTypeUpdateView,
    SubjectTeacherListView,
    SubjectTeacherCreateView,
    SubjectTeacherUpdateView,
    AssessmentStatisticsView,
)

urlpatterns = [
    # Qiymətləndirmə
    path('', AssessmentListView.as_view(), name='assessment_list'),
    path('<int:pk>/', AssessmentDetailView.as_view(), name='assessment_detail'),
    path('create/', AssessmentCreateView.as_view(), name='assessment_create'),
    path('<int:pk>/update/', AssessmentUpdateView.as_view(), name='assessment_update'),
    
    # Qiymətləndirmə növləri
    path('types/', AssessmentTypeListView.as_view(), name='assessment_type_list'),
    path('types/create/', AssessmentTypeCreateView.as_view(), name='assessment_type_create'),
    path('types/<int:pk>/update/', AssessmentTypeUpdateView.as_view(), name='assessment_type_update'),
    
    # Fənn müəllimləri
    path('subject-teachers/', SubjectTeacherListView.as_view(), name='subject_teacher_list'),
    path('subject-teachers/create/', SubjectTeacherCreateView.as_view(), name='subject_teacher_create'),
    path('subject-teachers/<int:pk>/update/', SubjectTeacherUpdateView.as_view(), name='subject_teacher_update'),
    
    # Statistika
    path('statistics/', AssessmentStatisticsView.as_view(), name='assessment_statistics'),
] 