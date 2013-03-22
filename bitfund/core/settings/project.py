# custom bitfund project settings
from decimal import getcontext

#misc project related
PROJECT_VERSION = '0.6'

SESSION_PARAM_PROTOTYPE_HIDDEN_ENTRANCE = 'hidden-entrance'
PROTOTYPE_LANDING_PAGE_URL = '/index.htm'

DEFAULT_PASSWORD = 'asdasdasd' #default password set to semianonimous users
ABANDONED_ACCOUNT_REGISTRATION_PARAMETER_NAME = 'renew-registration'

SESSION_PARAM_RETURN_TO_PROJECT = 'return-to-project'

BITFUND_OWN_PROJECT_ID = 5  #BitFund own project DB ID

#homepage
MAX_NEEDS_PER_PROJECT = 10
MAX_GOALS_PER_PROJECT = 10

PROJECTS_IN_HOMEPAGE_COLUMN = 10

#needs and goals
TIME_TO_SHOW_HOURS = 48 #when it's time to show hours instead of days for "time to go" for budget and goals, in hours

DEFAULT_MONTHLY_DONATION_AMOUNT = 1 # default donation in $
DEFAULT_ONETIME_DONATION_AMOUNT = 5 # default donation in $
GOAL_DEFAULT_TITLE = u'Untitled goal'

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
CHART_RADIUS_LIST = (6, 6, 4, 2)
CHART_IMAGE_TYPE = 'png' #gif, png, jpg

CHART_PARAMS = {'project': {'large': {'w': 85, #px
                                      'h': 85, #px
                                      'ir': 1.6, #units unknown, meaning uncertain, it just works
                                        },
                            'medium': {'w': 85, #px
                                       'h': 85, #px
                                       'ir': 1.6, #units unknown, meaning uncertain, it just works
                                        },
                            'small': {'w': 53, #px
                                      'h': 53, #px
                                      'ir': 1.6, #units unknown, meaning uncertain, it just works
                                        },
                            },
                'need': {'large': {'w': 85, #px
                                   'h': 85, #px
                                   'ir': 1.6, #units unknown, meaning uncertain, it just works
                                    },
                         'medium': {'w': 85, #px
                                    'h': 85, #px
                                    'ir': 1.6, #units unknown, meaning uncertain, it just works
                                    },
                         'small': {'w': 85, #px
                                   'h': 85, #px
                                   'ir': 1.6, #units unknown, meaning uncertain, it just works
                                    },
                        },
                'goal': {'large': {'w': 85, #px
                                   'h': 85, #px
                                   'ir': 1.6, #units unknown, meaning uncertain, it just works
                                    },
                         'medium': {'w': 85, #px
                                    'h': 85, #px
                                    'ir': 1.6, #units unknown, meaning uncertain, it just works
                                    },
                         'small': {'w': 53, #px
                                   'h': 53, #px
                                   'ir': 1.6, #units unknown, meaning uncertain, it just works
                                    },
                        },
}

ARGB_DONUT_CHART_PLEDGES = (0.345, 0.435, 0.0196, 1, 'solid') # '#586F05'
ARGB_DONUT_CHART_REDONATIONS = (0.553, 0.702, 0.0314, 1, 'solid') # '#8DB308'
ARGB_DONUT_CHART_OTHER_SOURCES = (0.937, 0.737, 0.035, 1, 'solid') # '#EFBC09'
ARGB_DONUT_CHART_BACKGROUND = (0.929, 0.922, 0.922, 1, 'solid') # '#EDEBEA'

TOTAL_DEGREES = 360 #captain obvious

RGBCOLOR_DONUT_CHART_PLEDGES = '586F05'
RGBCOLOR_DONUT_CHART_REDONATIONS = '8DB308'
RGBCOLOR_DONUT_CHART_OTHER_SOURCES = 'EFBC09'
RGBCOLOR_DONUT_CHART_BACKGROUND = 'EDEBEA'

MINIMAL_DEFAULT_PLEDGES_DEGREES = 5  #empty chart looks better if a tiny colored bit is shown
MINIMAL_DEFAULT_REDONATIONS_DEGREES = 3
MINIMAL_DEFAULT_OTHER_SOURCES_DEGREES = 2

#user accounts
MINIMAL_SUPPORTED_PROJECTS_COUNT_FOR_PUBLIC = 10

