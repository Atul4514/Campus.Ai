from django import forms
from django.contrib.auth import get_user_model
from .models import CollegeIDAllowlist
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

User = get_user_model()

from django.contrib.auth.forms import PasswordResetForm

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'college_id', 'department', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Display Name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'college_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'College ID'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
        }
    # ... rest stays the same (clean_college_id, clean, save methods unchanged)

class StyledPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )

    def send_mail(self, *args, **kwargs):
        print("Password reset email is being sent...")
        return super().send_mail(*args, **kwargs)


class StyledSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )



class RegisterForm(forms.ModelForm):
    YEAR_CHOICES = [
        ('', 'Select Year'),
        ('First Year', 'First Year'),
        ('Second Year', 'Second Year'),
        ('Third Year', 'Third Year'),
        ('Fourth Year', 'Fourth Year'),
    ]
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'college_id', 'department', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Display Name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'college_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'College ID'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
        }

    def clean_college_id(self):
        college_id = self.cleaned_data['college_id']
        try:
            entry = CollegeIDAllowlist.objects.get(college_id=college_id)
        except CollegeIDAllowlist.DoesNotExist:
            raise forms.ValidationError("Invalid college ID. Not in allowlist.")
        if entry.is_used:
            raise forms.ValidationError("This college ID is already registered.")
        return college_id

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        allowlist_entry = CollegeIDAllowlist.objects.get(college_id=self.cleaned_data['college_id'])
        user.role = allowlist_entry.role
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            allowlist_entry.is_used = True
            allowlist_entry.save()
            if user.role == 'student':
                from student_management.models import StudentProfile
                profile, created = StudentProfile.objects.get_or_create(user=user)
                if self.cleaned_data.get('year'):
                    profile.year = self.cleaned_data['year']
                    profile.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
