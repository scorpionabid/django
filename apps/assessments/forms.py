from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Assessment, AssessmentType, Subject

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['student', 'subject', 'assessment_type', 'grade', 'semester', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'grade': forms.NumberInput(attrs={'min': 1, 'max': 10, 'step': 1})
        }
    
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['student'].queryset = school.student_set.filter(is_active=True)
            self.fields['subject'].queryset = Subject.objects.filter(
                subjectteacher__teacher__school=school,
                subjectteacher__is_active=True
            ).distinct()
            self.fields['assessment_type'].queryset = AssessmentType.objects.filter(
                school=school,
                is_active=True
            )
            
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class BulkAssessmentForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assessment_type = forms.ModelChoiceField(
        queryset=AssessmentType.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class_grade = forms.ChoiceField(
        choices=[(i, f'{i}-ci sinif') for i in range(1, 12)],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    semester = forms.ChoiceField(
        choices=[(1, '1-ci semestr'), (2, '2-ci semestr')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['subject'].queryset = Subject.objects.filter(
                subjectteacher__teacher__school=school,
                subjectteacher__is_active=True
            ).distinct()
            self.fields['assessment_type'].queryset = AssessmentType.objects.filter(
                school=school,
                is_active=True
            )

class AssessmentTypeForm(forms.ModelForm):
    class Meta:
        model = AssessmentType
        fields = ['name', 'weight', 'min_required', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'weight': forms.NumberInput(attrs={'min': 1, 'max': 100}),
            'min_required': forms.NumberInput(attrs={'min': 0, 'max': 10})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class AssessmentFilterForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        required=False,
        empty_label="Bütün fənlər",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assessment_type = forms.ModelChoiceField(
        queryset=AssessmentType.objects.none(),
        required=False,
        empty_label="Bütün növlər",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class_grade = forms.ChoiceField(
        choices=[('', 'Bütün siniflər')] + [(i, f'{i}-ci sinif') for i in range(1, 12)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    semester = forms.ChoiceField(
        choices=[('', 'Bütün semestrlər'), (1, '1-ci semestr'), (2, '2-ci semestr')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_grade = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min'})
    )
    
    max_grade = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max'})
    )
    
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['subject'].queryset = Subject.objects.filter(
                subjectteacher__teacher__school=school,
                subjectteacher__is_active=True
            ).distinct()
            self.fields['assessment_type'].queryset = AssessmentType.objects.filter(
                school=school,
                is_active=True
            ) 