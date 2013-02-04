# custom bitfund settings
PROJECT_VERSION = '0.1'

PROTOTYPE_HIDDEN_ENTRANCE                       = 'hidden-entrance'
PROTOTYPE_LANDING_PAGE_URL                      = '/index.htm'

DEFAULT_PASSWORD                                = 'asdasdasd' #default password set to semianonimous users
ABANDONED_ACCOUNT_REGISTRATION_PARAMETER_NAME   = 'renew-registration' 
 

MAX_NEEDS_PER_PROJECT = 10
MAX_GOALS_PER_PROJECT = 10

DEFAULT_MONTHLY_DONATION_AMOUNT                 = 1 # default donation in $
DEFAULT_ONETIME_DONATION_AMOUNT                 = 5 # default donation in $

MAX_EXPENSES_ON_PROJECT_PAGE                    = 1 # max needs and goals to show in the list near Pledge button 
MAX_GOALS_ON_PROJECT_PAGE                       = 2 # max goals to show on the project page
MAX_USERS_ON_PROJECT_PAGE                       = 4 # max users to show in the Team block

DATE_INPUT_FORMATS = ('%d %b %Y', '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b %d %Y', '%b %d, %Y', '%d %b, %Y', '%B %d %Y', '%B %d, %Y', '%d %B %Y', '%d %B, %Y')

FAKE_CHECKOUT_SYSTEM_URL = '/pledger/fake_external_checkout'

PROJECT_USER_ROLES_WEIGHTS = (
    ('treasurer',  50),
    ('maintainer', 30),
    ('developer',  15),
)


TIME_TO_SHOW_HOURS = 48 #when it's time to show hours instead of days for "time to go" for budget and goals, in hours       