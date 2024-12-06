from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Student, Teacher

@receiver([post_save, post_delete], sender=Student)
def update_student_counts(sender, instance, **kwargs):
    """Şagird əlavə/silindikdə məktəbin şagird sayını yeniləyir"""
    instance.school.update_total_students()

@receiver([post_save, post_delete], sender=Teacher)
def update_teacher_counts(sender, instance, **kwargs):
    """Müəllim əlavə/silindikdə məktəbin müəllim sayını yeniləyir"""
    instance.school.save()  # Bu total_teachers property-ni yeniləyəcək 