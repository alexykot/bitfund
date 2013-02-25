import re
from decimal import Decimal, getcontext

from django.utils.encoding import smart_unicode
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms

from bitfund.core.models import *
from bitfund.core.settings.project import CALCULATIONS_PRECISION
from bitfund.project.models import *
from bitfund.project.lists import DONATION_TYPES_CHOICES

class CreateProjectForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        super(forms.ModelForm, self).__init__(*args, **kw)
        self.fields.keyOrder = [
            'title',
            'key',
            'is_public',
            'logo',
            'brief',
            ]
    
    def clean_key(self):
        key     = self.cleaned_data['key'].lower()
        
        regex   = re.compile('^[a-z0-9-._]{1,}$')
        if not regex.search(smart_unicode(key)):
            raise ValidationError(_(u'Allowed chars - latin, numeric, dash, dot, underscore.'), code='invalid')

        regex   = re.compile('^[a-z]{1}')
        if not regex.search(smart_unicode(key)):
            raise ValidationError(_(u'Must start with a latin.'), code='invalid')

        return key
    
    class Meta:
        model   = Project
        fields  = {'key', 'title', 'brief', 'logo', 'is_public'}
        widgets = {
                   'is_public'    : forms.RadioSelect(choices=YES_NO_CHOICES),
                   }

#a form for new backers, email only. 
class NewBackerForm(forms.Form):
    user_email  = forms.EmailField(label=_('Please tell us your email so we could remind you about pledges you\'ll enter today'), required = True)

#a one-field form for need or goal amount
class SupportProjectForm(forms.Form):
    amount      = forms.DecimalField(max_value=9999999999, min_value=0, decimal_places=2, max_digits=12, required=False)
    need        = forms.IntegerField(widget=forms.HiddenInput, required=False)
    goal        = forms.IntegerField(widget=forms.HiddenInput, required=False)
    is_monthly  = forms.BooleanField(required=False)

class ProjectNeedsGoalsListForm(forms.Form):
    needsgoals = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    def __init__(self, project_needsgoals_choices=[], *args, **kw):
        super(forms.Form, self).__init__(*args, **kw)
        
        self.fields['needsgoals'].choices = project_needsgoals_choices
    

class CreateProjectNeedForm(forms.ModelForm):
    amount = forms.DecimalField(max_value=9999999999, min_value=0.01, decimal_places=2, max_digits=12, required=True, label=_('amount'))

    def __init__(self, *args, **kw):
        super(forms.ModelForm, self).__init__(*args, **kw)

        self.fields.keyOrder = [
            'title',
            'amount',
            'key',
            'brief',
            ]

    class Meta:
        model   = ProjectNeed
        fields  = {'key', 'title', 'amount', 'brief', }

    
class CreateProjectGoalForm(forms.ModelForm):
    amount = forms.DecimalField(max_value=9999999999, min_value=0.01, decimal_places=2, max_digits=12, required=True)

    def __init__(self, *args, **kw):
        super(forms.ModelForm, self).__init__(*args, **kw)
        self.fields.keyOrder = [
            'title',
            'amount',
            'date_ending',
            'key',
            'brief',
            ]

    class Meta:
        model   = ProjectGoal
        fields  = {'key', 'title', 'date_ending', 'amount', 'brief', }

class AddLinkedProjectForm(forms.Form):
    linked_project = forms.ModelChoiceField(queryset=Project.objects.all(), required=True, empty_label=u'Select Project')
    redonation_percent = forms.DecimalField(min_value=0.01, decimal_places=2,
                                         required=False)
    redonation_amount = forms.DecimalField(min_value=0.01, decimal_places=2,
                                        required=False)
    brief = forms.CharField(max_length=255, widget=forms.Textarea)

    def __init__(self, main_project_id, *args, **kw):
        super(AddLinkedProjectForm, self).__init__(*args, **kw)

        getcontext().prec = CALCULATIONS_PRECISION

        already_linked_projects_query = (Project_Dependencies.objects
                                         .filter(depender_project=main_project_id)
                                         .values('dependee_project')
        )

        already_linked_projects_list = []

        for linked_project in already_linked_projects_query :
            already_linked_projects_list.append(linked_project['dependee_project'])


        self.fields['linked_project'].queryset = (Project.objects
                                                  .filter(is_public=True)
                                                  .exclude(id=main_project_id)
                                                  .exclude(id__in=already_linked_projects_list)
                                                  )
        free_percent, free_amount = Project(main_project_id).getMaxAvailableRedonationPercentandAmount()

        #redefined to set correct max_value
        self.fields['redonation_percent'] = forms.DecimalField(max_value=free_percent, min_value=0.01, decimal_places=4,
                                            required=False)
        self.fields['redonation_amount'] = forms.DecimalField(max_value=free_amount, min_value=0.01, decimal_places=4,
                           required=False)


    def clean(self):
        cleaned_data = super(AddLinkedProjectForm, self).clean()

        if ('redonation_percent' in cleaned_data and
                    cleaned_data['redonation_percent'] > 0 and
                    'redonation_amount' in cleaned_data and
                    cleaned_data['redonation_amount'] > 0) :
            raise ValidationError(_(u'You must choose either percent or a fixed amount, not both.'), code='invalid')

        return cleaned_data

class EditLinkedProjectForm(forms.Form):
    linked_project = forms.ModelChoiceField(queryset=Project.objects.all(), required=True, empty_label=u'Select Project',
                                            widget=forms.HiddenInput)
    redonation_percent = forms.DecimalField(required=False) # reinitialized properly in the __init__
    redonation_amount = forms.DecimalField(required=False) # reinitialized properly in the __init__
    brief = forms.CharField(max_length=255, widget=forms.Textarea)

    def __init__(self, main_project_id, linked_project_id, *args, **kw):
        super(EditLinkedProjectForm, self).__init__(*args, **kw)

        free_percent, free_amount = Project(main_project_id).getMaxAvailableRedonationPercentandAmount()

        linked_project_dependency = Project_Dependencies.objects.get(dependee_project__id=linked_project_id, depender_project__id=main_project_id)
        free_percent = free_percent + (linked_project_dependency.redonation_percent or Decimal(0))
        free_amount = free_amount + (linked_project_dependency.redonation_amount or Decimal(0))

        #redefined to set correct max_value
        self.fields['redonation_percent'] = forms.DecimalField(max_value=free_percent, min_value=0, decimal_places=4,
                                                               required=False)
        self.fields['redonation_amount'] = forms.DecimalField(max_value=free_amount, min_value=0, decimal_places=4,
                                                              required=False)

    def clean(self):
        cleaned_data = super(EditLinkedProjectForm, self).clean()

        if ('redonation_percent' not in cleaned_data or cleaned_data['redonation_percent'] == 0) :
            cleaned_data['redonation_percent'] = None

        if ('redonation_amount' not in cleaned_data or cleaned_data['redonation_amount'] == 0) :
            cleaned_data['redonation_amount'] = None

        if (cleaned_data['redonation_percent'] is not None and cleaned_data['redonation_amount'] is not None) :
            raise ValidationError(_(u'You must choose either percent or a fixed amount, not both.'), code='invalid')

        return cleaned_data

class PledgeProjectNeedForm(forms.Form):
    pledge_type = forms.ChoiceField(required=True, widget=forms.HiddenInput, choices=DONATION_TYPES_CHOICES)
    pledge_amount = forms.DecimalField(min_value=0.01, decimal_places=4, required=True)

