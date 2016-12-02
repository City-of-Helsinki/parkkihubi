import os

from environ import Env
from raven import fetch_git_sha
from raven.exceptions import InvalidGitRepository

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assert os.path.isfile(os.path.join(BASE_DIR, 'manage.py'))

#####################
# Local environment #
#####################
env = Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

########################
# Django core settings #
########################
DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env.str('SECRET_KEY', default=('' if not DEBUG else 'xxx'))
ALLOWED_HOSTS = ['*']

#########
# Paths #
#########
default_var_root = os.path.join(BASE_DIR, 'var')
user_var_root = os.path.expanduser('~/var')
if os.path.isdir(user_var_root):
    default_var_root = user_var_root
VAR_ROOT = env.str('VAR_ROOT', default_var_root)

# Create var root if it doesn't exist
if not os.path.isdir(VAR_ROOT):
    print('Creating var root %s' % VAR_ROOT)
    os.makedirs(VAR_ROOT)

MEDIA_ROOT = os.path.join(VAR_ROOT, 'media')
MEDIA_URL = '/media/'
ROOT_URLCONF = 'parkkihubi.urls'
STATIC_ROOT = os.path.join(VAR_ROOT, 'static')
STATIC_URL = '/static/'

############
# Database #
############
if os.environ.get('CI'):
    default_database_url = 'postgis://postgres:@localhost/parkkihubi'
else:
    default_database_url = 'postgis://parkkihubi:parkkihubi@localhost/parkkihubi'

DATABASES = {
    'default': env.db_url(
        default=default_database_url
    )
}

##########
# Caches #
##########
CACHES = {'default': env.cache_url(default='locmemcache://')}

##################
# Installed apps #
##################
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'raven.contrib.django.raven_compat',
    'parkkihubi'
]

##############
# Middleware #
##############
MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

#############
# Templates #
#############
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

##########
# Sentry #
##########
try:
    git_sha = fetch_git_sha(BASE_DIR)
except InvalidGitRepository:
    git_sha = None
RAVEN_CONFIG = {
    'dsn': env.str('SENTRY_DSN', default=None),
    'release': git_sha,
}

############################
# Languages & Localization #
############################
LANGUAGE_CODE = 'fi'
TIME_ZONE = 'Europe/Helsinki'
USE_I18N = True
USE_L10N = True
USE_TZ = True

########
# WSGI #
########
WSGI_APPLICATION = 'parkkihubi.wsgi.application'

##########
# Mailer #
##########
vars().update(env.email_url(
    default=('consolemail://' if DEBUG else 'smtp://localhost:25')
))
