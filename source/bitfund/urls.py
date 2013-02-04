from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import redirect_to

from bitfund.settings_project import PROJECT_VERSION
from project.api import *

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

#DJANGO USUAL
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bitfund.views.home', name='home'),
    # url(r'^bitfund/', include('bitfund.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/{0,}', include(admin.site.urls)),
    (r'^accounts/', include('userena.urls')),
)

#API URLS
urlpatterns += patterns('',
    (r'^api/', include(ProjectResource().urls)),
    (r'^api/', include(ProjectNeedResource().urls)),
    (r'^api/', include(ProjectGoalResource().urls)),
)

#MISC PAGES
urlpatterns += patterns('bitfund.views',
    (r'^index.htm', 'landing'),
    (r'^/{0,}$', 'index'),
    (r'^projects{0,}/{0,}$', redirect_to, {'url': '/'}),
    (r'^pledger{0,}/{0,}$', redirect_to, {'url': '/'}),
    (r'^login/{0,}$', 'login'),
    (r'^logout/{0,}$', 'logout'),
    (r'^register/{0,}$', 'register'),
)

#PROJECTS
urlpatterns += patterns('project.views',
    (r'^projects/create$', 'create'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'view'),
    (r'^(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'view'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit/{0,}$', 'edit'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_needs/{0,}$', 'edit_needs'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_needs/(?P<need_id>[0-9]{1,})/{0,}$', 'edit_needs'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/delete_need/(?P<need_id>[0-9]{1,})/{0,}$', 'delete_need'),
    
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/chart/{0,}$', 'chart_image'),
    

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_goals/{0,}$', 'edit_goals'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_goals/(?P<goal_id>[0-9]{1,})/{0,}$', 'edit_goals'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/delete_goal/(?P<goal_id>[0-9]{1,})/{0,}$', 'delete_goal'),
   
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/support/{0,}$', 'support'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/support/(?P<support_type>(onetime|monthly))/{0,}$', 'support'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/drop_support/{0,}$', 'drop_support'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/goals/{0,}$', 'goals'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/goals/(?P<goal_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'goal_view'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/linked_projects/{0,}$', 'linked_projects'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/linked_projects/(?P<linked_project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'linked_project_view'),
    
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/about/{0,}$', 'about'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/contribute/{0,}$', 'contribute'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/team/{0,}$', 'team'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/timeline/{0,}$', 'timeline'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/blog/{0,}$', 'blog'),

)

#USER ACCOUNT
urlpatterns += patterns('pledger.views',
    (r'^pledger/donations_overview/{0,}$', 'donations_overview'),
    (r'^pledger/donations_update/{0,}$', 'donations_update'),
    (r'^pledger/checkout/{0,}$', 'checkout'),
    (r'^pledger/checkout_success/{0,}$', 'checkout_success'),
    (r'^pledger/donations_success/{0,}$', 'donations_success'),
    (r'^pledger/fake_external_checkout/{0,}$', 'fake_external_checkout'),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    ) 
