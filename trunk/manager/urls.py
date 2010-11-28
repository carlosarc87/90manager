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
	#(r'^registrarse/', 'manager.equipos.views.registrar_usuario'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
   	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
   	(r'^accounts/$', 'django.contrib.auth.views.login'),
    #(r'^accounts/profile', 'manager.equipos.views.index'),

   	(r'^equipos/(?P<equipo_id>\d+)/$', 'manager.equipos.views.ver_equipo'),
   	(r'^equipos/(?P<equipo_id>\d+)/editar$', 'manager.equipos.views.editar_equipo'),
)
