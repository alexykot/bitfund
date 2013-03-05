from django.http import HttpResponse

class HttpResponseNotImplemented(HttpResponse):
    status_code = 501
