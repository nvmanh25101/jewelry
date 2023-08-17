from django import forms
import re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class SignupForm(forms.Form):
    username = forms.CharField(max_length=30, label="Username")
    email = forms.EmailField(max_length=100, label="Email")
    fist_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")
    password1 = forms.CharField(
        max_length=100, label="Password", widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        max_length=100, label="Confirm Password", widget=forms.PasswordInput()
    )

    def clean_password2(self):
        if "password1" in self.cleaned_data:
            password1 = self.cleaned_data["password1"]
            password2 = self.cleaned_data["password2"]

            if password2 == password1 and password1:
                return password2
        raise forms.ValidationError("Password does not match")

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not re.search(r"^\w+$", username):
            raise forms.ValidationError(
                "Username can only contain alphanumeric characters and the underscore."
            )
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError("Username is already taken.")

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["fist_name"],
            last_name=self.cleaned_data["last_name"],
        )
        return user


class UpdateProfileForm(forms.Form):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop("username", None)
        super().__init__(*args, **kwargs)

    def save(self):
        user = User.objects.filter(username=self.username).update(
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )
