from django.db.models import Sum, Count

from bitfund.pledger.models import *

def frontend_header_template_data(request):
    if 'user' not in request :
        return {}

    header_data = {}
    if 'user' in request and request.user.is_authenticated() :
        header_data = {
            'projects_donations_onetime_count'  : DonationCart.getProjectsSupportedCount(request.user, 'onetime'),
            'projects_donations_monthly_count'  : DonationCart.getProjectsSupportedCount(request.user, 'monthly'),
            'projects_donations_onetime_total'  : DonationCart.getProjectsSupportedTotal(request.user, 'onetime'),
            'projects_donations_monthly_total'  : DonationCart.getProjectsSupportedTotal(request.user, 'monthly'),
        }
    
    return header_data

def user_is_stranger(request):
    if 'user' not in request :
        return {}

    return {'user_is_stranger': bool(request.user.groups.filter(name='strangers').count()) }