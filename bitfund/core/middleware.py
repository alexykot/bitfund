from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from bitfund.core.settings.project import PROTOTYPE_LANDING_PAGE_URL, PROTOTYPE_HIDDEN_ENTRANCE, API_USER_TOKEN_PARAM_NAME

class HiddenEntranceMiddleware(object):
    def process_request(self, request):
        if request.path == PROTOTYPE_LANDING_PAGE_URL: 
            return None;
        elif PROTOTYPE_HIDDEN_ENTRANCE in request.GET: 
            request.session[PROTOTYPE_HIDDEN_ENTRANCE] = True
            return HttpResponseRedirect('/')
        elif PROTOTYPE_HIDDEN_ENTRANCE in request.session:
            return None;
        else : 
            return HttpResponseRedirect(PROTOTYPE_LANDING_PAGE_URL)
        
        
class SaveUserTokenMiddleware(object):
    def process_request(self, request):
        if API_USER_TOKEN_PARAM_NAME in request.GET :
            request.session[API_USER_TOKEN_PARAM_NAME] = request.GET[API_USER_TOKEN_PARAM_NAME] 
        
        return None;
