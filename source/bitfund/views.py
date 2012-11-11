from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse 
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_user_login
from django.contrib.auth import logout as django_user_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password 
from django.contrib.auth.models import Group 
from django.template import RequestContext
from django.db.models import Q
from django.core.validators import validate_email

from bitfund.models import *
from bitfund.forms import *
from project.forms import *
from bitfund.custom_configs import ABANDONED_ACCOUNT_REGISTRATION_PARAMETER_NAME


def index(request):
    public_projects_list    = Project.objects.filter(Q(is_public = True) | Q(maintainer_id=request.user.id))
    
    return render_to_response('bitfund/index.djhtm', {'public_projects_list' : public_projects_list,
                                                  'request'               : request,
                                                  }, context_instance=RequestContext(request))


def login(request):
    if (request.user.is_authenticated() and not request.user.groups.filter(name__exact='strangers').count()) :
        return HttpResponseRedirect(reverse('bitfund.views.index'))
                                          
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
                        return HttpResponseRedirect(reverse('bitfund.views.index'))
                else:
                    login_error = 'your account is disabled'
            else:
                login_error = 'login / password key pair is wrong'
        else :
            login_error = 'login / password key pair is wrong'
                    
        return render_to_response('bitfund/login.djhtm', {'form'        : form,
                                                      'request'     : request,
                                                      'login_error' : login_error,
                                                      }, context_instance=RequestContext(request))
    else : 
        form = LoginForm()
            
        return render_to_response('bitfund/login.djhtm', {'form'     : form,
                                                      'request'  : request,
                                                      }, context_instance=RequestContext(request))

def logout(request):
    if (request.user.is_authenticated()) :
        django_user_logout(request)
        return HttpResponseRedirect(reverse('bitfund.views.index'))
    else :
        return HttpResponseRedirect(reverse('bitfund.views.login'))

def register(request):
    if (request.user.is_authenticated() and not request.user.groups.filter(name__exact='strangers').count()) :
        return HttpResponseRedirect(reverse('bitfund.views.index'))
        
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
            
            
            
            return HttpResponseRedirect(reverse('bitfund.views.index'))
        else :
            return render_to_response('bitfund/register.djhtm', {'form'     : form,
                                                             'request'  : request,
                                                             }, context_instance=RequestContext(request))
        
    else : 
        form = RegistrationForm()
            
        return render_to_response('bitfund/register.djhtm', {'form'     : form,
                                                         'request'  : request,
                                                         }, context_instance=RequestContext(request))
