# Django settings for bitfund project.


#this is server related settings like DB access and local paths
from settings_server import *

#this is custom project settings not related to django, but used in this project 
from settings_project import *

#this is django extensions settings 
from settings_extensions import *


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
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    #project custom middleware 
    'bitfund.middleware.HiddenEntranceMiddleware',
    'bitfund.middleware.SaveUserTokenMiddleware',
    
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    
    # installed middleware
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'bitfund.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'bitfund.wsgi.application'

INSTALLED_APPS = (
    # standard aps                  
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    
    
    # proejct apps
    'bitfund',          # bitfund core 
    'pledger',          # pledger account
    'project',          # project
    'accounts',         # project
    
    # installed thirdparty apps
    # utilities 
    'south',            # DB migrations  
    'debug_toolbar',    # debug toolbar

    # functionality extensions
    'crispy_forms',         # bootstrap based forms styling
    'django_cleanup',       # autodelete old files for FileField
    'widget_tweaks',        # easy CSS stryling for forms
    'userena',              # user accounts enhanced
    'guardian',             # object permissions checking
    'easy_thumbnails',      # easier thumbnailing
    'tastypie',             # API framework
    'model_utils',          # models utilities
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
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    
    
    #custom processors
    'bitfund.context_processors.frontend_header_template_data',
    'bitfund.context_processors.user_is_stranger',
)

AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
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
