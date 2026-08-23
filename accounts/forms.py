# forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            exists = User.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
            if exists:
                raise forms.ValidationError("This email is already in use.")
        return email