from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from bitfund.settings_custom import PROTOTYPE_LANDING_PAGE_URL, PROTOTYPE_HIDDEN_ENTRANCE

class HiddenEntranceMiddleware(object):
    def process_request(self, request):
        if request.path == PROTOTYPE_LANDING_PAGE_URL: 
            return None;
        elif PROTOTYPE_HIDDEN_ENTRANCE in request.GET: 
            request.session[PROTOTYPE_HIDDEN_ENTRANCE] = True
            return None;
        elif PROTOTYPE_HIDDEN_ENTRANCE in request.session:
            return None;
        else : 
            return HttpResponseRedirect(PROTOTYPE_LANDING_PAGE_URL)
        
