import csv
import io
from django.core.exceptions import ValidationError
from .models import User, School, Sector, Region, Student
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from io import BytesIO
from django.utils import timezone

class CSVImporter:
    @staticmethod
    def import_users(csv_file):
        results = {
            'success': 0,
            'errors': []
        }
        
        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            for row in csv_data:
                try:
                    # Məcburi sahələri yoxla
                    required_fields = ['utis_code', 'first_name', 'last_name', 'user_type']
                    for field in required_fields:
                        if not row.get(field):
                            raise ValidationError(f'{field} sahəsi boş ola bilməz')
                    
                    # İstifadəçi növünü yoxla
                    user_type = row['user_type'].lower()
                    if user_type not in ['school', 'sector', 'region']:
                        raise ValidationError(f'Yanlış istifadəçi növü: {user_type}')
                    
                    # UTIS kodu yoxla
                    utis_code = row['utis_code']
                    if not utis_code.endswith('@edu.az'):
                        raise ValidationError(f'Yanlış UTIS kodu: {utis_code}')
                    
                    # İstifadəçi yarat/yenilə
                    user, created = User.objects.update_or_create(
                        utis_code=utis_code,
                        defaults={
                            'username': utis_code,
                            'email': utis_code,
                            'first_name': row['first_name'],
                            'last_name': row['last_name'],
                            'user_type': user_type,
                            'phone': row.get('phone', ''),
                        }
                    )
                    
                    # Əgər yeni istifadəçidirsə, müvəqqəti şifrə təyin et
                    if created:
                        user.set_password('changeme123')
                        user.save()
                    
                    # Məktəb/Sektor/Region əlaqəsini yarat
                    if user_type == 'school' and row.get('school_code'):
                        school = School.objects.get(code=row['school_code'])
                        user.managed_school = school
                    elif user_type == 'sector' and row.get('sector_code'):
                        sector = Sector.objects.get(code=row['sector_code'])
                        user.managed_sector = sector
                    elif user_type == 'region' and row.get('region_code'):
                        region = Region.objects.get(code=row['region_code'])
                        user.managed_region = region
                    
                    user.save()
                    results['success'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"Sətir {csv_data.line_num}: {str(e)}")
                    
        except Exception as e:
            results['errors'].append(f"CSV faylı oxunarkən xəta: {str(e)}")
            
        return results

class CSVExporter:
    @staticmethod
    def export_users():
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Başlıqlar
        headers = [
            'UTIS Kodu', 'Ad', 'Soyad', 'İstifadəçi növü', 
            'Telefon', 'Məktəb/Sektor/Region'
        ]
        writer.writerow(headers)
        
        # Data
        for user in User.objects.all():
            if user.user_type == 'school':
                organization = user.managed_school.name if user.managed_school else ''
            elif user.user_type == 'sector':
                organization = user.managed_sector.name if user.managed_sector else ''
            else:
                organization = user.managed_region.name if user.managed_region else ''
                
            writer.writerow([
                user.utis_code,
                user.first_name,
                user.last_name,
                user.get_user_type_display(),
                user.phone,
                organization
            ])
            
        return output.getvalue()

class StudentCSVImporter:
    @staticmethod
    def import_students(csv_file, school):
        results = {
            'success': 0,
            'errors': []
        }
        
        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            for row in csv_data:
                try:
                    # Məcburi sahələri yoxla
                    required_fields = ['utis_code', 'first_name', 'last_name', 'class_grade']
                    for field in required_fields:
                        if not row.get(field):
                            raise ValidationError(f'{field} sahəsi boş ola bilməz')
                    
                    # UTIS kodu yoxla
                    utis_code = row['utis_code']
                    if not utis_code.endswith('@student.edu.az'):
                        raise ValidationError(f'Yanlış şagird UTIS kodu: {utis_code}')
                    
                    # Sinif yoxla
                    class_grade = row['class_grade']
                    if not class_grade.isdigit() or not (1 <= int(class_grade) <= 11):
                        raise ValidationError(f'Yanlış sinif: {class_grade}')
                    
                    # Şagird yarat/yenilə
                    student, created = Student.objects.update_or_create(
                        utis_code=utis_code,
                        defaults={
                            'first_name': row['first_name'],
                            'last_name': row['last_name'],
                            'class_grade': class_grade,
                            'school': school,
                            'custom_id': row.get('custom_id', ''),
                            'parent_phone': row.get('parent_phone', ''),
                            'notes': row.get('notes', '')
                        }
                    )
                    
                    results['success'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"Sətir {csv_data.line_num}: {str(e)}")
            
            # Məktəb şagird sayını yenilə
            school.update_total_students()
            
        except Exception as e:
            results['errors'].append(f"CSV faylı oxunarkən xəta: {str(e)}")
            
        return results

    @staticmethod
    def download_template():
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'utis_code', 'first_name', 'last_name', 'class_grade',
            'custom_id', 'parent_phone', 'notes'
        ])
        
        # Nümunə data
        writer.writerow([
            'example@student.edu.az', 'Ad', 'Soyad', '5',
            'ID123', '+994501234567', 'Əlavə qeydlər'
        ])
        
        return output.getvalue()

class PDFReportGenerator:
    def __init__(self):
        # Azərbaycan dili üçün font qeydiyyatı
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'static/fonts/DejaVuSans.ttf'))
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            fontName='DejaVuSans',
            fontSize=16,
            spaceAfter=30
        ))
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            fontName='DejaVuSans',
            fontSize=10,
            spaceAfter=12
        ))

    def generate_region_report(self, region, data):
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elements = []
        
        # Başlıq
        title = Paragraph(
            f"{region.name} Region - Hesabat",
            self.styles['CustomTitle']
        )
        elements.append(title)
        
        # Ümumi statistika
        stats_data = [
            ['Göstərici', 'Dəyər'],
            ['Ümumi məktəb', str(data['total_stats']['schools'])],
            ['Ümumi şagird', str(data['total_stats']['students'])],
            ['Ümumi müəllim', str(data['total_stats']['teachers'])],
            ['Orta davamiyyət', f"{data['attendance_rate']:.1f}%"],
            ['Orta qiymət', f"{data['avg_grade']:.2f}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[8*cm, 8*cm])
        stats_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        # Ən yaxşı məktəblər
        elements.append(Paragraph('Ən Yüksək Göstəricili Məktəblər', self.styles['CustomBody']))
        top_schools_data = [['Məktəb', 'Sektor', 'Orta Qiymət']]
        for school in data['top_schools']:
            top_schools_data.append([
                school.name,
                school.sector.name,
                f"{school.avg_grade:.2f}"
            ])
            
        top_schools_table = Table(top_schools_data, colWidths=[8*cm, 5*cm, 3*cm])
        top_schools_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(top_schools_table)
        
        # Hesabat tarixi
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(
            f"Hesabat tarixi: {timezone.now().strftime('%d.%m.%Y %H:%M')}",
            self.styles['CustomBody']
        ))
        
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf