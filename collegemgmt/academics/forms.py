from django import forms
from .models import TimetableEntry, StudyMaterial, Notice, Subject


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        for name in ('department', 'semester', 'section'):
            if name in self.fields:
                self.fields[name].help_text = 'Use the exact student profile values.'


class SubjectForm(StyledModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'department', 'semester']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Data Structures'}),
            'department': forms.TextInput(attrs={'placeholder': 'e.g. Computer Science'}),
            'semester': forms.NumberInput(attrs={'min': 1, 'max': 8}),
        }

    def clean_semester(self):
        semester = self.cleaned_data['semester']
        if not 1 <= semester <= 8:
            raise forms.ValidationError('Semester must be between 1 and 8.')
        return semester


from django.contrib.auth import get_user_model

User = get_user_model()


class TimetableForm(StyledModelForm):
    faculty = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['faculty', 'admin']).order_by('full_name'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Assign Faculty Member',
        empty_label='-- Select Faculty Member --',
    )

    class Meta:
        model = TimetableEntry
        fields = ['faculty', 'subject', 'section', 'day_of_week', 'start_time', 'end_time', 'room']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, is_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.order_by('department', 'semester', 'name')
        if not is_admin:
            self.fields.pop('faculty', None)
        else:
            self.fields['faculty'].required = True

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('start_time') and cleaned.get('end_time') and cleaned['start_time'] >= cleaned['end_time']:
            self.add_error('end_time', 'End time must be after start time.')
        return cleaned


class StudyMaterialForm(StyledModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'subject', 'section', 'description', 'file']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.order_by('department', 'semester', 'name')


class NoticeForm(StyledModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'body', 'subject', 'department', 'semester', 'section', 'attachment', 'is_pinned']
        widgets = {'body': forms.Textarea(attrs={'rows': 4}), 'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.order_by('department', 'semester', 'name')
        self.fields['subject'].required = False
