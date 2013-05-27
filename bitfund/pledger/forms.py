from django import forms
from leetchi.resources import User as leetchi_user

from django_countries.countries import COUNTRIES as COUNTRIES_LIST
from bitfund.pledger.models import BANK_ACCOUNT_ENTITY_TYPE_CHOICES, MangoAccount
from bitfund.project.models import Project


class MangoAccountForm(forms.ModelForm):
    # first_name = forms.CharField(max_length=255, required=True)
    # last_name = forms.CharField(max_length=255, required=True)
    # email = forms.EmailField(required=True)
    # dob = forms.DateField(required=True)
    account_type = forms.ChoiceField(choices=leetchi_user.TYPE_CHOICES, required=True)
    nationality = forms.ChoiceField(choices=COUNTRIES_LIST, required=True)

    class Meta:
        model   = MangoAccount
        fields  = {'first_name', 'last_name', 'email', 'dob', 'account_type', 'nationality'}

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


class ProjectWithdrawFundsForm(forms.Form):
    #both fields reinitialised in __init__
    project = forms.ModelChoiceField(queryset=Project.objects.all(), widget=forms.HiddenInput, required=True)
    amount = forms.DecimalField(min_value=0.01, decimal_places=12, required=True)

    def __init__(self, project, *args, **kw):
        super(ProjectWithdrawFundsForm, self).__init__(*args, **kw)

        maintainer_queryset = Project.objects.filter(id=project.id)
        self.fields['project'] = forms.ModelChoiceField(queryset=maintainer_queryset,
                                                        widget=forms.HiddenInput, initial=project.id)



        self.fields['amount'] = forms.DecimalField(min_value=0.01, max_value=project.amount_balance,
                                                   decimal_places=12, required=True, initial=project.amount_balance)



