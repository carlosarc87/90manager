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
from gestion_base import views as views_base
from gestion_usuario import views as views_usuario

urlpatterns = [
	url(r'^$', views_usuario.principal),
	url(r'^tablon/$', views_usuario.tablon),
	url(r'^creditos/', views_base.creditos),
	url(r'^contacto/', views_base.contacto),
	url(r'^siguenos/', views_base.siguenos),
	url(r'^changelog/', views_base.changelog),
	url(r'^condiciones/', views_base.condiciones),
]
