# -*- coding: utf-8 -*-
"""
Copyright 2017 by
    * Juan Miguel Lechuga Pérez
    * Jose Luis López Pino
    * Carlos Antonio Rivera Cabello

 This file is part of 90Manager.

    90Manager is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    90Manager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with 90Manager.  If not, see <http://www.gnu.org/licenses/>.

"""

import os

# Cargar datos sensibles (No deben de estar en el svn, son contraseñas y datos importantes)
try:
    import personales
except:  # No hay personales, cargar config por defecto
    vper = None
else:  # Hay personales, cargar configuracion de allí
    vper = personales.datos_personales

if vper:
    # Configuracion del e-mail
    EMAIL_HOST = vper['email_host']
    EMAIL_HOST_USER = vper['email_host_user']
    EMAIL_HOST_PASSWORD = vper['email_host_password']

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Variables del proyecto
URL_PROPIA = 'http://localhost:8000/'
RUTA = os.path.dirname(__file__) + "/"

# Mandar reporte de error por correo a los siguientes destinatarios cuando DEBUG = False
ADMINS = (('Juanmi', 'ciberjm@gmail.com'), ('Carlos', 'mail@carlosarc.com'))

MANAGERS = ADMINS

EMAIL_SUBJECT_PREFIX = '[90manager] '
SERVER_EMAIL = 'noreply@90manager.com'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dxlc%g2jveekf%npc_&(ip9x+0$9l^0(l8jk$@_^lju4)24c!v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Definición de aplicaciones
# El orden es importante

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones caseras
    'gestion_base',

    'gestion_usuario',
    'gestion_usuario.gestion_notificacion',

    'gestion_sistema.gestion_liga',
    'gestion_sistema.gestion_calendario',
    'gestion_sistema.gestion_jornada',
    'gestion_sistema.gestion_equipo',
    'gestion_sistema.gestion_partido',
    'gestion_sistema.gestion_clasificacion',
    'gestion_sistema.gestion_jugador',

    'gestion_mercado.gestion_subasta',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

AUTHENTICATION_BACKENDS = (
    'gestion_usuario.auth_backend.UsuarioModelBackend',
)

CUSTOM_USER_MODEL = 'gestion_usuario.Usuario'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            RUTA + "public/templates/",
            RUTA + "public/templates/juego/",
            RUTA + "public/templates/web/"
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(RUTA, 'sqlite3.db'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es-es'

SITE_ID = 1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = RUTA + "public/media"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Cambio de variables para la redireccion del login
LOGIN_URL = "/cuentas/login/"
LOGOUT_URL = "/cuentas/logout/"
LOGIN_REDIRECT_URL = "/tablon/"

# Variables de sesión
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
