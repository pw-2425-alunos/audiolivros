from pathlib import Path
from decouple import config, Csv


BASE_DIR = Path(__file__).resolve().parent.parent

#SECRET_KEY = 'django-insecure-^r()*8!u72cyv#cj&t%b-3vv)s(vr=to5x(socw_d8i%33t0o%'
SECRET_KEY = config('SECRET_KEY')

#DEBUG = True
DEBUG = config('DEBUG', default=False, cast=bool)

#ALLOWED_HOSTS = ['audioLivros.pythonanywhere.com']
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'tfc',
    'bootstrap5',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# REDIRECIONAMENTOS
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/biblioteca'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# GOOGLE LOGIN BEHAVIOR
SOCIALACCOUNT_LOGIN_ON_GET = False  # garante que NÃO entra automaticamente
SOCIALACCOUNT_AUTO_SIGNUP = False   # não cria contas automaticamente

SOCIALACCOUNT_ADAPTER = "tfc.adapters.NoNewSocialAccountAdapter"  # impede novo registo por Google

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_ALLOW_REGISTRATION = False

# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'beeaudiolivros@gmail.com'
EMAIL_HOST_PASSWORD = 'ycrqdotfodeyrbnb'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # necessário para allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

DB_ENGINE= config('DB_ENGINE', default='sqlite')

if DB_ENGINE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME'),
            'USER' : config('DB_USER'),
            'PASSWORD' : config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='3306'),
        }
    }
else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-pt'     # Português de Portugal
TIME_ZONE = 'Europe/Lisbon' # Fuso horário de Portugal continental
USE_I18N = True              # Ativa internacionalização
USE_L10N = True              # (opcional, Django < 4.0) Ativa formatação local
USE_TZ = True                # Usa timezone-aware datetimes

STATIC_URL = '/static/'
STATIC_ROOT = '/home/audioLivros/project/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/audioLivros/project/media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
