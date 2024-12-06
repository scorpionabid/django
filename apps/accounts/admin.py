from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Region, Sector, School, Student, Teacher, ChangeHistory

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'utis_code')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Şəxsi məlumatlar'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('İdarəetmə'), {'fields': ('user_type', 'managed_school', 'managed_sector', 'managed_region')}),
        (_('İcazələr'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'total_sectors', 'total_schools', 'total_students', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region', 'total_schools', 'total_students', 'is_active')
    list_filter = ('region', 'is_active')
    search_fields = ('name', 'code', 'region__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'sector', 'total_students', 'total_teachers', 'is_active')
    list_filter = ('sector__region', 'sector', 'is_active')
    search_fields = ('name', 'code', 'sector__name', 'sector__region__name')
    readonly_fields = ('created_at', 'updated_at', 'total_students')
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'sector', 'is_active')
        }),
        (_('Əlaqə'), {
            'fields': ('address', 'phone')
        }),
        (_('Statistika'), {
            'fields': ('total_students',)
        }),
        (_('Tarixlər'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'utis_code', 'school', 'class_grade', 'is_active')
    list_filter = ('school__sector__region', 'school__sector', 'school', 'class_grade', 'is_active')
    search_fields = ('first_name', 'last_name', 'utis_code', 'custom_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'utis_code', 'custom_id', 'is_active')
        }),
        (_('Məktəb məlumatları'), {
            'fields': ('school', 'class_grade')
        }),
        (_('Əlaqə'), {
            'fields': ('parent_phone', 'notes')
        }),
        (_('Tarixlər'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'utis_code', 'school', 'email', 'is_active')
    list_filter = ('school__sector__region', 'school__sector', 'school', 'is_active')
    search_fields = ('first_name', 'last_name', 'utis_code', 'email')
    filter_horizontal = ('subjects',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'utis_code', 'is_active')
        }),
        (_('Məktəb məlumatları'), {
            'fields': ('school', 'subjects')
        }),
        (_('Əlaqə'), {
            'fields': ('phone', 'email')
        }),
        (_('Tarixlər'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ChangeHistory)
class ChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'change_type', 'model_name', 'created_at')
    list_filter = ('change_type', 'model_name', 'school__sector__region', 'school__sector', 'school')
    search_fields = ('user__username', 'description', 'school__name')
    readonly_fields = ('created_at',) 