from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Student, Teacher

ROLE_CHOICES = [
    ('student', 'Student'),
    ('teacher', 'Teacher'),
]

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    full_name = forms.CharField(max_length=255)

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit)
        role = self.cleaned_data['role']
        if role == 'student':
            Student.objects.create(user=user)
        else:
            Teacher.objects.create(user=user)
        return user