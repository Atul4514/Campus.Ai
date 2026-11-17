from django import forms
from academics.models import Subject
from .models import StudentProfile


DEFAULT_DEPARTMENT_CHOICES = [
    ('', 'Select Department'),
    ('Computer Science', 'Computer Science'),
    ('Information Technology', 'Information Technology'),
    ('Electronics', 'Electronics'),
    ('Data Science', 'Data Science'),
    ('Mechanical Engineering', 'Mechanical Engineering'),
    ('Civil Engineering', 'Civil Engineering'),
    ('Electrical Engineering', 'Electrical Engineering'),
    ('Management Studies', 'Management Studies'),
    ('Commerce', 'Commerce'),
    ('Applied Sciences', 'Applied Sciences'),
]


class StudentProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Full Name',
        })
    )

    department = forms.ChoiceField(
        required=False,
        label="Department",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_department',
        }),
        choices=DEFAULT_DEPARTMENT_CHOICES,
    )

    class Meta:
        model = StudentProfile
        fields = [
            'profile_photo',
            'phone_number',
            'roll_number',
            'course',
            'year',
            'semester',
            'section',
            'blood_group',
            'date_of_birth',
            'address',
            'guardian_name',
            'guardian_phone',
            'emergency_contact',
        ]
        widgets = {
            'profile_photo': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'id': 'id_profile_photo',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Phone Number',
            }),
            'roll_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Roll Number',
            }),
            'course': forms.Select(attrs={
                'class': 'form-select',
            }),
            'year': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Section (e.g. A, B)',
            }),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address',
            }),
            'guardian_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': "Guardian's Full Name",
            }),
            'guardian_phone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': "Guardian's Phone",
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Emergency Contact Number',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamic department choices combining defaults, database subjects, and user current department
        try:
            db_depts = {
                d.strip() for d in Subject.objects.values_list('department', flat=True).distinct()
                if d and d.strip()
            }
        except Exception:
            db_depts = set()

        dept_choices = list(DEFAULT_DEPARTMENT_CHOICES)
        existing_keys = {k.lower() for k, _ in dept_choices if k}

        for d in sorted(db_depts):
            if d.lower() not in existing_keys:
                dept_choices.append((d, d))
                existing_keys.add(d.lower())

        current_dept = ''
        if self.instance and hasattr(self.instance, 'user') and self.instance.user:
            self.fields['full_name'].initial = self.instance.user.full_name
            current_dept = getattr(self.instance.user, 'department', '') or ''
            if current_dept and current_dept.lower() not in existing_keys:
                dept_choices.append((current_dept, current_dept))
                existing_keys.add(current_dept.lower())

        self.fields['department'].choices = dept_choices
        self.fields['department'].initial = current_dept

        # Ensure course dropdown includes current value if existing value is custom
        if self.instance and self.instance.course:
            existing_courses = {k for k, _ in self.fields['course'].choices}
            if self.instance.course not in existing_courses:
                self.fields['course'].choices = list(self.fields['course'].choices) + [
                    (self.instance.course, self.instance.course)
                ]

    def save(self, commit=True):
        profile = super().save(commit=commit)
        full_name = self.cleaned_data.get('full_name')
        department = self.cleaned_data.get('department')
        if hasattr(profile, 'user') and profile.user:
            update_fields = []
            if full_name is not None and profile.user.full_name != full_name:
                profile.user.full_name = full_name
                update_fields.append('full_name')
            if department is not None and profile.user.department != department:
                profile.user.department = department
                update_fields.append('department')
            if update_fields:
                profile.user.save(update_fields=update_fields)
        return profile
