
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
   #  ('root', 'root@localhost.com'),
)

LOGIN_URL = '/login/'

MANAGERS = ADMINS

#AUTH_PROFILE_MODULE = 'bitfund.UserProfile'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'bitfund_dev',
        'USER': 'alexy',
        'PASSWORD': '9nxb45G1M7BYb_IhaV2mxc8rOJbgk78q',
        'HOST': '88.198.122.134',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/home/cwiz/git/BitFund/Sources/source/uploads/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.b
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/uploads/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/cwiz/git/bitfund/bitfund/static/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (                    
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/cwiz/git/bitfund/bitfund/static/',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '!2%8m1%61x&amp;7k$+2hh!g*g(xyw4c2!p%u(m_ply=duz)+cqkmx'

TEMPLATE_DIRS = (
   '/home/cwiz/git/bitfund/bitfund/templates',
)


INTERNAL_IPS = ('127.0.0.1','192.168.51.120')


EMAIL_HOST          = 'localhost'
EMAIL_PORT          = '25' 
EMAIL_HOST_USER     = 'root'
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS       = False

