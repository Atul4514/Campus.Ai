from django import forms
from .models import StudentProfile


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
            'course': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. B.Tech CSE, MBA, BCA',
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
        if self.instance and hasattr(self.instance, 'user') and self.instance.user:
            self.fields['full_name'].initial = self.instance.user.full_name

    def save(self, commit=True):
        profile = super().save(commit=commit)
        full_name = self.cleaned_data.get('full_name')
        if full_name is not None and hasattr(profile, 'user') and profile.user:
            profile.user.full_name = full_name
            profile.user.save(update_fields=['full_name'])
        return profile
