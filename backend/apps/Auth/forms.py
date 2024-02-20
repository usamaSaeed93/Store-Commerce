from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField

User = get_user_model()


class RegisterForm(forms.ModelForm):
    """
    The default

    """

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email"]

    def clean_email(self):
        """
        Verify email is available.
        """
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email


class UserAdminCreationForm(forms.ModelForm):
    """
    This is user admin creation form
    """

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """
    This is user admin change form
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "is_active",
        ]

    def clean_password(self):
        return self.initial["password"]
