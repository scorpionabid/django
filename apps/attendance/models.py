from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from apps.accounts.models import Student, Teacher, School
from django.utils import timezone

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'İştirak edir'),
        ('absent', 'İştirak etmir'),
        ('late', 'Gecikib'),
        ('excused', 'Üzrlü'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(_('Tarix'), default=timezone.now)
    morning_status = models.CharField(
        _('Səhər statusu'),
        max_length=10,
        choices=STATUS_CHOICES,
        default='present'
    )
    afternoon_status = models.CharField(
        _('Günorta statusu'),
        max_length=10,
        choices=STATUS_CHOICES,
        default='present'
    )
    recorded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    excuse_document = models.FileField(
        _('Üzrlü sənəd'),
        upload_to='excuse_documents/%Y/%m/',
        blank=True,
        null=True
    )
    notes = models.TextField(_('Qeydlər'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Davamiyyət')
        verbose_name_plural = _('Davamiyyət')
        ordering = ['-date', 'student__last_name']
        unique_together = ['student', 'date']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['date', 'morning_status']),
            models.Index(fields=['date', 'afternoon_status']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.date}"
    
    def clean(self):
        # Gələcək tarixə davamiyyət yazılmasın
        if self.date > timezone.now().date():
            raise ValidationError(_('Gələcək tarixə davamiyyət qeyd edilə bilməz'))
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def school(self):
        return self.student.school
    
    @property
    def sector(self):
        return self.student.sector
    
    @property
    def region(self):
        return self.student.region
    
    @property
    def is_fully_present(self):
        return self.morning_status == 'present' and self.afternoon_status == 'present'
    
    @property
    def is_fully_absent(self):
        return self.morning_status == 'absent' and self.afternoon_status == 'absent'

class AttendanceReport(models.Model):
    REPORT_TYPES = (
        ('daily', 'Günlük'),
        ('weekly', 'Həftəlik'),
        ('monthly', 'Aylıq'),
    )
    
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    report_type = models.CharField(_('Hesabat növü'), max_length=10, choices=REPORT_TYPES)
    start_date = models.DateField(_('Başlanğıc tarixi'))
    end_date = models.DateField(_('Bitmə tarixi'))
    total_students = models.PositiveIntegerField(_('Ümumi şagird'))
    present_count = models.PositiveIntegerField(_('İştirak edən'))
    absent_count = models.PositiveIntegerField(_('İştirak etməyən'))
    late_count = models.PositiveIntegerField(_('Gecikən'))
    excused_count = models.PositiveIntegerField(_('Üzrlü'))
    generated_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Davamiyyət hesabatı')
        verbose_name_plural = _('Davamiyyət hesabatları')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'report_type', 'start_date']),
        ]
    
    def __str__(self):
        return f"{self.school} - {self.get_report_type_display()} ({self.start_date})"
    
    @property
    def attendance_rate(self):
        """Davamiyyət faizi"""
        if self.total_students == 0:
            return 0
        return (self.present_count / self.total_students) * 100
    
    @property
    def sector(self):
        return self.school.sector
    
    @property
    def region(self):
        return self.school.region
    