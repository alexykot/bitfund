from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import redirect_to
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from bitfund.project.api import *

# Uncomment the next two lines to enable the admin:
admin.autodiscover()


#DJANGO USUAL
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bitfund.core.views.home', name='home'),
    # url(r'^bitfund/', include('bitfund.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/{0,}', include(admin.site.urls)),
)

#API URLS
urlpatterns += patterns('',
    (r'^api/', include(ProjectResource().urls)),
    (r'^api/', include(ProjectNeedResource().urls)),
    (r'^api/', include(ProjectGoalResource().urls)),
    (r'^api/', include(ProjectDependenciesResource().urls)),
    (r'^selectable/', include('selectable.urls')),
)

#MISC PAGES
urlpatterns += patterns('bitfund.core.views',
    (r'^index.htm', 'landing'),
    (r'^/{0,}$', 'index'),
    (r'^projects{0,}/{0,}$', redirect_to, {'url': '/'}),
    (r'^pledger{0,}/{0,}$', redirect_to, {'url': '/'}),
    (r'^login/{0,}$', 'login'),
    (r'^logout/{0,}$', 'logout'),
    (r'^register/{0,}$', 'register'),
)

#PROJECTS
urlpatterns += patterns('bitfund.project.views',
    (r'^projects/create$', 'create'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'budget'),
    (r'^(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'budget'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit/{0,}$', 'edit'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_needs/{0,}$', 'edit_needs'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_needs/(?P<need_id>[0-9]{1,})/{0,}$', 'edit_needs'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/delete_need/(?P<need_id>[0-9]{1,})/{0,}$', 'delete_need'),
    
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/chart/{0,}$', 'chart_image'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/(?P<need_key>[a-z]{1}[a-z0-9-_.]{1,})/chart/{0,}$', 'chart_image'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/(?P<goal_key>[a-z]{1}[a-z0-9-_.]{1,})/chart/{0,}$', 'chart_image'),
    
    
    

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_goals/{0,}$', 'edit_goals'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_goals/(?P<goal_id>[0-9]{1,})/{0,}$', 'edit_goals'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/delete_goal/(?P<goal_id>[0-9]{1,})/{0,}$', 'delete_goal'),
   
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/support/{0,}$', 'support'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/support/(?P<support_type>(onetime|monthly))/{0,}$', 'support'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/drop_support/{0,}$', 'drop_support'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/goals/{0,}$', 'goals'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/goals/(?P<goal_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'goal_view'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/linked_projects/{0,}$', 'linked_projects'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_linked_project/{0,}$', 'crud_linked_project'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_linked_project/(?P<action>add)/{0,}$', 'crud_linked_project'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_linked_project/(?P<action>edit|drop|toggle_public)/(?P<linked_project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'crud_linked_project'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_bitfund_link/(?P<action>donate|refuse)/{0,}$', 'crud_bitfund_link'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_pledge_need/(?P<need_id>[0-9]{1,})/{0,}$', 'crud_pledge_need'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_pledge_need/(?P<need_id>[0-9]{1,})/(?P<action>pledge|drop_subscription|switch_monthly)/{0,}$', 'crud_pledge_need'),

)

#USER ACCOUNT
urlpatterns += patterns('bitfund.pledger.views',
    (r'^pledger/account/attach_card/{0,}$', 'attach_card'),
    (r'^pledger/account/attach_card/return-to/(?P<return_project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'attach_card'),

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
