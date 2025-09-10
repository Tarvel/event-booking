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
    email = forms.EmailField(label="Email", max_length=150)
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


from django import forms
from django.contrib.auth.forms import PasswordChangeForm


class TailwindPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": (
                        "w-full px-4 py-2 bg-white "
                        "border border-slate-300 "
                        "rounded-lg focus:outline-none focus:ring-2 "
                        "focus:ring-green-500 transition-colors"
                    ),
                    "placeholder": field.label,
                }
            )
