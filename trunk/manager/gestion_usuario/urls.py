# -*- coding: utf-8 -*-
"""
Copyright 2013 by
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
	(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
	(r'^login/$', 'gestion_usuario.views.principal'),
	(r'^confirmar/(?P<clave>\w+)/$', 'gestion_usuario.views.activar_usuario'),
	(r'^notificaciones/', include('gestion_usuario.gestion_notificacion.urls')),
	(r'^password/cambiar/$', 'gestion_usuario.views.principal'),
	(r'^password/cambiar/hecho/$', 'django.contrib.auth.views.logout_then_login'),
	(r'^password/recordar/$', 'django.contrib.auth.views.password_reset', {}),
	(r'^password/recordar/completar/$', 'django.contrib.auth.views.password_reset_complete', {}),
	(r'^password/recordar/hecho/$', 'django.contrib.auth.views.password_reset_done', {}),
	(r'^password/recordar/confirmar/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {}),
)
