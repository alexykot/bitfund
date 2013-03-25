import re
from decimal import Decimal, getcontext
import urlparse

from django.utils.encoding import smart_unicode
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware, now
from django.utils.translation import ugettext_lazy as _
from django import forms

from bitfund.core.models import *
from bitfund.core.settings.project import CALCULATIONS_PRECISION, YOUTUBE_VIDEO_ID_LENGTH, MIN_GOAL_TIMELENGTH_DAYS
from bitfund.project.models import *
from bitfund.project.lists import DONATION_TYPES_CHOICES


class CreateProjectForm(forms.Form):
    title = forms.CharField(max_length=255, required=True)

    def clean_title(self):
        title     = self.cleaned_data['title']

        same_title_projects_count = Project.objects.filter(title__exact=title).count()

        if same_title_projects_count > 0 :
            raise ValidationError(_(u'Project with this title already exists, please claim it instead.'), code='invalid')

        return title

class EditProjectForm(forms.ModelForm):
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
        widgets = {'is_public'    : forms.RadioSelect(choices=YES_NO_CHOICES),
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
    

class ProjectNeedForm(forms.ModelForm):
    title = forms.CharField(max_length=255, required=False)
    amount = forms.DecimalField(max_value=9999999999, decimal_places=2, max_digits=12, label=_('amount'), required=False)
    sort_order = forms.IntegerField(widget=forms.HiddenInput, required=False)
    drop_need = forms.BooleanField(widget=forms.HiddenInput, required=False)

    class Meta:
        model   = ProjectNeed
        widgets = {'is_public': forms.HiddenInput(),
                   'brief': forms.Textarea(),
        }
        exclude = ('project', 'date_added', 'key',)


    def clean(self):
        cleaned_data = super(ProjectNeedForm, self).clean()

        title = cleaned_data.get('title')
        amount = cleaned_data.get('amount')
        drop_need = cleaned_data.get('drop_need')
        is_public = cleaned_data.get('is_public')

        if not drop_need and is_public and (amount == 0 or amount is None):
            self._errors["amount"] = self.error_class([_(u'Amount is required for active needs.')])
            del cleaned_data["amount"]
        elif not is_public and amount is None :
            cleaned_data["amount"] = 0

        if not drop_need and is_public and title == '':
            self._errors["title"] = self.error_class([_(u'Title is required for active needs.')])
            del cleaned_data["title"]

        return cleaned_data


class CreateProjectGoalForm(forms.Form):
    title = forms.CharField(max_length=255)

class EditProjectGoalForm(forms.ModelForm):
    amount = forms.DecimalField(max_value=9999999999, min_value=0, decimal_places=2, max_digits=12)
    date_starting = forms.DateField(input_formats=('%m/%d/%Y',), required=False, widget=forms.DateInput(format='%m/%d/%Y'))
    date_ending = forms.DateField(input_formats=('%m/%d/%Y',), required=False, widget=forms.DateInput(format='%m/%d/%Y'))

    class Meta:
        model = ProjectGoal
        fields = {'key', 'title', 'brief', 'text',
                  'image', 'youtube_video_id', 'vimeo_video_id',
                  'amount',
                  'date_starting', 'date_ending',
                  }
        widgets = { 'brief': forms.Textarea(),
                   }

    def clean_key(self):
        key     = self.cleaned_data['key'].lower()

        regex   = re.compile('^[a-z0-9-._]{1,}$')
        if not regex.search(smart_unicode(key)):
            raise ValidationError(_(u'Allowed chars - latin, numeric, dash, dot, underscore.'), code='invalid')

        regex   = re.compile('^[a-z]{1}')
        if not regex.search(smart_unicode(key)):
            raise ValidationError(_(u'Must start with a latin.'), code='invalid')

        same_key_projects_count = (ProjectGoal.objects
                                   .filter(project_id=self.instance.project_id)
                                   .filter(key__exact=key)
                                   .exclude(id=self.instance.id)
                                   .count())
        if same_key_projects_count > 0 :
            raise ValidationError(_(u'Key already used in another goal for this project.'), code='invalid')

        return key


    # parses provided youtube link and cuts video_id out of it. parses these link patterns:
    # http://[www.]youtube.com/[<anything>]?[<anything>&]v=iYWzMvlj2RQ[&<anything>]
    # http://[www.]youtube.com/[<anything>]v/iYWzMvlj2RQ[?<anything>]
    # http://[www.]youtube.com/[<anything>]embed/iYWzMvlj2RQ[?<anything>]
    # http://youtu.be/iYWzMvlj2RQ[/<anything>][?<anything>]
    def clean_youtube_video_id(self):
        #yes, this is a full URL and not the id yet, no naming error here.
        youtube_video_url = self.cleaned_data['youtube_video_id']
        youtube_video_id = None

        if youtube_video_url is None or youtube_video_url == '' :
            if self.instance.youtube_video_id is not None :
                return self.instance.youtube_video_id
            else :
                return youtube_video_id

        parsed_url = urlparse.urlparse(youtube_video_url)
        if parsed_url.netloc == 'youtu.be' :
            youtube_video_id = parsed_url.path.strip('/').split('/')[0]
        elif parsed_url.netloc.strip('w.') == 'youtube.com' :
            query_list = parsed_url.query.split('&')
            for query_part in query_list :
                query_part_parsed = query_part.split('=')

                if query_part_parsed[0] == 'v' :
                    youtube_video_id = query_part_parsed[1]
                    break

            # parameter 'v' not found in the URL query - let's look in the path
            if youtube_video_id is None :
                import itertools
                path_list = parsed_url.path.strip('/').split('/')
                for index, path_part in enumerate(path_list) :
                    if path_part == 'v' or path_part == 'embed' :
                        youtube_video_id = path_list[index+1]
                        break
                    elif len(path_part) == YOUTUBE_VIDEO_ID_LENGTH :
                        youtube_video_id = path_part
                        break

        if youtube_video_id is None :
            raise ValidationError(_(u'Youtube video URL invalid.'), code='invalid')

        return youtube_video_id


    # parses provided youtube link and cuts video_id out of it. parses these link patterns:
    #  http://player.vimeo.com/video/47437305[?<anything>]
    #  http://[www.]vimeo.com/47437305[?<anything>][#<anything>]
    def clean_vimeo_video_id(self):
        #yes, this is a full URL and not the id yet, no naming error here.
        vimeo_video_url = self.cleaned_data['vimeo_video_id']
        vimeo_video_id = None

        if vimeo_video_url is None or vimeo_video_url == '' :
            return vimeo_video_id

        parsed_url = urlparse.urlparse(vimeo_video_url)
        if parsed_url.netloc == 'player.vimeo.com' :
            vimeo_video_id = parsed_url.path.strip('/').split('/')[1]
        elif parsed_url.netloc.strip('w.') == 'vimeo.com' :
            vimeo_video_id = parsed_url.path.strip('/')

        if vimeo_video_id is None :
            raise ValidationError(_(u'Youtube video URL invalid.'), code='invalid')

        return vimeo_video_id

    def clean(self):
        cleaned_data = super(EditProjectGoalForm, self).clean()
        date_starting = cleaned_data.get("date_starting")
        date_ending = cleaned_data.get("date_ending")

        if date_starting is None and self.instance.date_starting is not None:
            date_starting = self.instance.date_starting
        if date_ending is None and self.instance.date_ending is not None:
            date_ending = self.instance.date_ending

        if date_ending is not None and date_starting is not None :
            goal_length_timedelta = date_ending-date_starting
            if goal_length_timedelta.days < MIN_GOAL_TIMELENGTH_DAYS :
                raise ValidationError(_(u'Goal must last at least '+str(MIN_GOAL_TIMELENGTH_DAYS)+u' days.'), code='invalid')

        return cleaned_data


class AddLinkedProjectForm(forms.Form):
    linked_project = forms.ModelChoiceField(queryset=Project.objects.all(), required=True, empty_label=u'Select Project')
    redonation_percent = forms.DecimalField(min_value=0.01, decimal_places=2, required=False)
    redonation_amount = forms.DecimalField(min_value=0.01, decimal_places=2, required=False)
    sort_order = forms.IntegerField(required=False, widget=forms.HiddenInput)
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

class PledgeProjectGoalForm(forms.Form):
    pledge_amount = forms.DecimalField(min_value=0.01, decimal_places=4, required=True)

class PledgeNoBudgetProjectForm(forms.Form):
    pledge_type = forms.ChoiceField(required=True, widget=forms.HiddenInput, choices=DONATION_TYPES_CHOICES)
    pledge_amount = forms.DecimalField(decimal_places=8, required=True)
