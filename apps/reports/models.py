from django.db import models
from apps.accounts.models import User, School, Sector, Region
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Report(models.Model):
    PERIOD_CHOICES = (
        ('daily', 'Gündəlik'),
        ('weekly', 'Həftəlik'),
        ('monthly', 'Aylıq'),
        ('quarterly', 'Rüblük'),
        ('yearly', 'İllik'),
    )
    
    REPORT_TYPES = (
        ('attendance', 'Davamiyyət'),
        ('assessment', 'Qiymətləndirmə'),
        ('combined', 'Ümumi'),
    )
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Hesabatın aid olduğu məktəb/sektor/region
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Hesabat faylı
    excel_file = models.FileField(upload_to='reports/excel/', null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.get_period_display()}" 