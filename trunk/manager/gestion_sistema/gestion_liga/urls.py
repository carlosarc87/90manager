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
   	# Modulo de ligas
   	(r'^crear/$', 'gestion_sistema.gestion_liga.views.crear_liga'),
   	(r'^publicas/$', 'gestion_sistema.gestion_liga.views.ver_ligas_publicas'),
   	(r'^ver/$', 'gestion_sistema.gestion_liga.views.ver_liga'),
   	(r'^ver/(?P<liga_id>\d+)/$', 'gestion_sistema.gestion_liga.views.ver_liga_id'),
   	(r'^avanzar/$', 'gestion_sistema.gestion_liga.views.avanzar_jornada_liga'),
   	(r'^activar/$', 'gestion_sistema.gestion_liga.views.activar_liga'),
)
