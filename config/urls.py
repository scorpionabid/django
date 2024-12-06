from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('assessments/', include('apps.assessments.urls')),
] 