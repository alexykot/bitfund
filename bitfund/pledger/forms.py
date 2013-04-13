from django import forms
from model_utils.choices import Choices
from bitfund.pledger.models import BANK_ACCOUNT_ENTITY_TYPE_CHOICES


class BankAccountBusinessUnderwritingForm(forms.Form):
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

class BankAccountPersonUnderwritingForm(forms.Form):
    ba_entity_type = forms.ChoiceField(choices=BANK_ACCOUNT_ENTITY_TYPE_CHOICES,
                                       required=True, widget=forms.RadioSelect)

    ba_person_name = forms.CharField(max_length=255, required=True)
    ba_person_phone = forms.CharField(max_length=255, required=True)
    ba_person_address = forms.CharField(max_length=255, required=True)
    ba_person_city = forms.CharField(max_length=255, required=False)
    ba_person_region = forms.CharField(max_length=255, required=False)
    ba_person_zip = forms.CharField(max_length=255, required=True)
    ba_person_country = forms.CharField(max_length=255, required=False)
    ba_person_dob = forms.DateField(input_formats=('%m/%d/%Y',), required=False, widget=forms.DateInput(format='%m/%d/%Y'))
