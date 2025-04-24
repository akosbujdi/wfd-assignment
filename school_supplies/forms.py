from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Student, Teacher
from .models import Item

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


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ['inv_manage_id', 'created_at']


class EditAccountForm(UserChangeForm):
    full_name = forms.CharField(max_length=100, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'new_password', 'confirm_password']


class ItemUpdateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'quantity', 'image']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required
        for field in self.fields:
            self.fields[field].required = True
