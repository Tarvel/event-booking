from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "is_organizer",
        ]

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
        ]


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=150)
    password = forms.CharField(label="Password", widget=forms.PasswordInput())
