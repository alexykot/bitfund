# django-debug-toolbar
# installed apps settings
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    #'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    #'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
    #'HIDE_DJANGO_SQL': False,
    #'TAG': 'div',
    #'ENABLE_STACKTRACES' : True,
}

# django-guardian
ANONYMOUS_USER_ID   = -1
AUTH_PROFILE_MODULE = 'pledger.Profile'


# django-tastypie
TASTYPIE_FULL_DEBUG = True


#social auth
TWITTER_CONSUMER_KEY         = ''
TWITTER_CONSUMER_SECRET      = ''
FACEBOOK_APP_ID = ''
FACEBOOK_APP_SECRET = ''
GOOGLE_CONSUMER_KEY          = ''
GOOGLE_CONSUMER_SECRET       = ''
GOOGLE_OAUTH2_CLIENT_ID      = ''
GOOGLE_OAUTH2_CLIENT_SECRET  = ''

LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL    = '/login/'

SOCIAL_AUTH_UID_LENGTH = 223 # as per http://django-social-auth.readthedocs.org/en/latest/configuration.html#tweaking-some-fields-length

SOCIAL_AUTH_FORCE_POST_DISCONNECT = True
SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['next',]

#SOCIAL_AUTH_USER_MODEL = 'bitfund.pledger.models.Profile'
