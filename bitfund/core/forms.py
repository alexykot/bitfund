import re

from django.utils.encoding import smart_unicode
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms

from bitfund.project.models import *


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, label=_('username or email'))
    password = forms.CharField(max_length=255, widget = forms.PasswordInput)



class RegistrationForm(forms.Form):
    username              = forms.CharField(max_length=255)
    password              = forms.CharField(max_length=255, widget = forms.PasswordInput)
    password_confirmation = forms.CharField(max_length=255, widget = forms.PasswordInput)
    email                 = forms.EmailField()
    first_name            = forms.CharField(max_length=255)
    last_name             = forms.CharField(max_length=255)

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        password              = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")
        if password and password_confirmation and password != password_confirmation :
            msg = _("Password confirmation must match password.")
            self._errors["password_confirmation"] = self.error_class([msg])
            
            del cleaned_data["password"]
            del cleaned_data["password_confirmation"]
                        
        username              = cleaned_data.get("username")
        email                 = cleaned_data.get("email")
        if username == email :
            msg = _("Username must be not equal to email.")
            self._errors["username"] = self.error_class([msg])
            
            del cleaned_data["username"] 
        elif username and User.objects.filter(username__exact = username).count():
            msg = _("Username already exists.")
            self._errors["username"] = self.error_class([msg])
            
            del cleaned_data["username"] 
        
        if email and User.objects.filter(email__exact = email).count() :
            if not User.objects.get(email__exact=email).groups.filter(name__exact='strangers').count() : 
                msg = _("Email already exists.")
                self._errors["email"] = self.error_class([msg])
                
                del cleaned_data["email"]
        
        return cleaned_data


class ContactForm(forms.Form):
    email = forms.EmailField()
    name = forms.CharField(max_length=255, required=False)
    message = forms.CharField(widget = forms.Textarea, required=False)