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

from gestion_sistema.gestion_jornada import views

urlpatterns = [
   	# Modulo de jornadas
   	url(r'^actual/$', views.ver_jornada_actual),
   	url(r'^listar/$', views.listar_jornadas),
   	url(r'^ver/(?P<jornada_id>\d+)/$', views.ver_jornada_id),
   	url(r'^ver/$', views.ver_jornada),
]
