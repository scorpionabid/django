from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils import timezone
from .models import Assessment, AssessmentType, Subject, SubjectTeacher
from .forms import AssessmentForm, AssessmentTypeForm, SubjectTeacherForm

class AssessmentListView(LoginRequiredMixin, ListView):
    model = Assessment
    template_name = 'assessments/assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Assessment.objects.select_related(
            'student', 'subject', 'assessment_type', 'teacher'
        )
        
        user = self.request.user
        if user.user_type == 'school':
            queryset = queryset.filter(student__school=user.managed_school)
        elif user.user_type == 'sector':
            queryset = queryset.filter(student__school__sector=user.managed_sector)
        elif user.user_type == 'region':
            queryset = queryset.filter(student__school__sector__region=user.managed_region)
            
        # Filtrlər
        filters = {}
        
        subject = self.request.GET.get('subject')
        if subject:
            filters['subject_id'] = subject
            
        class_grade = self.request.GET.get('class_grade')
        if class_grade:
            filters['student__class_grade'] = class_grade
            
        assessment_type = self.request.GET.get('assessment_type')
        if assessment_type:
            filters['assessment_type_id'] = assessment_type
            
        semester = self.request.GET.get('semester')
        if semester:
            filters['semester'] = semester
            
        if filters:
            queryset = queryset.filter(**filters)
            
        # Axtarış
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__utis_code__icontains=search)
            )
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Filter seçimləri üçün məlumatlar
        if user.user_type == 'school':
            context['subjects'] = Subject.objects.filter(
                subjectteacher__teacher__school=user.managed_school,
                subjectteacher__is_active=True
            ).distinct()
            context['assessment_types'] = AssessmentType.objects.filter(
                school=user.managed_school,
                is_active=True
            )
        else:
            context['subjects'] = Subject.objects.filter(is_active=True)
            
        context['class_grades'] = range(1, 12)
        context['semesters'] = [1, 2]
        
        return context

class AssessmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Assessment
    form_class = AssessmentForm
    template_name = 'assessments/assessment_form.html'
    success_url = '/assessments/'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.managed_school
        return kwargs
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher
        messages.success(self.request, 'Qiymətləndirmə uğurla əlavə edildi')
        return super().form_valid(form)

class AssessmentDetailView(LoginRequiredMixin, DetailView):
    model = Assessment
    template_name = 'assessments/assessment_detail.html'
    context_object_name = 'assessment'
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'student', 'subject', 'assessment_type', 'teacher',
            'student__school', 'student__school__sector'
        )
        
        user = self.request.user
        if user.user_type == 'school':
            queryset = queryset.filter(student__school=user.managed_school)
        elif user.user_type == 'sector':
            queryset = queryset.filter(student__school__sector=user.managed_sector)
        elif user.user_type == 'region':
            queryset = queryset.filter(student__school__sector__region=user.managed_region)
            
        return queryset

class AssessmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Assessment
    form_class = AssessmentForm
    template_name = 'assessments/assessment_form.html'
    success_url = '/assessments/'
    
    def test_func(self):
        assessment = self.get_object()
        return (
            self.request.user.user_type == 'school' and 
            assessment.student.school == self.request.user.managed_school and
            assessment.teacher == self.request.user.teacher
        )
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.managed_school
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Qiymətləndirmə uğurla yeniləndi')
        return super().form_valid(form)

class AssessmentTypeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AssessmentType
    template_name = 'assessments/assessment_type_list.html'
    context_object_name = 'assessment_types'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def get_queryset(self):
        return AssessmentType.objects.filter(
            school=self.request.user.managed_school,
            is_active=True
        ).order_by('name')

class AssessmentTypeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = AssessmentType
    form_class = AssessmentTypeForm
    template_name = 'assessments/assessment_type_form.html'
    success_url = '/assessments/types/'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def form_valid(self, form):
        form.instance.school = self.request.user.managed_school
        messages.success(self.request, 'Qiymətləndirmə növü uğurla əlavə edildi')
        return super().form_valid(form)

class AssessmentTypeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AssessmentType
    form_class = AssessmentTypeForm
    template_name = 'assessments/assessment_type_form.html'
    success_url = '/assessments/types/'
    
    def test_func(self):
        assessment_type = self.get_object()
        return (
            self.request.user.user_type == 'school' and 
            assessment_type.school == self.request.user.managed_school
        )
    
    def form_valid(self, form):
        messages.success(self.request, 'Qiymətləndirmə növü uğurla yeniləndi')
        return super().form_valid(form)

class SubjectTeacherListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = SubjectTeacher
    template_name = 'assessments/subject_teacher_list.html'
    context_object_name = 'subject_teachers'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def get_queryset(self):
        return SubjectTeacher.objects.filter(
            teacher__school=self.request.user.managed_school,
            is_active=True
        ).select_related('teacher', 'subject').order_by(
            'subject__name', 'class_grade', 'teacher__last_name'
        )

class AssessmentStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'assessments/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Tarix aralığı
        end_date = timezone.now().date()
        start_date = end_date.replace(month=1, day=1)  # İlin əvvəli
        
        # Statistika məlumatları
        if user.user_type == 'school':
            school = user.managed_school
            context.update({
                'class_stats': school.get_class_assessment_statistics(start_date, end_date),
                'subject_stats': school.get_subject_assessment_statistics(start_date, end_date),
                'teacher_stats': school.get_teacher_assessment_statistics(start_date, end_date),
                'type_stats': school.get_assessment_type_statistics(start_date, end_date)
            })
        elif user.user_type == 'sector':
            sector = user.managed_sector
            context.update({
                'school_stats': sector.get_school_assessment_statistics(start_date, end_date),
                'subject_stats': sector.get_subject_assessment_statistics(start_date, end_date)
            })
        else:  # region
            region = user.managed_region
            context.update({
                'sector_stats': region.get_sector_assessment_statistics(start_date, end_date),
                'subject_stats': region.get_subject_assessment_statistics(start_date, end_date)
            })
        
        return context