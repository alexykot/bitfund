# Django settings for bitfund project.

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',

    # installed middleware
    'social_auth.middleware.SocialAuthExceptionMiddleware',

    #project custom middleware
    'bitfund.core.middleware.HiddenEntranceMiddleware',
    'bitfund.core.middleware.MangoInitMiddleware',
    'bitfund.core.middleware.UserCardAccountCheckMiddleware',
    'bitfund.core.middleware.UserProjectsCountMiddleware',
    'bitfund.core.middleware.SaveUserTokenMiddleware',
#    'bitfund.core.middleware.SQLLogToConsoleMiddleware',

    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'bitfund.core.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'bitfund.core.wsgi.application'

INSTALLED_APPS = (
    # standard aps                  
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',


    # proejct apps
    'bitfund.core',          # bitfund core
    'bitfund.pledger',          # pledger account
    'bitfund.project',          # project

    # installed thirdparty apps
    # utilities 
    'south',            # DB migrations
    'debug_toolbar',    # debug toolbar

    # functionality extensions
    'crispy_forms',     # bootstrap based forms styling
    'django_cleanup',   # autodelete old files for FileField
    'widget_tweaks',    # easy CSS stryling for forms
    'guardian',         # object permissions checking
    'easy_thumbnails',  # easier thumbnailing
    'tastypie',         # API framework
    'social_auth',      # authentication via various big name sites
    'model_utils',      # models utilities
    'gravatar',         # gravatar avatars
    'ajaxuploader',     # ajax files upload

    #'selectable',       # select fields ajax autocomplete lookups
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    # django defaults
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',

    #installed processors
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_login_redirect',

    #custom processors
    # 'bitfund.core.context_processors.frontend_header_template_data',
    # 'bitfund.core.context_processors.user_is_stranger',
)


AUTH_PROFILE_MODULE = 'bitfund.pledger.views.Profile'

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.contrib.github.GithubBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    # 'social_auth.backends.yahoo.YahooBackend',
    # 'social_auth.backends.browserid.BrowserIDBackend',
    # 'social_auth.backends.contrib.linkedin.LinkedinBackend',
    # 'social_auth.backends.contrib.disqus.DisqusBackend',
    # 'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    # 'social_auth.backends.contrib.orkut.OrkutBackend',
    # 'social_auth.backends.contrib.foursquare.FoursquareBackend',
    # 'social_auth.backends.contrib.vkontakte.VKontakteBackend',
    # 'social_auth.backends.contrib.live.LiveBackend',
    # 'social_auth.backends.contrib.skyrock.SkyrockBackend',
    # 'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
    # 'social_auth.backends.contrib.readability.ReadabilityBackend',
    # 'social_auth.backends.OpenIDBackend',

    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)


# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True