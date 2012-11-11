from pledger.models import *
from django.db.models import Sum, Count

def frontend_header_template_data(request):
    header_data = {}
    
    if (request.user.is_authenticated()) :
        header_data = {
            'projects_donations_onetime_count'  : DonationCart.getProjectsSupportedCount(request.user, 'onetime'),
            'projects_donations_monthly_count'  : DonationCart.getProjectsSupportedCount(request.user, 'monthly'),
            'projects_donations_onetime_total'  : DonationCart.getProjectsSupportedTotal(request.user, 'onetime'),
            'projects_donations_monthly_total'  : DonationCart.getProjectsSupportedTotal(request.user, 'monthly'),
        }
    
    return header_data

def user_is_stranger(request):
    return {'user_is_stranger': bool(request.user.groups.filter(name='strangers').count()) }