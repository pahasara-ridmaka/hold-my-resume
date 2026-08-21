from django import forms

from .models import Application, Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "website", "location"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Google"}
            ),
            "website": forms.URLInput(
                attrs={"class": "form-control", "palceholder": "https://..."}
            ),
            "location": forms.TextInput(
                attrs={"class": "forma-control", "placeholder": "e.g. Colombo / Remote"}
            ),
        }


class ApplicationForm(forms.ModelForm):
    company_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "e.g. Google"}
        ),
    )

    class Meta:
        model = Application
        fields = [
            "job_title",
            "job_url",
            "job_description",
            "status",
            "platform",
            "salary_estimate",
            "applied_date",
            "resume_file",
            "cover_letter_file",
        ]

        widgets = {
            "job_title": forms.TextInput(
                attrs={
                    "class": "form-control",
                      "placeholder": "e.g. Software Engineer"
                      }
            ),
            "job_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://..."}
            ),
            "job_description": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Job description..."}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "platform": forms.Select(attrs={"class": "form-control"}),
            "salary_estimate": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "e.g. 100000"}
            ),
            "resume_file": forms.ClearableFileInput(
                attrs={"class": "form-control-file"}
            ),
            "cover_letter_file": forms.ClearableFileInput(
                attrs={"class": "form-control-file"}
            ),
            'applied_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'w-full bg-transparent focus:outline-none font-bold text-sm text-black',
                }
            ),
        }

