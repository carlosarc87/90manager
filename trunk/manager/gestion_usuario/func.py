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
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from django.contrib.sessions.models import Session
from datetime import datetime

from models import Usuario

def generarPagina(template, parametros, request, form = False):
	""" Genera una pagina web con los templates añadiendo unos parámetros por defecto """
	usuario = request.user
	parametros['usuario'] = usuario
	parametros['num_notificaciones'] = usuario.notificacion_set.filter(leida = False).count()
	return render_to_response(template, parametros, context_instance = RequestContext(request))

def redireccionar(direccion):
	""" Redirecciona a otra pagina web """
	return HttpResponseRedirect(direccion)

def getUsuariosConectados():
    # Query all non-expired sessions
    sesiones = Session.objects.filter(expire_date__gte = datetime.now())
    uid_list = []

    # Build a list of user ids from that query
    for sesion in sesiones:
        data = sesion.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return Usuario.objects.filter(id__in = uid_list)
