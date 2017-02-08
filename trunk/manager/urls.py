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

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

# Para que funcione lo necesario para media
from django.views.static import *

# Habilitar la administracion
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
	# Administracion
	url(r'^admin/', include(admin.site.urls)),

	# Modulos
	url(r'^cuentas/', include('gestion_usuario.urls')),
	url(r'^equipos/', include('gestion_sistema.gestion_equipo.urls')),
	url(r'^ligas/', include('gestion_sistema.gestion_liga.urls')),
	url(r'^clasificacion/', include('gestion_sistema.gestion_clasificacion.urls')),
	url(r'^jornadas/', include('gestion_sistema.gestion_jornada.urls')),
	url(r'^partidos/', include('gestion_sistema.gestion_partido.urls')),
	url(r'^jugadores/', include('gestion_sistema.gestion_jugador.urls')),
	url(r'^mercado/subastas/', include('gestion_mercado.gestion_subasta.urls')),

	# Gestion basica de la web
	url(r'', include('gestion_base.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
