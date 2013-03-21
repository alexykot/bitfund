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

# django-tastypie
TASTYPIE_FULL_DEBUG = True

#social auth
#social auth secrets and other stuff that should not be in the repository
from bitfund.core.settings.secrets import *
LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL    = '/login/'

SOCIAL_AUTH_UID_LENGTH = 223 # as per http://django-social-auth.readthedocs.org/en/latest/configuration.html#tweaking-some-fields-length

SOCIAL_AUTH_FORCE_POST_DISCONNECT = True
SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['next',]

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    #'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'bitfund.pledger.models.create_profile',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details'
)