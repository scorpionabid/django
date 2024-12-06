from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, FormView, UpdateView, CreateView, View
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.db.models import Q, Count, Avg, Case, When, FloatField
from django.utils import timezone
from datetime import timedelta
from .models import User, Student, Teacher, School, Region, Sector, ChangeHistory, Subject, SubjectTeacher, Assessment, Attendance
from .forms import StudentImportForm, UserImportForm, ProfileUpdateForm, SubjectTeacherForm, BulkStudentUpdateForm, StudentPromotionForm, StudentGraduationForm, CustomPasswordChangeForm, LoginForm
from django.http import HttpResponseForbidden, HttpResponse
import csv
from django.contrib.auth import update_session_auth_hash
from .utils import PDFReportGenerator

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me', False)
        if not remember_me:
            # Brauzer bağlandıqda session silinir
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Email və ya şifrə yanlışdır')
        return super().form_invalid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()
        
        if user.user_type == 'school':
            school = user.managed_school
            context.update({
                'total_students': Student.objects.filter(school=school, is_active=True).count(),
                'total_teachers': Teacher.objects.filter(school=school, is_active=True).count(),
                'attendance_today': school.get_daily_attendance(today),
                'recent_assessments': school.get_recent_assessments(),
                'class_statistics': school.get_class_statistics(),
                'subject_statistics': school.get_subject_statistics(),
            })
        elif user.user_type == 'sector':
            sector = user.managed_sector
            context.update({
                'total_schools': School.objects.filter(sector=sector, is_active=True).count(),
                'total_students': Student.objects.filter(school__sector=sector, is_active=True).count(),
                'total_teachers': Teacher.objects.filter(school__sector=sector, is_active=True).count(),
                'school_statistics': sector.get_school_statistics(),
            })
        else:  # region
            region = user.managed_region
            context.update({
                'total_sectors': Sector.objects.filter(region=region, is_active=True).count(),
                'total_schools': School.objects.filter(sector__region=region, is_active=True).count(),
                'total_students': Student.objects.filter(school__sector__region=region, is_active=True).count(),
                'sector_statistics': region.get_sector_statistics(),
            })
        
        return context

class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        action = request.POST.get('action')
        
        if action == 'update_profile':
            form = ProfileUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil məlumatlarınız yeniləndi')
            else:
                for error in form.errors.values():
                    messages.error(request, error)
                    
        elif action == 'change_password':
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                messages.success(request, 'Şifrəniz uğurla dəyişdirildi')
            else:
                for error in form.errors.values():
                    messages.error(request, error)
        
        return redirect('profile')

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'accounts/student_list.html'
    context_object_name = 'students'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Student.objects.filter(is_active=True)
        user = self.request.user
        
        # stifadəçi səlahiyyətinə görə filter
        if user.user_type == 'school':
            queryset = queryset.filter(school=user.managed_school)
        elif user.user_type == 'sector':
            queryset = queryset.filter(school__sector=user.managed_sector)
        elif user.user_type == 'region':
            queryset = queryset.filter(school__sector__region=user.managed_region)
        
        # Axtarış
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(utis_code__icontains=search)
            )
        
        # Sinif filtri
        class_grade = self.request.GET.get('class_grade')
        if class_grade:
            queryset = queryset.filter(class_grade=class_grade)
        
        return queryset.select_related('school')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_grades'] = range(1, 12)  # 1-11 siniflər
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'accounts/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Son 30 günün davamiyyəti
        context['recent_attendance'] = student.attendance_set.filter(
            date__gte=timezone.now() - timedelta(days=30)
        ).order_by('-date')
        
        # Son qiymətləndirmələr
        context['recent_assessments'] = student.assessment_set.select_related(
            'subject', 'assessment_type'
        ).order_by('-created_at')[:10]
        
        return context

class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = 'accounts/teacher_list.html'
    context_object_name = 'teachers'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Teacher.objects.filter(is_active=True).select_related(
            'school', 'school__sector', 'school__sector__region'
        ).prefetch_related('subjects')
        
        user = self.request.user
        if user.user_type == 'school':
            queryset = queryset.filter(school=user.managed_school)
        elif user.user_type == 'sector':
            queryset = queryset.filter(school__sector=user.managed_sector)
        elif user.user_type == 'region':
            queryset = queryset.filter(school__sector__region=user.managed_region)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(utis_code__icontains=search) |
                Q(email__icontains=search)
            )
        
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subjects__id=subject)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Fənn filtri üçün
        if user.user_type == 'school':
            context['subjects'] = Subject.objects.filter(
                subjectteacher__teacher__school=user.managed_school
            ).distinct()
        else:
            context['subjects'] = Subject.objects.filter(is_active=True)
            
        return context

class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = Teacher
    template_name = 'accounts/teacher_detail.html'
    context_object_name = 'teacher'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.get_object()
        today = timezone.now().date()
        
        # Müəllimin fənləri və sinifləri
        context['subject_classes'] = teacher.subjectteacher_set.filter(
            is_active=True
        ).select_related('subject').order_by('subject__name', 'class_grade')
        
        # Son qiymətləndirmələr
        context['recent_assessments'] = teacher.assessment_set.select_related(
            'student', 'subject', 'assessment_type'
        ).order_by('-created_at')[:20]
        
        # Statistika
        context['statistics'] = {
            'total_students': teacher.get_total_students(),
            'average_grade': teacher.get_average_grade(),
            'assessment_count': teacher.assessment_set.count(),
            'subjects_count': teacher.subjects.count()
        }
        
        return context

class SchoolListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = School
    template_name = 'accounts/school_list.html'
    context_object_name = 'schools'
    paginate_by = 30
    
    def test_func(self):
        return self.request.user.user_type in ['sector', 'region']
    
    def get_queryset(self):
        queryset = School.objects.filter(is_active=True).select_related(
            'sector', 'sector__region'
        ).annotate(
            student_count=Count('student', filter=Q(student__is_active=True)),
            teacher_count=Count('teacher', filter=Q(teacher__is_active=True)),
            avg_grade=Avg('student__assessment__grade')
        )
        
        user = self.request.user
        if user.user_type == 'sector':
            queryset = queryset.filter(sector=user.managed_sector)
        elif user.user_type == 'region':
            queryset = queryset.filter(sector__region=user.managed_region)
            
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
            
        sector = self.request.GET.get('sector')
        if sector and user.user_type == 'region':
            queryset = queryset.filter(sector_id=sector)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.user_type == 'region':
            context['sectors'] = Sector.objects.filter(
                region=self.request.user.managed_region,
                is_active=True
            )
        return context

class ImportStudentsView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'accounts/import_students.html'
    form_class = StudentImportForm
    success_url = '/students/'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def form_valid(self, form):
        try:
            file = form.cleaned_data['file']
            imported, errors = Student.objects.import_from_csv(
                file, 
                school=self.request.user.managed_school
            )
            
            if imported:
                messages.success(
                    self.request,
                    f'{imported} şagird uğurla idxal edildi'
                )
            
            if errors:
                for error in errors:
                    messages.error(self.request, error)
                    
        except Exception as e:
            messages.error(self.request, f'Xəta baş verdi: {str(e)}')
            
        return super().form_valid(form)

class SchoolDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = School
    template_name = 'accounts/school_detail.html'
    context_object_name = 'school'
    
    def test_func(self):
        user = self.request.user
        school = self.get_object()
        
        if user.user_type == 'school':
            return school == user.managed_school
        elif user.user_type == 'sector':
            return school.sector == user.managed_sector
        elif user.user_type == 'region':
            return school.sector.region == user.managed_region
            
        return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.get_object()
        today = timezone.now().date()
        
        # Əsas statistika
        context['statistics'] = {
            'total_students': school.student_set.filter(is_active=True).count(),
            'total_teachers': school.teacher_set.filter(is_active=True).count(),
            'attendance_rate': school.get_attendance_rate(today),
            'average_grade': school.get_average_grade()
        }
        
        # Sinif statistikası
        context['class_stats'] = school.get_class_statistics()
        
        # Fənn statistikası
        context['subject_stats'] = school.get_subject_statistics()
        
        # Son fəaliyyətlər
        context['recent_activities'] = ChangeHistory.objects.filter(
            school=school
        ).select_related('user').order_by('-created_at')[:20]
        
        return context

class RegionManagerView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/region_manager.html'
    
    def test_func(self):
        return self.request.user.user_type == 'region'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        region = self.request.user.managed_region
        
        # Sektor statistikası
        context['sector_stats'] = Sector.objects.filter(
            region=region,
            is_active=True
        ).annotate(
            school_count=Count('school', filter=Q(school__is_active=True)),
            student_count=Count('school__student', filter=Q(school__student__is_active=True)),
            teacher_count=Count('school__teacher', filter=Q(school__teacher__is_active=True)),
            avg_grade=Avg('school__student__assessment__grade')
        ).order_by('name')
        
        # Ümumi statistika
        context['total_stats'] = {
            'sectors': region.sector_set.filter(is_active=True).count(),
            'schools': School.objects.filter(sector__region=region, is_active=True).count(),
            'students': Student.objects.filter(school__sector__region=region, is_active=True).count(),
            'teachers': Teacher.objects.filter(school__sector__region=region, is_active=True).count()
        }
        
        # Son dəyişikliklər
        context['recent_changes'] = ChangeHistory.objects.filter(
            school__sector__region=region
        ).select_related('user', 'school').order_by('-created_at')[:50]
        
        return context

class ImportUsersView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'accounts/import_users.html'
    form_class = UserImportForm
    success_url = '/region-manager/'
    
    def test_func(self):
        return self.request.user.user_type == 'region'
    
    def form_valid(self, form):
        try:
            file = form.cleaned_data['file']
            user_type = form.cleaned_data['user_type']
            region = self.request.user.managed_region
            
            imported, errors = User.objects.import_from_csv(
                file=file,
                user_type=user_type,
                region=region
            )
            
            if imported:
                messages.success(
                    self.request,
                    f'{imported} istifadəçi uğurla idxal edildi'
                )
            
            if errors:
                for error in errors:
                    messages.error(self.request, error)
                    
        except Exception as e:
            messages.error(self.request, f'Xəta baş verdi: {str(e)}')
            
        return super().form_valid(form)

class HistoryView(LoginRequiredMixin, ListView):
    model = ChangeHistory
    template_name = 'accounts/history.html'
    context_object_name = 'changes'
    paginate_by = 50
    
    def get_queryset(self):
        user = self.request.user
        queryset = ChangeHistory.objects.select_related('user', 'school')
        
        # İstifadəçi səlahiyyətinə görə filter
        if user.user_type == 'school':
            queryset = queryset.filter(school=user.managed_school)
        elif user.user_type == 'sector':
            queryset = queryset.filter(school__sector=user.managed_sector)
        elif user.user_type == 'region':
            queryset = queryset.filter(school__sector__region=user.managed_region)
            
        # Tarix aralığı filtri
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date and end_date:
            try:
                start = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                end = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__range=[start, end])
            except ValueError:
                pass
                
        return queryset.order_by('-created_at')

class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Tarix aralığı
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        if user.user_type == 'school':
            school = user.managed_school
            context.update(school.get_detailed_statistics(start_date, end_date))
            
        elif user.user_type == 'sector':
            sector = user.managed_sector
            context.update(sector.get_detailed_statistics(start_date, end_date))
            
        else:  # region
            region = user.managed_region
            context.update(region.get_detailed_statistics(start_date, end_date))
        
        return context

def download_template(request):
    """İstifadəçi idxalı üçün CSV şablon faylını yükləyir"""
    if not request.user.is_authenticated or request.user.user_type != 'region':
        return HttpResponseForbidden()
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['UTIS Kodu', 'Ad', 'Soyad', 'Email', 'Telefon', 'İstifadəçi növü', 'Məktəb/Sektor kodu'])
    
    return response

def download_student_template(request):
    """Şagird idxalı üçün CSV şablon faylını yükləyir"""
    if not request.user.is_authenticated or request.user.user_type != 'school':
        return HttpResponseForbidden()
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['UTIS Kodu', 'Ad', 'Soyad', 'Sinif', 'Valideyn telefonu', 'Qeydlər'])
    
    return response

class SubjectTeacherCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = SubjectTeacher
    form_class = SubjectTeacherForm
    template_name = 'accounts/subject_teacher_form.html'
    success_url = '/teachers/subjects/'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.managed_school
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Fənn-müəllim əlaqəsi uğurla yaradıldı')
        return super().form_valid(form)

class SubjectTeacherUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SubjectTeacher
    form_class = SubjectTeacherForm
    template_name = 'accounts/subject_teacher_form.html'
    success_url = '/teachers/subjects/'
    
    def test_func(self):
        subject_teacher = self.get_object()
        return (
            self.request.user.user_type == 'school' and 
            subject_teacher.teacher.school == self.request.user.managed_school
        )
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.managed_school
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Fənn-müəllim əlaqəsi uğurla yeniləndi')
        return super().form_valid(form)

class BulkStudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'accounts/bulk_student_update.html'
    form_class = BulkStudentUpdateForm
    success_url = '/students/'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def form_valid(self, form):
        try:
            updated = form.save(school=self.request.user.managed_school)
            messages.success(self.request, f'{updated} şagird uğurla yeniləndi')
        except Exception as e:
            messages.error(self.request, f'Xəta baş verdi: {str(e)}')
        return super().form_valid(form)

class StudentPromotionView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'accounts/student_promotion.html'
    form_class = StudentPromotionForm
    success_url = '/students/'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.managed_school
        return kwargs
    
    def form_valid(self, form):
        try:
            promoted = form.save()
            messages.success(
                self.request, 
                f'{promoted} şagird növbəti sinifə keçirildi'
            )
        except Exception as e:
            messages.error(self.request, f'Xəta baş verdi: {str(e)}')
        return super().form_valid(form)

class StudentGraduationView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'accounts/student_graduation.html'
    form_class = StudentGraduationForm
    success_url = '/students/'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.managed_school
        return kwargs
    
    def form_valid(self, form):
        try:
            graduated = form.save()
            messages.success(
                self.request, 
                f'{graduated} şagird məzun edildi'
            )
        except Exception as e:
            messages.error(self.request, f'Xəta baş verdi: {str(e)}')
        return super().form_valid(form)

class TeacherCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Teacher
    template_name = 'accounts/teacher_form.html'
    fields = ['first_name', 'last_name', 'utis_code', 'email', 'phone', 'subjects']
    success_url = '/teachers/'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def form_valid(self, form):
        form.instance.school = self.request.user.managed_school
        messages.success(self.request, 'Müəllim uğurla əlavə edildi')
        return super().form_valid(form)

class TeacherUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Teacher
    template_name = 'accounts/teacher_form.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'subjects', 'is_active']
    success_url = '/teachers/'
    
    def test_func(self):
        teacher = self.get_object()
        return (
            self.request.user.user_type == 'school' and 
            teacher.school == self.request.user.managed_school
        )
    
    def form_valid(self, form):
        messages.success(self.request, 'Müəllim məlumatları yeniləndi')
        return super().form_valid(form)

class StudentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Student
    template_name = 'accounts/student_form.html'
    fields = ['first_name', 'last_name', 'utis_code', 'class_grade', 'parent_phone', 'notes']
    success_url = '/students/'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def form_valid(self, form):
        form.instance.school = self.request.user.managed_school
        messages.success(self.request, 'Şagird uğurla əlavə edildi')
        return super().form_valid(form)

class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Student
    template_name = 'accounts/student_form.html'
    fields = ['first_name', 'last_name', 'class_grade', 'parent_phone', 'notes', 'is_active']
    success_url = '/students/'
    
    def test_func(self):
        student = self.get_object()
        return (
            self.request.user.user_type == 'school' and 
            student.school == self.request.user.managed_school
        )
    
    def form_valid(self, form):
        messages.success(self.request, 'Şagird məlumatları yeniləndi')
        return super().form_valid(form)

class RegionDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/region_dashboard.html'
    
    def test_func(self):
        return self.request.user.user_type == 'region'
        
    def get(self, request, *args, **kwargs):
        if 'export_pdf' in request.GET:
            return self.export_pdf()
        return super().get(request, *args, **kwargs)
    
    def export_pdf(self):
        region = self.request.user.managed_region
        today = timezone.now().date()
        
        # PDF üçün data hazırla
        data = {
            'total_stats': {
                'schools': School.objects.filter(sector__region=region, is_active=True).count(),
                'students': Student.objects.filter(school__sector__region=region, is_active=True).count(),
                'teachers': Teacher.objects.filter(school__sector__region=region, is_active=True).count(),
            },
            'attendance_rate': Attendance.objects.filter(
                student__school__sector__region=region,
                date=today
            ).aggregate(
                rate=Avg(Case(
                    When(morning_status='present', then=100),
                    default=0,
                    output_field=FloatField(),
                ))
            )['rate'] or 0,
            'avg_grade': Assessment.objects.filter(
                student__school__sector__region=region
            ).aggregate(
                avg=Avg('grade')
            )['avg'] or 0,
            'top_schools': School.objects.filter(
                sector__region=region
            ).annotate(
                avg_grade=Avg('student__assessment__grade')
            ).exclude(
                avg_grade__isnull=True
            ).order_by('-avg_grade')[:5]
        }
        
        # PDF generasiya et
        pdf_generator = PDFReportGenerator()
        pdf = pdf_generator.generate_region_report(region, data)
        
        # PDF faylını yüklə
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{region.name}_hesabat_{today}.pdf"'
        response.write(pdf)
        
        return response

class SectorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/sector_dashboard.html'
    
    def test_func(self):
        return self.request.user.user_type == 'sector'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sector = self.request.user.managed_sector
        today = timezone.now().date()
        
        # Məktəb statistikası
        school_stats = School.objects.filter(
            sector=sector,
            is_active=True
        ).annotate(
            student_count=Count('student', filter=Q(student__is_active=True)),
            teacher_count=Count('teacher', filter=Q(teacher__is_active=True)),
            attendance_rate=Avg(Case(
                When(
                    student__attendance__date=today,
                    student__attendance__morning_status='present',
                    then=100
                ),
                default=0,
                output_field=FloatField(),
            )),
            avg_grade=Avg('student__assessment__grade')
        ).order_by('name')
        
        # Ümumi statistika
        context.update({
            'school_stats': school_stats,
            'total_stats': {
                'schools': school_stats.count(),
                'students': Student.objects.filter(school__sector=sector, is_active=True).count(),
                'teachers': Teacher.objects.filter(school__sector=sector, is_active=True).count(),
            }
        })
        
        return context

class SchoolDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/school_dashboard.html'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.request.user.managed_school
        today = timezone.now().date()
        
        # Bugünkü davamiyyət
        today_attendance = Attendance.objects.filter(
            student__school=school,
            date=today
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(morning_status='present')),
            absent=Count('id', filter=Q(morning_status='absent')),
            late=Count('id', filter=Q(morning_status='late')),
            excused=Count('id', filter=Q(morning_status='excused'))
        )
        
        # Sinif statistikası
        class_stats = Student.objects.filter(
            school=school,
            is_active=True
        ).values('class_grade').annotate(
            total=Count('id'),
            present=Count(
                'attendance',
                filter=Q(attendance__date=today, attendance__morning_status='present')
            )
        ).order_by('class_grade')
        
        # Son qiymətləndirmələr
        recent_assessments = Assessment.objects.filter(
            student__school=school
        ).select_related(
            'student', 'subject', 'assessment_type'
        ).order_by('-created_at')[:10]
        
        context.update({
            'total_stats': {
                'students': Student.objects.filter(school=school, is_active=True).count(),
                'teachers': Teacher.objects.filter(school=school, is_active=True).count(),
            },
            'today_attendance': today_attendance,
            'class_stats': class_stats,
            'recent_assessments': recent_assessments,
            'attendance_rate': (today_attendance['present'] / today_attendance['total'] * 100) if today_attendance['total'] > 0 else 0
        })
        
        return context