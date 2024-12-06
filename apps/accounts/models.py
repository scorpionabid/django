from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    USER_TYPES = (
        ('school', 'Məktəb'),
        ('sector', 'Sektor'),
        ('region', 'Region'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    utis_code = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    managed_school = models.ForeignKey('School', on_delete=models.SET_NULL, null=True, blank=True)
    managed_sector = models.ForeignKey('Sector', on_delete=models.SET_NULL, null=True, blank=True)
    managed_region = models.ForeignKey('Region', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _('İstifadəçi')
        verbose_name_plural = _('İstifadəçilər')

class Region(models.Model):
    name = models.CharField(_('Ad'), max_length=100)
    code = models.CharField(_('Kod'), max_length=20, unique=True)
    is_active = models.BooleanField(_('Aktivdir'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regionlar')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_students(self):
        return Student.objects.filter(
            school__sector__region=self,
            is_active=True
        ).count()
    
    @property
    def total_schools(self):
        return School.objects.filter(
            sector__region=self,
            is_active=True
        ).count()
    
    @property
    def total_sectors(self):
        return self.sector_set.filter(is_active=True).count()
    
    @property
    def total_teachers(self):
        return Teacher.objects.filter(
            school__sector__region=self,
            is_active=True
        ).count()

class Sector(models.Model):
    name = models.CharField(_('Ad'), max_length=100)
    code = models.CharField(_('Kod'), max_length=20, unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    is_active = models.BooleanField(_('Aktivdir'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Sektor')
        verbose_name_plural = _('Sektorlar')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.region.name})"
    
    @property
    def total_schools(self):
        return self.school_set.filter(is_active=True).count()
    
    @property
    def total_students(self):
        return Student.objects.filter(
            school__sector=self,
            is_active=True
        ).count()
    
    @property
    def total_teachers(self):
        return Teacher.objects.filter(
            school__sector=self,
            is_active=True
        ).count()

class School(models.Model):
    name = models.CharField(_('Ad'), max_length=200)
    code = models.CharField(_('Kod'), max_length=20, unique=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    address = models.TextField(_('Ünvan'), blank=True)
    phone = models.CharField(_('Telefon'), max_length=20, blank=True)
    total_students = models.PositiveIntegerField(_('Şagird sayı'), default=0)
    is_active = models.BooleanField(_('Aktivdir'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Məktəb')
        verbose_name_plural = _('Məktəblər')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sector.name})"
    
    @property
    def region(self):
        return self.sector.region
    
    @property
    def total_teachers(self):
        return self.teacher_set.filter(is_active=True).count()
    
    def update_total_students(self):
        self.total_students = self.student_set.filter(is_active=True).count()
        self.save()

class Student(models.Model):
    first_name = models.CharField(_('Ad'), max_length=50)
    last_name = models.CharField(_('Soyad'), max_length=50)
    utis_code = models.CharField(_('UTIS kodu'), max_length=50, unique=True)
    custom_id = models.CharField(_('Xüsusi ID'), max_length=50, blank=True)
    class_grade = models.PositiveSmallIntegerField(_('Sinif'))
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    parent_phone = models.CharField(_('Valideyn telefonu'), max_length=20, blank=True)
    notes = models.TextField(_('Qeydlər'), blank=True)
    is_active = models.BooleanField(_('Aktivdir'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Şagird')
        verbose_name_plural = _('Şagirdlər')
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def sector(self):
        return self.school.sector
    
    @property
    def region(self):
        return self.school.sector.region

class Teacher(models.Model):
    first_name = models.CharField(_('Ad'), max_length=50)
    last_name = models.CharField(_('Soyad'), max_length=50)
    utis_code = models.CharField(_('UTIS kodu'), max_length=50, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subjects = models.ManyToManyField('assessments.Subject', verbose_name=_('Fənlər'))
    phone = models.CharField(_('Telefon'), max_length=20, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    is_active = models.BooleanField(_('Aktivdir'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Müəllim')
        verbose_name_plural = _('Müəllimlər')
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def sector(self):
        return self.school.sector
    
    @property
    def region(self):
        return self.school.sector.region

class ChangeHistory(models.Model):
    CHANGE_TYPES = (
        ('create', 'Yaradılma'),
        ('update', 'Yenilənmə'),
        ('delete', 'Silinmə'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True)
    change_type = models.CharField(max_length=10, choices=CHANGE_TYPES)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Dəyişiklik tarixi')
        verbose_name_plural = _('Dəyişiklik tarixçəsi')
        ordering = ['-created_at']