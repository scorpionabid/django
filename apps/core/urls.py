from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('statistics/', views.system_statistics, name='system_statistics'),
] 