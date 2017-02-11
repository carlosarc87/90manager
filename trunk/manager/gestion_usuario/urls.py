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

from django.conf.urls import include, url
from django.contrib.auth import views

from gestion_usuario import views as views_usuario

urlpatterns = [
    # Modulo de login
    url(r'^logout/$', views.logout_then_login),
    url(r'^login/$', views_usuario.principal),
    url(r'^confirmar/(?P<clave>\w+)/$', views_usuario.activar_usuario),
    url(r'^notificaciones/', include('gestion_usuario.gestion_notificacion.urls')),
    url(r'^password/cambiar/$', views_usuario.principal),
    url(r'^password/cambiar/hecho/$', views.logout_then_login),
    url(r'^password/recordar/$', views.password_reset, {}),
    url(r'^password/recordar/completar/$', views.password_reset_complete, {}),
    url(r'^password/recordar/hecho/$', views.password_reset_done, {}),
    url(r'^password/recordar/confirmar/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', views.password_reset_confirm, {}),
]
