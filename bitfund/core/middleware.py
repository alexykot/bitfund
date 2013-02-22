from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.db import connection
from django.template import Template, Context
from django.conf import settings

from bitfund.core.settings.project import PROTOTYPE_LANDING_PAGE_URL, SESSION_PARAM_PROTOTYPE_HIDDEN_ENTRANCE, API_USER_TOKEN_PARAM_NAME


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