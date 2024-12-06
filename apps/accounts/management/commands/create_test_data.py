from django.core.management.base import BaseCommand
from apps.accounts.models import Region, Sector, School, User, Student, Teacher
from apps.assessments.models import Subject, AssessmentType
import random

class Command(BaseCommand):
    help = 'Test datası yaradır'

    def handle(self, *args, **kwargs):
        # Region
        region = Region.objects.create(name="Bakı", code="BAK01")
        
        # Sektor
        sector = Sector.objects.create(name="Xətai", code="XET01", region=region)
        
        # Məktəb
        school = School.objects.create(
            name="289 nömrəli məktəb",
            code="SCH289",
            sector=sector
        )
        
        # İstifadəçilər
        region_user = User.objects.create_user(
            username='region@edu.az',
            password='region123',
            user_type='region',
            managed_region=region
        )
        
        sector_user = User.objects.create_user(
            username='sector@edu.az',
            password='sector123',
            user_type='sector',
            managed_sector=sector
        )
        
        school_user = User.objects.create_user(
            username='school@edu.az',
            password='school123',
            user_type='school',
            managed_school=school
        )
        
        # Fənlər
        subjects = [
            Subject.objects.create(name="Riyaziyyat", code="MATH"),
            Subject.objects.create(name="Azərbaycan dili", code="AZE"),
            Subject.objects.create(name="Fizika", code="PHY")
        ]
        
        # Qiymətləndirmə növləri
        assessment_types = [
            AssessmentType.objects.create(name="KSQ", weight=40, school=school),
            AssessmentType.objects.create(name="BSQ", weight=60, school=school)
        ]
        
        # Müəllimlər
        for i in range(5):
            teacher = Teacher.objects.create(
                first_name=f"Müəllim{i}",
                last_name=f"Soyadı{i}",
                utis_code=f"teacher{i}@edu.az",
                school=school
            )
            teacher.subjects.add(*random.sample(list(subjects), 2))
        
        # Şagirdlər
        for i in range(20):
            Student.objects.create(
                first_name=f"Şagird{i}",
                last_name=f"Soyadı{i}",
                utis_code=f"student{i}@student.edu.az",
                class_grade=random.randint(1, 11),
                school=school
            )
        
        self.stdout.write(self.style.SUCCESS('Test datası uğurla yaradıldı')) 