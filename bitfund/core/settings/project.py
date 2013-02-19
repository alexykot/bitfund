# custom bitfund settings
from decimal import getcontext

PROJECT_VERSION = '0.1'

PROTOTYPE_HIDDEN_ENTRANCE = 'hidden-entrance'
PROTOTYPE_LANDING_PAGE_URL = '/index.htm'

DEFAULT_PASSWORD = 'asdasdasd' #default password set to semianonimous users
ABANDONED_ACCOUNT_REGISTRATION_PARAMETER_NAME = 'renew-registration'

MAX_NEEDS_PER_PROJECT = 10
MAX_GOALS_PER_PROJECT = 10

DEFAULT_MONTHLY_DONATION_AMOUNT = 1 # default donation in $
DEFAULT_ONETIME_DONATION_AMOUNT = 5 # default donation in $

DATE_INPUT_FORMATS = (
'%d %b %Y', '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b %d %Y', '%b %d, %Y', '%d %b, %Y', '%B %d %Y', '%B %d, %Y',
'%d %B %Y', '%d %B, %Y')

FAKE_CHECKOUT_SYSTEM_URL = '/pledger/fake_external_checkout'

TIME_TO_SHOW_HOURS = 48 #when it's time to show hours instead of days for "time to go" for budget and goals, in hours

API_USER_TOKEN_PARAM_NAME = 'userToken'
API_TARGET_MONTH_PARAM_NAME = 'targetMonth'

SITE_CURRENCY_CODE = 'USD'
SITE_CURRENCY_SIGN = '$'

CALCULATIONS_PRECISION = 28 #for decimal calculations, used as `getcontext().prec` value
getcontext().prec = CALCULATIONS_PRECISION

BITFUND_OWN_PROJECT_ID = 5


RGBCOLOR_DONUT_CHART_PLEDGES = '586F05'
RGBCOLOR_DONUT_CHART_REDONATIONS = '8DB308'
RGBCOLOR_DONUT_CHART_OTHER_SOURCES = 'EFBC09'
RGBCOLOR_DONUT_CHART_BACKGROUND = 'EDEBEA'

#empty chart looks better if a tiny colored bit is shown
MINIMAL_DEFAULT_PLEDGES_RADIANT = 2
MINIMAL_DEFAULT_REDONATIONS_RADIANT = 2
MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT = 1