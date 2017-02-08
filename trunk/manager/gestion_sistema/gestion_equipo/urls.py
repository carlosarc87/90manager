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

from django.conf.urls import url
from gestion_sistema.gestion_equipo import views

urlpatterns = [
	# Modulo de equipos
   	url(r'^ver/$', views.ver_equipo),
   	url(r'^mi_equipo/$', views.ver_equipo_propio),
   	url(r'^ver/(?P<equipo_id>\d+)/$', views.ver_equipo_id),
   	url(r'^crear/$', views.crear_equipo),
   	url(r'^listar/$', views.listar_equipos_liga),
]
