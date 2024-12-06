from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Attendance, AttendanceReport
from .forms import AttendanceForm, AttendanceReportForm, BulkAttendanceForm

class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Attendance.objects.select_related(
            'student', 'student__school', 'recorded_by'
        )
        
        user = self.request.user
        if user.user_type == 'school':
            queryset = queryset.filter(student__school=user.managed_school)
        elif user.user_type == 'sector':
            queryset = queryset.filter(student__school__sector=user.managed_sector)
        elif user.user_type == 'region':
            queryset = queryset.filter(student__school__sector__region=user.managed_region)
            
        # Tarix filtri
        date = self.request.GET.get('date')
        if date:
            try:
                attendance_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(date=attendance_date)
            except ValueError:
                pass
        else:
            queryset = queryset.filter(date=timezone.now().date())
            
        # Status filtri
        morning_status = self.request.GET.get('morning_status')
        if morning_status:
            queryset = queryset.filter(morning_status=morning_status)
            
        afternoon_status = self.request.GET.get('afternoon_status')
        if afternoon_status:
            queryset = queryset.filter(afternoon_status=afternoon_status)
            
        # Sinif filtri
        class_grade = self.request.GET.get('class_grade')
        if class_grade:
            queryset = queryset.filter(student__class_grade=class_grade)
            
        # Axtarış
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__utis_code__icontains=search)
            )
            
        return queryset.order_by('student__class_grade', 'student__last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Attendance.STATUS_CHOICES
        context['class_grades'] = range(1, 12)
        
        if self.request.user.user_type == 'school':
            context['bulk_form'] = BulkAttendanceForm(
                school=self.request.user.managed_school
            )
            
        return context

class AttendanceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance/attendance_form.html'
    success_url = '/attendance/'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.managed_school
        return kwargs
    
    def form_valid(self, form):
        form.instance.recorded_by = self.request.user.teacher
        messages.success(self.request, 'Davamiyyət uğurla qeyd edildi')
        return super().form_valid(form)

class AttendanceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance/attendance_form.html'
    success_url = '/attendance/'
    
    def test_func(self):
        attendance = self.get_object()
        return (
            self.request.user.user_type == 'school' and 
            attendance.student.school == self.request.user.managed_school
        )
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.managed_school
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Davamiyyət uğurla yeniləndi')
        return super().form_valid(form)

class AttendanceDetailView(LoginRequiredMixin, DetailView):
    model = Attendance
    template_name = 'attendance/attendance_detail.html'
    context_object_name = 'attendance'
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'student', 'student__school', 'recorded_by'
        )
        
        user = self.request.user
        if user.user_type == 'school':
            queryset = queryset.filter(student__school=user.managed_school)
        elif user.user_type == 'sector':
            queryset = queryset.filter(student__school__sector=user.managed_sector)
        elif user.user_type == 'region':
            queryset = queryset.filter(student__school__sector__region=user.managed_region)
            
        return queryset

class AttendanceReportListView(LoginRequiredMixin, ListView):
    model = AttendanceReport
    template_name = 'attendance/report_list.html'
    context_object_name = 'reports'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = AttendanceReport.objects.select_related(
            'school', 'school__sector', 'generated_by'
        )
        
        user = self.request.user
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
                queryset = queryset.filter(start_date__gte=start, end_date__lte=end)
            except ValueError:
                pass
                
        return queryset.order_by('-created_at')

class AttendanceReportCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = AttendanceReport
    form_class = AttendanceReportForm
    template_name = 'attendance/report_form.html'
    success_url = '/attendance/reports/'
    
    def test_func(self):
        return self.request.user.user_type == 'school'
    
    def form_valid(self, form):
        form.instance.school = self.request.user.managed_school
        form.instance.generated_by = self.request.user.teacher
        messages.success(self.request, 'Hesabat uğurla yaradıldı')
        return super().form_valid(form)

def generate_daily_report(request):
    """Gündəlik davamiyyət hesabatı yaradır"""
    if not request.user.is_authenticated or request.user.user_type != 'school':
        return HttpResponseForbidden()
        
    date = request.GET.get('date', timezone.now().date())
    school = request.user.managed_school
    
    try:
        report = AttendanceReport.objects.create_daily_report(
            school=school,
            date=date,
            generated_by=request.user.teacher
        )
        messages.success(request, 'Gündəlik hesabat uğurla yaradıldı')
        
    except Exception as e:
        messages.error(request, f'Xəta baş verdi: {str(e)}')
        
    return redirect('attendance_report_list')

def generate_weekly_report(request):
    """Həftəlik davamiyyət hesabatı yaradır"""
    if not request.user.is_authenticated or request.user.user_type != 'school':
        return HttpResponseForbidden()
        
    end_date = request.GET.get('end_date', timezone.now().date())
    start_date = end_date - timedelta(days=7)
    school = request.user.managed_school
    
    try:
        report = AttendanceReport.objects.create_weekly_report(
            school=school,
            start_date=start_date,
            end_date=end_date,
            generated_by=request.user.teacher
        )
        messages.success(request, 'Həftəlik hesabat uğurla yaradıldı')
        
    except Exception as e:
        messages.error(request, f'Xəta baş verdi: {str(e)}')
        
    return redirect('attendance_report_list')

def generate_monthly_report(request):
    """Aylıq davamiyyət hesabatı yaradır"""
    if not request.user.is_authenticated or request.user.user_type != 'school':
        return HttpResponseForbidden()
        
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    school = request.user.managed_school
    
    try:
        report = AttendanceReport.objects.create_monthly_report(
            school=school,
            year=year,
            month=month,
            generated_by=request.user.teacher
        )
        messages.success(request, 'Aylıq hesabat uğurla yaradıldı')
        
    except Exception as e:
        messages.error(request, f'Xəta baş verdi: {str(e)}')
        
    return redirect('attendance_report_list')