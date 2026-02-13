from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


def _apply_base_input_attrs(field, *, autocomplete=None):
    classes = field.widget.attrs.get("class", "")
    field.widget.attrs["class"] = f"{classes} auth-input".strip()
    if autocomplete:
        field.widget.attrs["autocomplete"] = autocomplete


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"
        _apply_base_input_attrs(self.fields["username"], autocomplete="username")
        _apply_base_input_attrs(self.fields["email"], autocomplete="email")
        _apply_base_input_attrs(self.fields["password1"], autocomplete="new-password")
        _apply_base_input_attrs(self.fields["password2"], autocomplete="new-password")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_base_input_attrs(self.fields["username"], autocomplete="username")
        _apply_base_input_attrs(self.fields["password"], autocomplete="current-password")


class LocalizedPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Текущий пароль", strip=False, widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="Новый пароль", strip=False, widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Подтверждение нового пароля", strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_base_input_attrs(self.fields["old_password"], autocomplete="current-password")
        _apply_base_input_attrs(self.fields["new_password1"], autocomplete="new-password")
        _apply_base_input_attrs(self.fields["new_password2"], autocomplete="new-password")


class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(label="Email", required=True)
    first_name = forms.CharField(label="Имя", max_length=150, required=False)
    last_name = forms.CharField(label="Фамилия", max_length=150, required=False)

    class Meta:
        model = Profile
        fields = ("display_name",)
        labels = {
            "display_name": "Отображаемое имя",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["email"].initial = self.user.email
        self.fields["first_name"].initial = self.user.first_name
        self.fields["last_name"].initial = self.user.last_name
        _apply_base_input_attrs(self.fields["display_name"], autocomplete="nickname")
        _apply_base_input_attrs(self.fields["email"], autocomplete="email")
        _apply_base_input_attrs(self.fields["first_name"], autocomplete="given-name")
        _apply_base_input_attrs(self.fields["last_name"], autocomplete="family-name")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Этот email уже используется другим пользователем.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.email = self.cleaned_data["email"]
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        if commit:
            self.user.save()
            profile.save()
        return profile
