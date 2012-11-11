from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bitfund.views.home', name='home'),
    # url(r'^bitfund/', include('bitfund.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/{0,}', include(admin.site.urls)),
    
)

urlpatterns += patterns('bitfund.views',
    (r'^/{0,}$', 'index'),
    (r'^projects{0,}/{0,}$', redirect_to, {'url': '/'}),
    (r'^pledger{0,}/{0,}$', redirect_to, {'url': '/'}),
    (r'^login/{0,}$', 'login'),
    (r'^logout/{0,}$', 'logout'),
    (r'^register/{0,}$', 'register'),
    
)

urlpatterns += patterns('project.views',
    (r'^project/create$', 'create'),

    (r'^project/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'view'),
    (r'^(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'view'),
    (r'^project/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit/{0,}$', 'edit'),

    (r'^project/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_needs/{0,}$', 'edit_needs'),
    (r'^project/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_needs/(?P<need_id>[0-9]{1,})/{0,}$', 'edit_needs'),
    (r'^project/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/delete_need/(?P<need_id>[0-9]{1,})/{0,}$', 'delete_need'),

    (r'^project/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_goals/{0,}$', 'edit_goals'),
    (r'^project/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_goals/(?P<goal_id>[0-9]{1,})/{0,}$', 'edit_goals'),
    (r'^project/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/delete_goal/(?P<goal_id>[0-9]{1,})/{0,}$', 'delete_goal'),
   
    (r'^project/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/support/{0,}$', 'support'),
    (r'^project/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/support/(?P<support_type>(onetime|monthly))/{0,}$', 'support'),
    (r'^project/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/drop_support/{0,}$', 'drop_support'),

)

urlpatterns += patterns('pledger.views',
    (r'^pledger/donations_overview/{0,}$', 'donations_overview'),
    (r'^pledger/donations_update/{0,}$', 'donations_update'),
    (r'^pledger/checkout/{0,}$', 'checkout'),
    (r'^pledger/checkout_success/{0,}$', 'checkout_success'),
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
    
    
"""
urlpatterns = patterns('',
    url(r'^/coorder-details/(?P<pk>\d+)/$',
        DetailView.as_view(
            model=Coorder,
            template_name='core/coorder_details.html')),                                   
  )

    url(r'^coorder-list/$',
        ListView.as_view(
            model=Coorder,                
            queryset=Coorder.objects.order_by('-pub_date')[:5],
            context_object_name='latest_coorders_list',
            template_name='core/view_coorders.html'),
        name = 'coorders_list'),
"""

"""
info_dict = {
             'queryset' : Coorder.objects.all(),
             }


    (r'^$', 'django.views.generic.list_detail.object_list', info_dict),
    url(r'^/details/(?P<object_id>\d+)$', 'django.views.generic.list_detail.object_detail', dict(info_dict, template_name='core/coorder_details.html'), 'poll_results'),
    (r'^/edit/(?P<coorder_id>\d+)$', 'core.views.edit'),

urlpatterns += patterns('polls.views',
    (r'^$', 'index'),
    (r'^(?P<poll_id>\d+)/$', 'detail'),
    (r'^(?P<poll_id>\d+)/results/$', 'results'),
    (r'^(?P<poll_id>\d+)/vote/$', 'vote'),    
)
"""