from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect

class DashboardView(LoginRequiredMixin):
    def get_template_names(self):
        user_type = self.request.user.user_type
        templates = {
            'school': 'dashboard/school.html',
            'sector': 'dashboard/sector.html',
            'region': 'dashboard/region.html'
        }
        return [templates.get(user_type, 'dashboard/school.html')]
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.user_type == 'school':
            context['school'] = user.managed_school
            context['teachers'] = user.managed_school.teacher_set.all()
            
        elif user.user_type == 'sector':
            context['sector'] = user.managed_sector
            context['schools'] = user.managed_sector.school_set.all()
            
        elif user.user_type == 'region':
            context['region'] = user.managed_region
            context['sectors'] = user.managed_region.sector_set.all()
            
        return context 