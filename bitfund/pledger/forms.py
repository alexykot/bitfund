from django import forms
from model_utils.choices import Choices
from bitfund.pledger.models import BANK_ACCOUNT_ENTITY_TYPE_CHOICES


class BankAccountUnderwritingForm(forms.Form):
    ba_uri = forms.CharField(widget=forms.HiddenInput, required=True)
    ba_entity_type = forms.ChoiceField(choices=BANK_ACCOUNT_ENTITY_TYPE_CHOICES,
                                       required=True, widget=forms.RadioSelect)

    ba_business_name = forms.CharField(max_length=255, required=True)
    ba_business_phone = forms.CharField(max_length=255, required=True)
    ba_business_email = forms.CharField(max_length=255, required=True)
    ba_business_tax = forms.CharField(max_length=255, required=False)
    ba_business_address = forms.CharField(max_length=255, required=True)
    ba_business_city = forms.CharField(max_length=255, required=False)
    ba_business_region = forms.CharField(max_length=255, required=False)
    ba_business_zip = forms.CharField(max_length=15, required=True)
    ba_business_country = forms.CharField(max_length=255, required=False)

    ba_person_name = forms.CharField(max_length=255, required=True)
    ba_person_phone = forms.CharField(max_length=255, required=True)
    ba_person_address = forms.CharField(max_length=255, required=True)
    ba_person_city = forms.CharField(max_length=255, required=False)
    ba_person_region = forms.CharField(max_length=255, required=False)
    ba_person_zip = forms.CharField(max_length=255, required=True)
    ba_person_country = forms.CharField(max_length=255, required=False)
