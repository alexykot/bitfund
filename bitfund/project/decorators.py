from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse 
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.decorators import available_attrs

from bitfund.project.forms import *

"""
def user_is_project_maintainer(request):
    def decorator(view_func, *args, **kwargs):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, project_key, *args, **kwargs):
            project = get_object_or_404(Project, key=project_key)

            if (project.maintainer_id != request.user.id) :
                return HttpResponseRedirect(reverse('bitfund.core.views.index', args=(project.key,)))
            else :
                view_func(request, *args, **kwargs)
            
        return _wrapped_view
    return decorator
"""
def user_is_project_maintainer(view):
    @wraps(view)
    def _wrapped_view(request, project_key, *args, **kwargs):
        project = get_object_or_404(Project, key=project_key)
        if (project.maintainer_id != request.user.id) :
            return HttpResponseForbidden()
        else :
            return view(request, project_key, *args, **kwargs)
    return _wrapped_view

def user_is_not_project_maintainer(view):
    @wraps(view)
    def _wrapped_view(request, project_key, *args, **kwargs):
        project = get_object_or_404(Project, key=project_key)
        if (project.maintainer_id == request.user.id) :
            return HttpResponseForbidden()
        else :
            return view(request, project_key, *args, **kwargs)
    return _wrapped_view





"""


TypeError at /projects/shotwheel/crud_linked_project
_wrapped_view() takes at least 2 arguments (1 given)

Request Method: GET
Request URL: http://127.0.0.1:8080/projects/shotwheel/crud_linked_project
Django Version: 1.4.3
Python Executable: /usr/bin/python
Python Version: 2.7.3
Python Path: ['/home/alexykot/Work/Projects/BitFund/Sources', '/home/alexykot/Work/Projects/BitFund/Sources/bitfund', '/usr/lib/python2.7', '/usr/lib/python2.7/plat-linux2', '/usr/lib/python2.7/lib-tk', '/usr/lib/python2.7/lib-old', '/usr/lib/python2.7/lib-dynload', '/usr/local/lib/python2.7/dist-packages', '/usr/lib/python2.7/dist-packages', '/usr/lib/python2.7/dist-packages/PIL', '/usr/lib/python2.7/dist-packages/gst-0.10', '/usr/lib/python2.7/dist-packages/gtk-2.0', '/usr/lib/pymodules/python2.7', '/usr/lib/python2.7/dist-packages/ubuntu-sso-client', '/usr/lib/python2.7/dist-packages/ubuntuone-client', '/usr/lib/python2.7/dist-packages/ubuntuone-control-panel', '/usr/lib/python2.7/dist-packages/ubuntuone-couch', '/usr/lib/python2.7/dist-packages/ubuntuone-installer', '/usr/lib/python2.7/dist-packages/ubuntuone-storage-protocol']
Server time: Mon, 18 Feb 2013 23:11:05 +0000
Installed Applications:
('django.contrib.auth',
 'django.contrib.contenttypes',
 'django.contrib.sessions',
 'django.contrib.sites',
 'django.contrib.messages',
 'django.contrib.staticfiles',
 'django.contrib.admin',
 'bitfund.core',
 'bitfund.pledger',
 'bitfund.project',
 'south',
 'debug_toolbar',
 'crispy_forms',
 'django_cleanup',
 'widget_tweaks',
 'guardian',
 'easy_thumbnails',
 'tastypie',
 'model_utils',
 'selectable')
Installed Middleware:
('debug_toolbar.middleware.DebugToolbarMiddleware',
 'django.middleware.common.CommonMiddleware',
 'django.contrib.sessions.middleware.SessionMiddleware',
 'django.middleware.csrf.CsrfViewMiddleware',
 'django.contrib.auth.middleware.AuthenticationMiddleware',
 'django.contrib.messages.middleware.MessageMiddleware',
 'django.middleware.transaction.TransactionMiddleware',
 'bitfund.core.middleware.HiddenEntranceMiddleware',
 'bitfund.core.middleware.SaveUserTokenMiddleware')

Traceback:
File "/usr/local/lib/python2.7/dist-packages/django/core/handlers/base.py" in get_response
  111.                         response = callback(request, *callback_args, **callback_kwargs)
File "/home/alexykot/Work/Projects/BitFund/Sources/bitfund/core/decorators.py" in wrap
  7.         return f(request, *args, **kwargs)

Exception Type: TypeError at /projects/shotwheel/crud_linked_project
Exception Value: _wrapped_view() takes at least 2 arguments (1 given)
Request information:
GET: No GET data

POST: No POST data

FILES: No FILES data

COOKIES:
__utmz = '96992031.1359306397.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
sessionid = '93c56f09da98e6b75458e454fa65fdd9'
djdt = 'hide'
csrftoken = '1pJZdKfAJRkGUbBF4IBGYTjb6XprZfKc'
__utma = '96992031.624591776.1359306397.1361226054.1361228897.11'
__utmb = '96992031.1.10.1361228897'
__utmc = '96992031'

META:
LC_NUMERIC = 'en_GB.UTF-8'
RUN_MAIN = 'true'
HTTP_REFERER = 'http://127.0.0.1:8080/projects/shotwheel/linked_projects'
wsgi.version =
SERVER_PROTOCOL = 'HTTP/1.1'
SERVER_SOFTWARE = 'WSGIServer/0.1 Python/2.7.3'
SCRIPT_NAME = u''
LESSOPEN = '| /usr/bin/lesspipe %s'
QUERY_STRING = ''
REQUEST_METHOD = 'GET'
LOGNAME = 'root'
USER = 'root'
PATH = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games'
LC_PAPER = 'en_GB.UTF-8'
HOME = '/root'
DISPLAY = ':1'
LANG = 'en_US.UTF-8'
TERM = 'xterm'
SHELL = '/bin/bash'
TZ = 'Europe/London'
XDG_SESSION_COOKIE = '8699a662b12e989ffe6ebb0a00000001-1361118171.550949-517469929'
SERVER_NAME = 'localhost'
REMOTE_ADDR = '127.0.0.1'
LC_MEASUREMENT = 'en_GB.UTF-8'
wsgi.url_scheme = 'http'
SERVER_PORT = '8080'
SUDO_USER = 'alexykot'
LC_MONETARY = 'en_GB.UTF-8'
USERNAME = 'root'
CONTENT_LENGTH = ''
HTTP_X_REQUESTED_WITH = 'XMLHttpRequest'
SUDO_COMMAND = '/bin/su'
LC_ADDRESS = 'en_GB.UTF-8'
SUDO_UID = '1000'
wsgi.input = <socket._fileobject object at 0xb602f8ac>
HTTP_USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0'
HTTP_HOST = '127.0.0.1:8080'
wsgi.multithread = True
HTTP_CONNECTION = 'keep-alive'
_ = '/home/alexykot/Work/Projects/BitFund/Sources/bitfund/manage.py'
XAUTHORITY = '/home/alexykot/.Xauthority'
HTTP_ACCEPT = 'text/html, */*; q=0.01'
LC_IDENTIFICATION = 'en_GB.UTF-8'
SUDO_GID = '1000'
wsgi.file_wrapper = ''
LESSCLOSE = '/usr/bin/lesspipe %s %s'
GATEWAY_INTERFACE = 'CGI/1.1'
wsgi.run_once = False
CSRF_COOKIE = '1pJZdKfAJRkGUbBF4IBGYTjb6XprZfKc'
wsgi.errors = <open file '<stderr>', mode 'w' at 0xb73350d0>
wsgi.multiprocess = False
HTTP_ACCEPT_LANGUAGE = 'en-US,en;q=0.5'
LC_TELEPHONE = 'en_GB.UTF-8'
SHLVL = '1'
PWD = '/home/alexykot'
DJANGO_SETTINGS_MODULE = 'bitfund.core.settings.django'
CONTENT_TYPE = 'text/plain'
LC_NAME = 'en_GB.UTF-8'
MAIL = '/var/mail/root'
LC_TIME = 'en_GB.UTF-8'
LS_COLORS = 'rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arj=01;31:*.taz=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.zip=01;31:*.z=01;31:*.Z=01;31:*.dz=01;31:*.gz=01;31:*.lz=01;31:*.xz=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.jpg=01;35:*.jpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.axv=01;35:*.anx=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.axa=00;36:*.oga=00;36:*.spx=00;36:*.xspf=00;36:'
REMOTE_HOST = ''
HTTP_ACCEPT_ENCODING = 'gzip, deflate'
HTTP_COOKIE = 'csrftoken=1pJZdKfAJRkGUbBF4IBGYTjb6XprZfKc; __utma=96992031.624591776.1359306397.1361226054.1361228897.11; __utmz=96992031.1359306397.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); sessionid=93c56f09da98e6b75458e454fa65fdd9; djdt=hide; __utmc=96992031; __utmb=96992031.1.10.1361228897'
PATH_INFO = u'/projects/shotwheel/crud_linked_project'

Settings:
Using settings module bitfund.core.settings.django
DEBUG_TOOLBAR_PANELS =
SELECTABLE_ESCAPED_KEYS = u'********************'
USE_L10N = True
USE_THOUSAND_SEPARATOR = False
CSRF_COOKIE_SECURE = False
LANGUAGE_CODE = 'en-gb'
ROOT_URLCONF = 'bitfund.core.urls'
MANAGERS =
DEFAULT_CHARSET = 'utf-8'
SITE_CURRENCY_CODE = 'USD'
STATIC_ROOT = '/home/alexykot/Work/Projects/BitFund/Sources/bitfund/web/static/'
CALCULATIONS_PRECISION = 28
API_TARGET_MONTH_PARAM_NAME = u'********************'
SELECTABLE_MAX_LIMIT = 25
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'
EMAIL_SUBJECT_PREFIX = '[Django] '
SEND_BROKEN_LINK_EMAILS = False
URL_VALIDATOR_USER_AGENT = 'Django/1.4.3 (https://www.djangoproject.com)'
STATICFILES_FINDERS =
DATE_FORMAT = 'N j, Y'
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_NAME = 'sessionid'
ADMIN_FOR =
TIME_INPUT_FORMATS =
DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql', 'TEST_MIRROR': None, 'NAME': 'bitfund_dev', 'TEST_CHARSET': None, 'TIME_ZONE': 'UTC', 'TEST_COLLATION': None, 'PORT': '3306', 'HOST': '88.198.122.134', 'USER': 'alexy', 'TEST_NAME': None, 'PASSWORD': u'********************', 'OPTIONS': {}}}
DEFAULT_PASSWORD = u'********************'
DEFAULT_ONETIME_DONATION_AMOUNT = 5
FILE_UPLOAD_PERMISSIONS = None
FILE_UPLOAD_HANDLERS =
DEFAULT_CONTENT_TYPE = 'text/html'
MAX_NEEDS_PER_PROJECT = 10
TASTYPIE_FULL_DEBUG = True
APPEND_SLASH = True
FIRST_DAY_OF_WEEK = 0
DATABASE_ROUTERS = []
FAKE_CHECKOUT_SYSTEM_URL = '/pledger/fake_external_checkout'
YEAR_MONTH_FORMAT = 'F Y'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
CACHES = {'default': {'LOCATION': '127.0.0.1:11211', 'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache'}}
SERVER_EMAIL = 'root@localhost'
SESSION_COOKIE_PATH = '/'
MIDDLEWARE_CLASSES =
USE_I18N = True
THOUSAND_SEPARATOR = ','
SECRET_KEY = u'********************'
LANGUAGE_COOKIE_NAME = 'django_language'
DEFAULT_INDEX_TABLESPACE = ''
TRANSACTIONS_MANAGED = False
LOGGING_CONFIG = 'django.utils.log.dictConfig'
PROTOTYPE_LANDING_PAGE_URL = '/index.htm'
TEMPLATE_LOADERS =
MAX_GOALS_PER_PROJECT = 10
WSGI_APPLICATION = 'bitfund.core.wsgi.application'
TEMPLATE_DEBUG = True
X_FRAME_OPTIONS = 'SAMEORIGIN'
AUTHENTICATION_BACKENDS =
FORCE_SCRIPT_NAME = None
USE_X_FORWARDED_HOST = False
SIGNING_BACKEND = 'django.core.signing.TimestampSigner'
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_DOMAIN = None
FILE_CHARSET = 'utf-8'
DEBUG = True
TIME_TO_SHOW_HOURS = 48
SESSION_FILE_PATH = None
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
INSTALLED_APPS =
LANGUAGES =
COMMENTS_ALLOW_PROFANITIES = False
STATICFILES_DIRS = '/home/alexykot/Work/Projects/BitFund/Sources/bitfund/static/'
BITFUND_OWN_PROJECT_ID = 5
PREPEND_WWW = False
SECURE_PROXY_SSL_HEADER = None
PASSWORD_RESET_TIMEOUT_DAYS = u'********************'
SESSION_COOKIE_HTTPONLY = True
DEBUG_PROPAGATE_EXCEPTIONS = False
MONTH_DAY_FORMAT = 'F j'
LOGIN_URL = '/login/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
ABANDONED_ACCOUNT_REGISTRATION_PARAMETER_NAME = 'renew-registration'
TIME_FORMAT = 'P'
DATE_INPUT_FORMATS =
CSRF_COOKIE_NAME = 'csrftoken'
EMAIL_HOST_PASSWORD = u'********************'
AUTH_PROFILE_MODULE = 'pledger.Profile'
CACHE_MIDDLEWARE_ALIAS = 'default'
SESSION_SAVE_EVERY_REQUEST = False
NUMBER_GROUPING = 0
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
CSRF_COOKIE_PATH = '/'
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGGING = {'loggers': {'django.request': {'handlers': ['mail_admins'], 'propagate': True, 'level': 'ERROR'}}, 'version': 1, 'disable_existing_loggers': False, 'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}}, 'handlers': {'mail_admins': {'class': 'django.utils.log.AdminEmailHandler', 'filters': ['require_debug_false'], 'level': 'ERROR'}}}
IGNORABLE_404_URLS =
LOCALE_PATHS =
TEMPLATE_STRING_IF_INVALID = ''
LOGOUT_URL = '/accounts/logout/'
EMAIL_USE_TLS = False
FIXTURE_DIRS =
EMAIL_HOST = 'localhost'
API_USER_TOKEN_PARAM_NAME = u'********************'
MEDIA_ROOT = '/home/alexykot/Work/Projects/BitFund/Sources/bitfund/web/uploads/'
DEFAULT_EXCEPTION_REPORTER_FILTER = 'django.views.debug.SafeExceptionReporterFilter'
ADMINS =
FORMAT_MODULE_PATH = None
DEFAULT_FROM_EMAIL = 'webmaster@localhost'
MEDIA_URL = '/uploads/'
DATETIME_FORMAT = 'N j, Y, P'
TEMPLATE_DIRS = '/home/alexykot/Work/Projects/BitFund/Sources/bitfund/templates'
DEFAULT_MONTHLY_DONATION_AMOUNT = 1
SITE_ID = 1
DISALLOWED_USER_AGENTS =
ALLOWED_INCLUDE_ROOTS =
PROJECT_VERSION = '0.1'
DECIMAL_SEPARATOR = '.'
PROTOTYPE_HIDDEN_ENTRANCE = 'hidden-entrance'
SHORT_DATE_FORMAT = 'm/d/Y'
MAX_EXPENSES_ON_PROJECT_PAGE = 1
TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'
SITE_CURRENCY_SIGN = '$'
CACHE_MIDDLEWARE_KEY_PREFIX = u'********************'
TIME_ZONE = 'Europe/London'
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_TABLESPACE = ''
TEMPLATE_CONTEXT_PROCESSORS =
SESSION_COOKIE_AGE = 1209600
SETTINGS_MODULE = 'bitfund.core.settings.django'
USE_ETAGS = False
LANGUAGES_BIDI =
FILE_UPLOAD_TEMP_DIR = None
INTERNAL_IPS =
STATIC_URL = '/static/'
EMAIL_PORT = '25'
USE_TZ = True
SHORT_DATETIME_FORMAT = 'm/d/Y P'
PASSWORD_HASHERS = u'********************'
ABSOLUTE_URL_OVERRIDES = {}
CACHE_MIDDLEWARE_SECONDS = 600
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}
ANONYMOUS_USER_ID = -1
DATETIME_INPUT_FORMATS =
EMAIL_HOST_USER = 'root'
PROFANITIES_LIST = u'********************'

You're seeing this error because you have DEBUG = True in your
Django settings file. Change that to False, and Django will
display a standard 500 page.


4 requests

22 KB

9.76s



"""