from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import Student, Teacher, School

class Subject(models.Model):
    name = models.CharField(_('Ad'), max_length=100)
    code = models.CharField(_('Kod'), max_length=20, unique=True)
    is_active = models.BooleanField(_('Aktivdir'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Fənn')
        verbose_name_plural = _('Fənlər')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class AssessmentType(models.Model):
    name = models.CharField(_('Ad'), max_length=100)
    weight = models.PositiveSmallIntegerField(_('Çəki'), default=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    is_active = models.BooleanField(_('Aktivdir'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Qiymətləndirmə növü')
        verbose_name_plural = _('Qiymətləndirmə növləri')
        ordering = ['name']
        unique_together = ['name', 'school']
    
    def __str__(self):
        return f"{self.name} ({self.school.name})"

class Assessment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    grade = models.PositiveSmallIntegerField(
        _('Qiymət'),
        validators=[MinValueValidator(2), MaxValueValidator(10)]
    )
    semester = models.PositiveSmallIntegerField(_('Semestr'), choices=[(1, '1'), (2, '2')])
    academic_year = models.CharField(_('Tədris ili'), max_length=9)  # format: 2023-2024
    notes = models.TextField(_('Qeydlər'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Qiymətləndirmə')
        verbose_name_plural = _('Qiymətləndirmələr')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'subject', 'semester', 'academic_year']),
            models.Index(fields=['teacher', 'subject', 'assessment_type']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.subject} ({self.grade})"
    
    def save(self, *args, **kwargs):
        # Qiyməti yuvarlaqlaşdır
        if self.grade:
            self.grade = round(self.grade)
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

class SubjectTeacher(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_grade = models.PositiveSmallIntegerField(_('Sinif'))
    is_active = models.BooleanField(_('Aktivdir'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Fənn müəllimi')
        verbose_name_plural = _('Fənn müəllimləri')
        unique_together = ['teacher', 'subject', 'class_grade']
        ordering = ['teacher', 'subject', 'class_grade']
    
    def __str__(self):
        return f"{self.teacher} - {self.subject} ({self.class_grade} sinif)"
    
    @property
    def school(self):
        return self.teacher.school