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

    # Habilitar la administracion
    (r'^admin/', include(admin.site.urls)),
	(r'^/?$', 'manager.gestion_entrenador.views.perfil_usuario'),
	
	# Modulo de login
    (r'^cuentas/logout/$', 'django.contrib.auth.views.logout'),
   	(r'^cuentas/login/$', 'django.contrib.auth.views.login'),
    (r'^cuentas/perfil/$', 'manager.gestion_entrenador.views.perfil_usuario'),
	(r'^cuentas/registrar/', 'manager.gestion_entrenador.views.registrar_usuario'),

	# Modulo de equipos
   	(r'^equipos/ver/(?P<equipo_id>\d+)/$', 'manager.gestion_entrenador.views.ver_equipo'),
   	(r'^equipos/crear/(?P<liga_id>\d+)/$', 'manager.gestion_entrenador.views.crear_equipo'),
   	
   	# Modulo de ligas
   	(r'^ligas/crear/$', 'manager.gestion_entrenador.views.crear_liga'),
   	(r'^ligas/ver/(?P<liga_id>\d+)/$', 'manager.gestion_entrenador.views.ver_liga'),
   	(r'^ligas/avanzar/(?P<liga_id>\d+)/$', 'manager.gestion_entrenador.views.avanzar_jornada_liga'),   	
   	(r'^ligas/activar/(?P<liga_id>\d+)/$', 'manager.gestion_entrenador.views.activar_liga'),
   	
   	# Modulo de jugadores
   	(r'^jugadores/ver/(?P<jugador_id>\d+)/$', 'manager.gestion_entrenador.views.ver_jugador'),
   	
   	# Modulo de jornadas
   	(r'^jornadas/ver/(?P<jornada_id>\d+)/$', 'manager.gestion_entrenador.views.ver_jornada'),
   	
   	# Modulo de partidos
   	(r'^partidos/ver/(?P<partido_id>\d+)/$', 'manager.gestion_entrenador.views.ver_partido'),
   	(r'^partidos/preparar/(?P<partido_id>\d+)/$', 'manager.gestion_entrenador.views.preparar_partido'),
   	(r'^partidos/jugar/(?P<partido_id>\d+)/$', 'manager.gestion_entrenador.views.jugar_partido'),
)
