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
from gestion_sistema.gestion_partido import views

urlpatterns = [
   	# Modulo de partidos
   	url(r'^ver/$', views.ver_partido),
   	url(r'^ver/(?P<partido_id>\d+)/$', views.ver_partido_id),
   	url(r'^mis_partidos/$', views.ver_partidos_propios),
   	url(r'^proximo/$', views.proximo_partido),
   	url(r'^repeticion/$', views.ver_repeticion_partido),
   	url(r'^preparar/$', views.preparar_partido),
   	url(r'^jugar/$', views.jugar_partido),
]
