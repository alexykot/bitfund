from django.utils.encoding import smart_unicode
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms

from bitfund.models import *
from pledger.models import *
from project.models import *
from bitfund.custom_configs import DATE_INPUT_FORMATS


#a one-field form for need or goal amount
class SupportProjectForm(forms.Form):
    support_total     = forms.DecimalField(max_value=9999999999, min_value=0, decimal_places=2, max_digits=12, required=False)
    donation_cart_id  = forms.IntegerField(widget=forms.HiddenInput, required=False)
    
class FakeExternalCheckoutForm(forms.Form):
    username = forms.CharField(max_length=255, widget=forms.HiddenInput) 
    amount   = forms.CharField(max_length=255, widget=forms.HiddenInput)
         