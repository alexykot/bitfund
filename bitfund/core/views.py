from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_user_login
from django.contrib.auth import logout as django_user_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.template import RequestContext
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.template.loader import add_to_builtins


from bitfund.core.decorators import ajax_required
from bitfund.core.models import *
from bitfund.core.forms import *
from bitfund.project.forms import *
from bitfund.core.settings_split.project import ABANDONED_ACCOUNT_REGISTRATION_PARAMETER_NAME, PROJECTS_IN_HOMEPAGE_COLUMN, SITE_CURRENCY_SIGN, SESSION_PARAM_PROTOTYPE_HIDDEN_ENTRANCE


def index(request):
    template_data = {'request': request,
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     'PROJECTS_IN_DATES_BACK_TO_LOOK':PROJECTS_IN_DATES_BACK_TO_LOOK,
                     }

    if request.method == 'POST' :
        template_data['create_project_form'] = CreateProjectForm(request.POST)
        if template_data['create_project_form'].is_valid() :
            existing_projects = Project.objects.filter(title=template_data['create_project_form'].cleaned_data['title'])

            if request.GET['action'] == 'support':
                if existing_projects.count() > 0:
                    return redirect('bitfund.project.views.budget', project_key=existing_projects[0].key)
                else :
                    project = Project()
                    project.title = template_data['create_project_form'].cleaned_data['title']
                    project.key = Project.slugifyKey(project.title)
                    project.save()
                    return redirect('bitfund.project.views.unclaimed', project_key=project.key)

            elif request.GET['action'] == 'create':
                if existing_projects.count() > 0:
                    return redirect('bitfund.project.views.budget', project_key=existing_projects[0].key)
                else :
                    project = Project()
                    project.title = template_data['create_project_form'].cleaned_data['title']
                    project.key = Project.slugifyKey(project.title)
                    project.status = PROJECT_STATUS_CHOICES.active
                    project.is_public = False
                    project.maintainer_id = request.user.id
                    project.save()
                    return redirect('bitfund.project.views.budget', project_key=project.key)

            else:
                return redirect('bitfund.core.views.index')
    else :
        template_data['create_project_form'] = CreateProjectForm()

    template_data['new_projects_list'] = (Project.objects
                                          .filter(is_public=True)
                                          .filter(status=PROJECT_STATUS_CHOICES.active)
                                          .order_by('-date_added')
                                          [:PROJECTS_IN_HOMEPAGE_COLUMN]
                                            )
    template_data['top_funded_projects_list'] = Project.getTopFundedProjects()
    template_data['top_linked_projects_list'] = Project.getTopLinkedProjects()
    template_data['unclaimed_projects_list'] = Project.getTopUnclaimedProjects()

    return render_to_response('core/index.djhtm', template_data, context_instance=RequestContext(request))

@ajax_required
def search_project(request):
    template_data = {'request': request,
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    search_string = request.GET['search_string']

    projects_list = (Project.objects
                             .exclude(status=PROJECT_STATUS_CHOICES.inactive)
                             .exclude(status=PROJECT_STATUS_CHOICES.archived)
                             .exclude(is_public=False)
                             .filter(title__icontains=search_string)
    )

    template_data['search_string'] = search_string
    template_data['results_count'] = projects_list.count()


    template_data['project_status_list'] = PROJECT_STATUS_CHOICES
    template_data['similar_projects_list_part1'] = []
    template_data['similar_projects_list_part2'] = []
    index = 0
    count = projects_list.count()
    for project in projects_list :
        project.monthly_total_donations = project.getTotalMonthlyDonations()

        project.monthly_budget = project.getTotalMonthlyBudget()

        if project.monthly_budget > 0 :
            project.monthly_total_donations_percent = Decimal( Decimal(project.monthly_total_donations)
                                                               / Decimal(project.monthly_budget) * Decimal(100))\
                                                            .quantize('0.00')
        else :
            project.monthly_total_donations_percent = -1

        if index < count :
            template_data['similar_projects_list_part1'].append(project)
        else :
            template_data['similar_projects_list_part2'].append(project)
        index = index+1

    return render_to_response('core/ajax-index_search_projects.djhtm', template_data, context_instance=RequestContext(request))


def login(request):
    if (request.user.is_authenticated() and not request.user.groups.filter(name__exact='strangers').count()) :
        return HttpResponseRedirect(reverse('bitfund.core.views.index'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        login_error = False
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                 validate_email(username_or_email)
            except Exception, e:
                username = username_or_email
            else :
                email = username_or_email
                try:
                    user = User.objects.get(email = email)
                except Exception, e:
                    username = ''
                else :
                    username = user.username

            user = authenticate(username=username, password=password)
            login_error = False
            if user is not None and not user.groups.filter(name__exact='strangers').count():
                if user.is_active:
                    django_user_login(request, user)
                    next_page = request.GET.get('next')
                    if (next_page) :
                        return HttpResponseRedirect(next_page)
                    else :
                        return HttpResponseRedirect(reverse('bitfund.core.views.index'))
                else:
                    login_error = 'your account is disabled'
            else:
                login_error = 'login / password key pair is wrong'
        else :
            login_error = 'login / password key pair is wrong'

        return render_to_response('core/login.djhtm', {'form'        : form,
                                                      'request'     : request,
                                                      'login_error' : login_error,
                                                      }, context_instance=RequestContext(request))
    else :
        form = LoginForm()

        return render_to_response('core/login.djhtm', {'form'     : form,
                                                      'request'  : request,
                                                      }, context_instance=RequestContext(request))

def logout(request):
    if (request.user.is_authenticated()) :
        django_user_logout(request)
        return HttpResponseRedirect(reverse('bitfund.core.views.index'))
    else :
        return HttpResponseRedirect(reverse('bitfund.core.views.login'))

def register(request):
    if (request.user.is_authenticated() and not request.user.groups.filter(name__exact='strangers').count()) :
        return HttpResponseRedirect(reverse('bitfund.core.views.index'))

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username         = form.cleaned_data['username']
            email            = form.cleaned_data['email']
            plain_password   = form.cleaned_data['password']
            encrypt_password = make_password(plain_password)


            if request.user.is_authenticated() and request.user.groups.filter(name__exact='strangers').count() :
                user = request.user
                user.username = username
                user.email    = email
                user.password = encrypt_password

                user.groups.clear() #just to be sure we'll clear all groups
                #user.groups.remove(Group.objects.get(name__exact='strangers'))



            elif (not request.user.is_authenticated()
                  and User.objects.filter(email=email).count()
                  and User.objects.get(email=email).groups.filter(name__exact='strangers').count() ) :
                user = User.objects.get(email=email)
                if ( request.GET[ABANDONED_ACCOUNT_REGISTRATION_PARAMETER_NAME] ) :
                    del user
                    # this bit will be done later, abandoned registration will be implemented in real application, not in a prototype
                else :
                    # for now we just not allowing to continue abandoned user history and completely dropping abandoned strangers accounts 
                    user.delete()
                    user = User.objects.create_user(username, email, plain_password)

            else :
                user = User.objects.create_user(username, email, plain_password)

            user.first_name = form.cleaned_data['first_name']
            user.last_name  = form.cleaned_data['last_name']
            user.save()
            Group.objects.get(name='users').user_set.add(user)



            return HttpResponseRedirect(reverse('bitfund.core.views.index'))
        else :
            return render_to_response('core/register.djhtm', {'form'     : form,
                                                             'request'  : request,
                                                             }, context_instance=RequestContext(request))

    else :
        form = RegistrationForm()

        return render_to_response('core/register.djhtm', {'form'     : form,
                                                         'request'  : request,
                                                         }, context_instance=RequestContext(request))


def landing(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            email   = form.cleaned_data['email']
            message = form.cleaned_data['message']

            send_mail('Message at bitfund.org from '+email, message, email, ['alexykot@gmail.com'], fail_silently=False)

            return render_to_response('core/landing.djhtm', {'form'         : form,
                                                                'message_sent' : True,
                                                                'request'      : request,
                                                                }, context_instance=RequestContext(request))
        else :
            return render_to_response('core/landing.djhtm', {'form'     : form,
                                                                'request'  : request,
                                                                }, context_instance=RequestContext(request))

    else :
        form = ContactForm()

    template_data = {'form'   : form,
                     'request'   : request,
                     'SESSION_PARAM_PROTOTYPE_HIDDEN_ENTRANCE': SESSION_PARAM_PROTOTYPE_HIDDEN_ENTRANCE,
                     }

    return render_to_response('core/static/landing.djhtm', template_data, context_instance=RequestContext(request))

def about(request):
    template_data = {'request'   : request, }

    return render_to_response('core/static/about.djhtm', template_data, context_instance=RequestContext(request))

def stats(request):
    template_data = {'request'   : request, }

    return render_to_response('core/static/stats.djhtm', template_data, context_instance=RequestContext(request))

def faq(request):
    template_data = {'request'   : request, }

    return render_to_response('core/static/faq.djhtm', template_data, context_instance=RequestContext(request))

def fraud(request):
    template_data = {'request'   : request, }

    return render_to_response('core/static/fraud.djhtm', template_data, context_instance=RequestContext(request))

def terms(request):
    template_data = {'request'   : request, }

    return render_to_response('core/static/terms.djhtm', template_data, context_instance=RequestContext(request))

def charts(request):
    template_data = {'request'   : request, }

    return render_to_response('core/static/charts.djhtm', template_data, context_instance=RequestContext(request))

def privacy(request):
    template_data = {'request'   : request, }

    return render_to_response('core/static/privacy.djhtm', template_data, context_instance=RequestContext(request))
