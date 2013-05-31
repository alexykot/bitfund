from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import redirect_to

from bitfund.project.api import *

# Uncomment the next two lines to enable the admin:
admin.autodiscover()


#DJANGO USUAL
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bitfund.core.views.home', name='home'),
    # url(r'^bitfund/', include('bitfund.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/{0,}', include(admin.site.urls)),

    url(r'', include('social_auth.urls')),
)

#API URLS
urlpatterns += patterns('',
    (r'^api/', include(ProjectResource().urls)),
    (r'^api/', include(ProjectNeedResource().urls)),
    (r'^api/', include(ProjectGoalResource().urls)),
    (r'^api/', include(ProjectDependenciesResource().urls)),
)

#zinnia blog
urlpatterns += patterns('',
    url(r'^blog/{0,}', include('zinnia.urls')),
    url(r'^comments/{0,}', include('django.contrib.comments.urls')),

    # url(r'^', include('zinnia.urls.capabilities')),
    # url(r'^search/', include('zinnia.urls.search')),
    # url(r'^sitemap/', include('zinnia.urls.sitemap')),
    # url(r'^trackback/', include('zinnia.urls.trackback')),
    # url(r'^blog/tags/', include('zinnia.urls.tags')),
    # url(r'^blog/feeds/', include('zinnia.urls.feeds')),
    # url(r'^blog/random/', include('zinnia.urls.random')),
    # url(r'^blog/authors/', include('zinnia.urls.authors')),
    # url(r'^blog/categories/', include('zinnia.urls.categories')),
    # url(r'^blog/comments/', include('zinnia.urls.comments')),
    # url(r'^blog/', include('zinnia.urls.entries')),
    # url(r'^blog/', include('zinnia.urls.archives')),
    # url(r'^blog/', include('zinnia.urls.shortlink')),
    # url(r'^blog/', include('zinnia.urls.quick_entry')),

)

#MISC PAGES
urlpatterns += patterns('bitfund.core.views',
    (r'^index.htm', 'landing'),
    (r'^/{0,}$', 'index'),
    (r'^projects{0,}/{0,}$', redirect_to, {'url': '/'}),
    (r'^pledger{0,}/{0,}$', redirect_to, {'url': '/'}),
    (r'^search_project/{0,}$', 'search_project'),
    (r'^login/{0,}$', 'login'),
    (r'^logout/{0,}$', 'logout'),
    (r'^register/{0,}$', 'register'),
    (r'^contact/{0,}$', 'contact'),

    (r'^about/{0,}$', 'about'),
    (r'^stats/{0,}$', 'stats'),
    (r'^faq/{0,}$', 'faq'),
    (r'^charts/{0,}$', 'charts'),
    (r'^terms/{0,}$', 'terms'),
    (r'^privacy/{0,}$', 'privacy'),
    (r'^fraud/{0,}$', 'fraud'),


)

#USER ACCOUNT
urlpatterns += patterns('bitfund.pledger.views',
                        (r'^account/{0,}$', 'profile'),
                        (r'^user/(?P<username>[a-zA-Z0-9-_.]{1,})/{0,}$', 'profile'),
                        (r'^user/(?P<external_service>tw|gh|gg|fb)/(?P<external_username>[a-zA-Z0-9-_.]{1,})/{0,}$', 'profile'),
                        (r'^account/{0,}$', 'profile'),
                        (r'^account/projects/{0,}$', 'projects'),
                        (r'^account/projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'projects'),
                        (r'^account/projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/withdraw/{0,}$', 'withdraw'),

                        (r'^account/existing_similar_projects/{0,}$', 'existing_similar_projects'),

                        (r'^account/attach_bank_card/{0,1}$', 'attach_bank_card'),
                        (r'^account/attach_bank_card/(?P<action>detach|attach)/{0,}$', 'attach_bank_card'),
                        (r'^account/attach_bank_account/{0,}$', 'attach_bank_account'),
                        (r'^account/attach_bank_account/(?P<action>underwrite|detach|attach)/{0,}$', 'attach_bank_account'),

                        )

#PROJECTS
urlpatterns += patterns('bitfund.project.views',

    #view
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'budget'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/goal/(?P<goal_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'goal'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/goal/(?P<goal_key>[a-z]{1}[a-z0-9-_.]{1,})/(?P<action>pledge|drop){0,}$', 'goal'),

    #charts
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/chart/{0,}$', 'chart_image_project'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/need/(?P<need_id>[0-9]{1,})/chart/{0,}$', 'chart_image_need'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/goal/(?P<goal_key>[a-z]{1}[a-z0-9-_.]{1,})/chart/{0,}$', 'chart_image_goal'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/linked_projects/{0,}$', 'linked_projects'),

    #pledge
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_pledge_empty_project/{0,}$', 'crud_pledge_empty_project'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_pledge_empty_project/(?P<action>pledge|drop_subscription|switch_monthly)/{0,}$', 'crud_pledge_empty_project'),

    #claims, votes, reports
    (r'^unclaimed/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'unclaimed'),
    (r'^claim/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'claim'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/maintainer_vote/{0,}$', 'vote_maintainer'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/maintainer_vote/(?P<action>support|dethrone)/{0,}$', 'vote_maintainer'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/report/{0,}$', 'report'),



    #CrUD
    ##projects
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit/{0,}$', 'budget_edit'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/toggle/{0,}$', 'project_toggle'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/photo_uload/{0,}$', 'budget_ajax_logo_upload'),

    ##needs
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/add_need/{0,}$', 'add_need'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_pledge_need/(?P<need_id>[0-9]{1,})/{0,}$', 'crud_pledge_need'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_pledge_need/(?P<need_id>[0-9]{1,})/(?P<action>pledge|drop_subscription|switch_monthly)/{0,}$', 'crud_pledge_need'),

    ##goals
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/goal_create/{0,}$', 'goal_create'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/goal/(?P<goal_key>[a-z]{1}[a-z0-9-_.]{1,})/edit/{0,}$', 'goal_edit'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/goal/(?P<goal_key>[a-z]{1}[a-z0-9-_.]{1,})/toggle/{0,}$', 'goal_toggle'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/edit_goal/(?P<goal_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'goal_edit'),
    #(r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/delete_goal/(?P<goal_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'delete_goal'),

    ##project links
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_linked_project/{0,}$', 'crud_linked_project'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_linked_project/(?P<action>add)/{0,}$', 'crud_linked_project'),
    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_linked_project/(?P<action>edit|drop|toggle_public)/(?P<linked_project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'crud_linked_project'),

    (r'^projects/(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/crud_bitfund_link/(?P<action>donate|refuse)/{0,}$', 'crud_bitfund_link'),



    #perfect URLs
    (r'^(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'budget'),
    (r'^(?P<project_key>[a-z]{1}[a-z0-9-_.]{1,})/(?P<goal_key>[a-z]{1}[a-z0-9-_.]{1,})/{0,}$', 'goal'),
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
