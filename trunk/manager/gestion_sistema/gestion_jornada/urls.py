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
   	# Modulo de jornadas
   	(r'^ver/(?P<jornada_id>\d+)/$', 'gestion_sistema.gestion_jornada.views.ver_jornada_id'),
   	(r'^ver/$', 'gestion_sistema.gestion_jornada.views.ver_jornada'),
   	(r'^listar/$', 'gestion_sistema.gestion_jornada.views.listar_jornadas'),
   	(r'^actual/$', 'gestion_sistema.gestion_jornada.views.jornada_actual'),
)
