# custom bitfund settings
from decimal import getcontext

PROJECT_VERSION = '0.1'

SESSION_PARAM_PROTOTYPE_HIDDEN_ENTRANCE = 'hidden-entrance'
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

TIME_TO_SHOW_HOURS = 48 #when it's time to show hours instead of days for "time to go" for budget and goals, in hours

API_USER_TOKEN_PARAM_NAME = 'userToken'
API_TARGET_MONTH_PARAM_NAME = 'targetMonth'

SITE_CURRENCY_CODE = 'USD'
SITE_CURRENCY_SIGN = '$'

CALCULATIONS_PRECISION = 28 #for decimal calculations, used as `getcontext().prec` value
getcontext().prec = CALCULATIONS_PRECISION

BITFUND_OWN_PROJECT_ID = 5

PROJECTS_IN_HOMEPAGE_COLUMN = 10

RGBCOLOR_DONUT_CHART_PLEDGES = '586F05'
RGBCOLOR_DONUT_CHART_REDONATIONS = '8DB308'
RGBCOLOR_DONUT_CHART_OTHER_SOURCES = 'EFBC09'
RGBCOLOR_DONUT_CHART_BACKGROUND = 'EDEBEA'


ARGB_DONUT_CHART_PLEDGES = (0.345, 0.435, 0.0196, 1, 'solid') # '#586F05'
ARGB_DONUT_CHART_REDONATIONS = (0.553, 0.702, 0.0314, 1, 'linear') # '#8DB308'
ARGB_DONUT_CHART_OTHER_SOURCES = (0.937, 0.737, 0.035, 1, 'radial') # '#EFBC09'
ARGB_DONUT_CHART_BACKGROUND = (0.929, 0.922, 0.922, 1, 'linear') # '#EDEBEA'


#empty chart looks better if a tiny colored bit is shown
MINIMAL_DEFAULT_PLEDGES_RADIANT = 2
MINIMAL_DEFAULT_REDONATIONS_RADIANT = 2
MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT = 1

SESSION_PARAM_RETURN_TO_PROJECT = 'return-to-project'

MINIMAL_SUPPORTED_PROJECTS_COUNT_FOR_PUBLIC = 10