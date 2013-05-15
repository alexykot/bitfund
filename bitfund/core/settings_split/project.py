# custom bitfund project settings
from decimal import getcontext

#misc bitfund related
PROJECT_VERSION = '0.9'

SESSION_PARAM_PROTOTYPE_HIDDEN_ENTRANCE = 'hidden-entrance'
PROTOTYPE_LANDING_PAGE_URL = '/index.htm'

DEFAULT_PASSWORD = 'asdasdasd' #default password set to semianonimous users
ABANDONED_ACCOUNT_REGISTRATION_PARAMETER_NAME = 'renew-registration'

SESSION_PARAM_RETURN_TO_PROJECT = 'return-to-project'

BITFUND_OWN_PROJECT_ID = 5  #BitFund own project DB ID

TRANSACTION_OVERHEAD_FEE_PERCENT = 3.9 # % to be added to each transaction for payment processor coverage, added separately from the amount
TRANSACTION_OVERHEAD_FEE_FIXED_AMOUNT = 0.3 # amount to be added to each transaction for payment processor coverage, added separately from the percent

WITHDRAWAL_OVERHEAD_FEE_PERCENT = 0 # % to be added to each transaction for payment processor coverage, added separately from the amount
WITHDRAWAL_OVERHEAD_FEE_FIXED_AMOUNT = 0.25 # amount to be added to each transaction for payment processor coverage, added separately from the percent

#homepage
MAX_NEEDS_PER_PROJECT = 10
MAX_PUBLIC_GOALS_PER_PROJECT = 3

PROJECTS_IN_HOMEPAGE_COLUMN = 10
PROJECTS_IN_DATES_BACK_TO_LOOK = 30

#projects
PROJECTS_MEDIA_DIR = 'projects/'

#needs and goals
TIME_TO_SHOW_HOURS = 48 #when it's time to show hours instead of days for "time to go" for budget and goals, in hours

DEFAULT_MONTHLY_DONATION_AMOUNT = 1 # default donation in $
DEFAULT_ONETIME_DONATION_AMOUNT = 5 # default donation in $
GOAL_DEFAULT_TITLE = u'Untitled goal'

YOUTUBE_VIDEO_ID_LENGTH = 11 #length of videoID param in chars

MIN_GOAL_TIMELENGTH_DAYS = 3 #minimal goal running time

#web API
API_USER_TOKEN_PARAM_NAME = 'userToken'
API_TARGET_MONTH_PARAM_NAME = 'targetMonth'
API_KEY_LENGTH = 32

#Currecies
SITE_CURRENCY_CODE = 'USD'
SITE_CURRENCY_SIGN = '$'

CALCULATIONS_PRECISION = 28 #for decimal calculations, used as `getcontext().prec` value
getcontext().prec = CALCULATIONS_PRECISION


#donut charts images
CHART_RADIUS_LIST = (6, 6, 4, 2) #relative sizes
CHART_IMAGE_TYPE = 'png' #only png supported at the moment
CHART_INNER_RADIUS = 1.6 #units unknown, meaning uncertain, it just works

CHART_PARAMS = {'project': {'default': {'w': 85, 'h': 85,},
                            'large': {'w': 85, 'h': 85,},
                            'medium': {'w': 85, 'h': 85,},
                            'small': {'w': 53, 'h': 53,},
                            },
                'need': {'default': {'w': 85, 'h': 85,},
                         'large': {'w': 85, 'h': 85,},
                         'medium': {'w': 85, 'h': 85,},
                         'small': {'w': 85, 'h': 85,},
                        },
                'goal': {'default': {'w': 85, 'h': 85,},
                         'large': {'w': 85, 'h': 85,},
                         'medium': {'w': 85, 'h': 85,},
                         'small': {'w': 53, 'h': 53,},
                        },
}

ARGB_DONUT_CHART_PLEDGES = (0.345, 0.435, 0.0196, 1, 'solid') # '#586F05'
ARGB_DONUT_CHART_REDONATIONS = (0.553, 0.702, 0.0314, 1, 'solid') # '#8DB308'
ARGB_DONUT_CHART_OTHER_SOURCES = (0.937, 0.737, 0.035, 1, 'solid') # '#EFBC09'
ARGB_DONUT_CHART_BACKGROUND = (0.929, 0.922, 0.922, 1, 'solid') # '#EDEBEA'

CHART_PLEDGES_RGB = '586F05'
CHART_REDONATIONS_RGB = '8DB308'
CHART_OTHER_SOURCES_RGB = 'EFBC09'
CHART_BACKGROUND_RGB = 'EDEBEA' #this means thinnest background ring in the chart, not the image background

CHART_PLEDGES_ALPHA = 1.0 #0 to 1 float, alpha channel
CHART_PLEDGES_STYLE = 'solid' #just use this,

TOTAL_DEGREES = 360 #captain obvious

MINIMAL_DEFAULT_PLEDGES_DEGREES = 5  #empty chart looks better if a tiny colored bit is shown
MINIMAL_DEFAULT_REDONATIONS_DEGREES = 3
MINIMAL_DEFAULT_OTHER_SOURCES_DEGREES = 2

#user accounts
MINIMAL_SUPPORTED_PROJECTS_COUNT_FOR_PUBLIC = 10


CACHE_TIMEOUT = 60 #index page cache timeout in seconds