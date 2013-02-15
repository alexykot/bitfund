import re

from django.utils.encoding import smart_unicode
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms

import selectable

from bitfund.core.models import *
from bitfund.project.models import *
from bitfund.project.lookups import LinkedProjectsLookup

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


# class AddLinkedProjectForm(forms.Form):
#     project_title = forms.CharField(
#         label=u'Select Project',
#         widget=selectable.AutoCompleteWidget(LinkedProjectsLookup),
#         required=True,
#         )
#     project_percent = forms.CharField(required=False)
#     project_amount = forms.CharField(required=False)



