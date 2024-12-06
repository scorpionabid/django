from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('api/v1/', include('apps.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 

admin.site.site_header = 'Məktəb İdarəetmə Sistemi'
admin.site.site_title = 'MİS Admin'
admin.site.index_title = 'İdarəetmə Paneli'

handler404 = 'apps.core.views.handler404'
handler500 = 'apps.core.views.handler500'
handler403 = 'apps.core.views.handler403' 