import datetime
from django.db.models.aggregates import Count
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.db import connection
from django.template import Template, Context
from django.conf import settings
from django.utils.timezone import now

from bitfund.core.settings.project import PROTOTYPE_LANDING_PAGE_URL, SESSION_PARAM_PROTOTYPE_HIDDEN_ENTRANCE, API_USER_TOKEN_PARAM_NAME
from bitfund.pledger.models import DonationTransaction, DONATION_TRANSACTION_TYPES_CHOICES, DONATION_TRANSACTION_STATUSES_CHOICES, DonationSubscription
from bitfund.project.lists import PROJECT_STATUS_CHOICES, DONATION_TYPES_CHOICES
from bitfund.project.models import Project


class HiddenEntranceMiddleware(object):
    def process_request(self, request):
        if request.path == PROTOTYPE_LANDING_PAGE_URL: 
            return None;
        elif SESSION_PARAM_PROTOTYPE_HIDDEN_ENTRANCE in request.GET:
            request.session[SESSION_PARAM_PROTOTYPE_HIDDEN_ENTRANCE] = True
            return HttpResponseRedirect('/')
        elif SESSION_PARAM_PROTOTYPE_HIDDEN_ENTRANCE in request.session:
            return None;
        else : 
            return HttpResponseRedirect(PROTOTYPE_LANDING_PAGE_URL)

class UserProjectsCountMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():


            project_recent_transactions = (DonationTransaction.objects
                                           .filter(pledger_user__id=request.user.id)
                                           .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.pledge)
                                           .filter(pledger_donation_type=DONATION_TYPES_CHOICES.onetime)
                                           .filter(transaction_datetime__gte=(now() - datetime.timedelta(days=30)))
                                           .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                                           .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                           .values('accepting_project__id')
                                           .distinct())



            pledge_subscriotions = (DonationSubscription.objects
                                                    .filter(user__id=request.user.id)
                                                    .filter(active=True)
                                                    .exclude(project__in=project_recent_transactions)
                                                    .values('project__id')
                                                    .distinct()
                                                   )

            request.user_projects_support_count = project_recent_transactions.count() + pledge_subscriotions.count()

            request.user_projects_own_count = (Project.objects
                                               .filter(maintainer__id=request.user.id)
                                               .exclude(status=PROJECT_STATUS_CHOICES.unclaimed)
                                               .aggregate(Count('key'))['key__count']
                                              ) or 0

        return None;


class SaveUserTokenMiddleware(object):
    def process_request(self, request):
        if API_USER_TOKEN_PARAM_NAME in request.GET :
            request.session[API_USER_TOKEN_PARAM_NAME] = request.GET[API_USER_TOKEN_PARAM_NAME] 
        
        return None;


class SQLLogToConsoleMiddleware:
    def process_response(self, request, response):
        if settings.DEBUG and connection.queries:
            time = sum([float(q['time']) for q in connection.queries])
            t = Template("{{count}} quer{{count|pluralize:\"y,ies\"}} in {{time}} seconds:\n\n{% for sql in sqllog %}[{{forloop.counter}}] {{sql.time}}s: {{sql.sql|safe}}{% if not forloop.last %}\n\n{% endif %}{% endfor %}")
            print t.render(Context({'sqllog':connection.queries,'count':len(connection.queries),'time':time}))
        return response