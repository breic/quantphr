# Django settings for quantphr project.

import socket
if socket.gethostname() == 'MacBook-5.local': 
	DEBUG = True
else: 
	DEBUG = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (	# use this to send email alerts when there is an exception, requires an email setup (see http://www.djangobook.com/en/2.0/chapter12/)
    ('Ben Reichardt', 'ben.reichardt@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'postgres',                      # Or path to database file if using sqlite3.
        'USER': 'quaphr',                      # Not used with sqlite3.
        'PASSWORD': 'hat9kazo8oidee6phyr',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	'/Users/breic/Documents/Programming/Django/projects/quantphr/quantphr/static',
	'/app/quantphr/static',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '$4e=u1ewibg+1z!!uv^g4t0++v&(7ad47qdzwx_j7)8$xm!357'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',	# uncommented for dajaxice
)

# Added for Dajaxice
TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.request",
                               "django.contrib.messages.context_processors.messages", 
						       #"social_auth.context_processors.social_auth_by_name_backends", # Adds a social_auth dict where each key is a provider name and its value is a UserSocialAuth instance if user has associated an account with that provider, otherwise None
						       #"social_auth.context_processors.social_auth_backends",	# Adds a social_auth dict with keys are associated, not_associated and backends. associated key is a list of UserSocialAuth instances associated with current user. not_associated is a list of providers names that the current user doesn't have any association yet. backends holds the list of backend names supported.
						       # "social_auth.context_processors.social_auth_by_type_backends", # Similar to social_auth_backends but each value is grouped by backend type openid, oauth2 and oauth.
							)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',	# for caching --- must be first
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',	# to prevent Cross Site Request Forgery
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',	# compresses responses to save bandwidth
    'django.middleware.cache.FetchFromCacheMiddleware',	# for caching --- must be last (meaning it is loaded first)
)

if DEBUG: 
	CACHE_BACKEND = 'dummy:///'		# dummy caching (for development) implements the cache interface without doing anything
else: 
	CACHE_BACKEND = 'locmem:///'	# local memory caching (per process), database caching is also easy to set up (see http://www.djangobook.com/en/2.0/chapter15/), but memcached is way faster
CACHE_MIDDLEWARE_SECONDS = 300	# cache each paper for 300 seconds (5 minutes)
CACHE_MIDDLEWARE_KEY_PREFIX = ''

ROOT_URLCONF = 'quantphr.urls'

import os.path
TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
    '/app/quantphr/templates',	# directory used by Heroku 
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #'/Users/breic/Documents/Programming/Django/projects/quantphr/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    #'django.contrib.messages',
    'django.contrib.staticfiles',
    'arxiv',
    'user',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
	#'social_auth',
	'django_openid_auth',
    'ajax',		# app containing the dajaxice server-side functions
	'dajaxice',	# asynchronous communication core of the dajaxproject ajax tool
	'south',	# database migration tool (e.g., for adding fields to existing models) --- after adding this, run ./manage.py syncdb and ./manage.py convert_to_south myapp to finish the installation --- then ./manage.py schemamigration myapp --auto and ./manage.py migrate myapp are the basic commands to migrate a database
)

DAJAXICE_MEDIA_PREFIX="dajaxice"	# dajaxice needs this line (prefix for the urls that dajaxice creates), but not the next two
DAJAXICE_DEBUG = True
DAJAXICE_JS_DOCSTRINGS = True
#DAJAXICE_NOTIFY_EXCEPTIONS = True
#DAJAXICE_FUNCTIONS = ( 	# only needed with older versions of dajaxice
#        'ajax.myexample', 
#)

###
# Configuration for django-openid-auth
###
AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)
OPENID_CREATE_USERS = True
OPENID_UPDATE_DETAILS_FROM_SREG = True
LOGIN_URL = '/openid/login/'
LOGIN_REDIRECT_URL = '/'
# For Media
#SITE_MEDIA_PATH = os.path.join(os.path.abspath(os.path.curdir), 'static')
# For Profiles
AUTH_PROFILE_MODULE = 'user.UserProfile'
OPENID_SREG_REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

####
## Configuration for django-social-auth
####
#AUTHENTICATION_BACKENDS = (
##    'social_auth.backends.twitter.TwitterBackend',
##    'social_auth.backends.facebook.FacebookBackend',
##    'social_auth.backends.google.GoogleOAuthBackend',
#    'social_auth.backends.google.GoogleOAuth2Backend',
#    'social_auth.backends.google.GoogleBackend',
##    'social_auth.backends.yahoo.YahooBackend',
##    'social_auth.backends.browserid.BrowserIDBackend',
##    'social_auth.backends.contrib.linkedin.LinkedinBackend',
##    'social_auth.backends.contrib.livejournal.LiveJournalBackend',
##    'social_auth.backends.contrib.orkut.OrkutBackend',
##    'social_auth.backends.contrib.foursquare.FoursquareBackend',
##    'social_auth.backends.contrib.github.GithubBackend',
##    'social_auth.backends.contrib.dropbox.DropboxBackend',
##    'social_auth.backends.contrib.flickr.FlickrBackend',
##    'social_auth.backends.contrib.instagram.InstagramBackend',
#    'social_auth.backends.OpenIDBackend',
#    'django_openid_auth.auth.OpenIDBackend',
#    'django.contrib.auth.backends.ModelBackend',
#)
##TWITTER_CONSUMER_KEY         = ''
##TWITTER_CONSUMER_SECRET      = ''
##FACEBOOK_APP_ID              = ''
##FACEBOOK_API_SECRET          = ''
##LINKEDIN_CONSUMER_KEY        = ''
##LINKEDIN_CONSUMER_SECRET     = ''
##ORKUT_CONSUMER_KEY           = ''
##ORKUT_CONSUMER_SECRET        = ''
#GOOGLE_CONSUMER_KEY          = ''
#GOOGLE_CONSUMER_SECRET       = ''
#GOOGLE_OAUTH2_CLIENT_ID      = ''
#GOOGLE_OAUTH2_CLIENT_SECRET  = ''
##FOURSQUARE_CONSUMER_KEY      = ''
##FOURSQUARE_CONSUMER_SECRET   = ''
##GITHUB_APP_ID                = ''
##GITHUB_API_SECRET            = ''
##DROPBOX_APP_ID               = ''
##DROPBOX_API_SECRET           = ''
##FLICKR_APP_ID                = ''
##FLICKR_API_SECRET            = ''
##INSTAGRAM_CLIENT_ID          = ''
##INSTAGRAM_CLIENT_SECRET      = ''
#
##LOGIN_URL          = '/login-form/'
#LOGIN_REDIRECT_URL = '/' #'/logged-in/'
##LOGIN_ERROR_URL    = '/login-error/'
###SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/new-users-redirect-url/'
#
#SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
#SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'
#
##SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
##SOCIAL_AUTH_EXTRA_DATA = False
#SOCIAL_AUTH_EXPIRATION = 'expires'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
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
