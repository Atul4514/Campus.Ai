from django import forms
from .models import FacultyProfile, SubjectAssignment
from academics.models import Subject
from django.contrib.auth import get_user_model

User = get_user_model()


class FacultyProfileEditForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150, required=False, label='Full Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Faculty full name'})
    )
    department = forms.CharField(
        max_length=100, required=False, label='Department',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science'})
    )
    phone = forms.CharField(
        max_length=15, required=False, label='Phone',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'})
    )

    class Meta:
        model = FacultyProfile
        fields = ['employee_id', 'designation', 'qualification', 'experience_years', 'joined_date']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee ID'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. M.Tech, PhD'}),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0, 'max': 60,
                'placeholder': 'Years of teaching experience (e.g. 5)',
            }),
            'joined_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['full_name'].initial = self.instance.user.full_name
            self.fields['department'].initial = self.instance.user.department
            self.fields['phone'].initial = self.instance.user.phone

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if commit:
            user = profile.user
            full_name = self.cleaned_data.get('full_name')
            department = self.cleaned_data.get('department')
            phone = self.cleaned_data.get('phone')
            changed = []
            if full_name is not None:
                user.full_name = full_name
                changed.append('full_name')
            if department is not None:
                user.department = department
                changed.append('department')
            if phone is not None:
                user.phone = phone
                changed.append('phone')
            if changed:
                user.save(update_fields=changed)
        return profile


class SubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = SubjectAssignment
        fields = ['subject', 'section']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Section (optional, e.g. A)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.order_by('department', 'semester', 'name')
