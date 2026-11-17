from django import forms
from .models import AttendanceSession
from academics.models import Subject


class AttendanceSessionForm(forms.ModelForm):
    # These are read-only display fields. Department and semester belong to
    # Subject, so keeping them derived prevents creating inconsistent sessions.
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'aria-readonly': 'true',
        }),
    )
    semester = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'aria-readonly': 'true',
        }),
    )

    class Meta:
        model = AttendanceSession
        fields = ['subject', 'section', 'date', 'topic']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Introduction to Linked Lists'}),
        }
        labels = {
            'topic': 'Lecture Topic (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.order_by('department', 'semester', 'name')
        selected_subject_id = self.data.get('subject') or self.initial.get('subject')
        if selected_subject_id:
            try:
                selected_subject = Subject.objects.get(pk=selected_subject_id)
            except (Subject.DoesNotExist, ValueError, TypeError):
                return
            self.initial['department'] = selected_subject.department
            self.initial['semester'] = selected_subject.semester
