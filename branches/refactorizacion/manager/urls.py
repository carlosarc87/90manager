from django.conf.urls.defaults import *

# Para que funcione lo necesario para media
from django.views.static import *
from django.conf import settings

# Habilitar la administracion
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Required to make static serving work
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    # Administracion
    (r'^admin/', include(admin.site.urls)),

	# Modulos
	(r'^cuentas/', include('gestion_usuario.urls')),
	(r'^equipos/', include('gestion_sistema.gestion_equipo.urls')),
	(r'^liga/', include('gestion_sistema.gestion_liga.urls')),
	(r'^jornada/', include('gestion_sistema.gestion_jornada.urls')),
	(r'^partido/', include('gestion_sistema.gestion_partido.urls')),
	(r'^jugador/', include('gestion_sistema.gestion_jugador.urls')),

	# Gestion basica de la web
	(r'', include('gestion_base.urls')),
)
