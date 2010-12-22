from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^manager/', include('manager.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
	(r'^/?$', 'manager.equipos.views.index'),
	
	
	# Modulo de login
	(r'^registrarse/', 'manager.equipos.views.registrar_usuario'),
    (r'^cuentas/logout/$', 'django.contrib.auth.views.logout'),
   	(r'^cuentas/login/$', 'django.contrib.auth.views.login'),
    (r'^cuentas/perfil/$', 'manager.equipos.views.perfil_usuario'),

	# Modulo de equipos
   	#(r'^equipos/(?P<equipo_id>\d+)/$', 'manager.equipos.views.ver_equipo'),
)
