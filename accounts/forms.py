from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full bg-transparent border-0 p-0 text-sm font-semibold text-black focus:ring-0 focus:outline-none placeholder:text-neutral-400",
                    "placeholder": "Your first name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full bg-transparent border-0 p-0 text-sm font-semibold text-black focus:ring-0 focus:outline-none placeholder:text-neutral-400",
                    "placeholder": "Your last name",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "w-full bg-transparent border-0 p-0 text-sm font-semibold text-black focus:ring-0 focus:outline-none placeholder:text-neutral-400",
                    "placeholder": "username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full bg-transparent border-0 p-0 text-sm font-semibold text-black focus:ring-0 focus:outline-none placeholder:text-neutral-400",
                    "placeholder": "you@example.com",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            exists = User.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
            if exists:
                raise forms.ValidationError("This email is already in use.")
        return email