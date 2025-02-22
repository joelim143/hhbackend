# forms.py
from django import forms

class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15, required=False)
    skills = forms.CharField(max_length=255, required=False)
    availability = forms.CharField(max_length=255, required=False)
