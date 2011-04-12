# -*- coding: utf-8 -*-
"""
Copyright 2011 by
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

from django.conf.urls.defaults import *

urlpatterns = patterns('',
	# Modulo de login
    (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'web/usuarios/logout.html'}),
   	(r'^login/$', 'gestion_usuario.views.principal'),
    (r'^perfil/$', 'gestion_usuario.views.perfil_usuario'),
	(r'^confirmar/(?P<clave>\w+)/$', 'gestion_usuario.views.activar_usuario'),
	(r'^notificaciones/', include('gestion_usuario.gestion_notificacion.urls')),
)
