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

# Vistas del sistema
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.db import transaction
from django.contrib.auth import authenticate, login

from django.db.models import Q

import datetime

from gestion_base.func import devolverMensaje
from gestion_sistema.gestion_liga.models import Liga

########################################################################

@login_required
def listar_notificaciones(request):
	''' Lista todas las notificaciones de un usuario '''
	usuario = request.user

	notificaciones = usuario.notificacion_set.all()
	for n in notificaciones:
		n.mensaje = n.getMensaje()

	return render_to_response("juego/notificaciones/listar.html", {"usuario" : usuario, "notificaciones" : notificaciones })

########################################################################

@login_required
def listar_notificaciones_liga(request, liga_id):
	''' Muestra las notificaciones de una liga '''
	usuario = request.user

	if Liga.objects.filter(id = liga_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una liga con identificador %s" % liga_id)

	liga = Liga.objects.get(id = liga_id)

	notificaciones = usuario.notificacion_set.filter(liga = liga)
	for n in notificaciones:
		n.mensaje = n.getMensaje()

	return render_to_response("juego/notificaciones/listar_liga.html", {"usuario" : usuario, "notificaciones" : notificaciones })

########################################################################

@login_required
def borrar_notificacion(request, notificacion_id):
	''' Borra una notificacion '''
	# Obtenemos el usuario
	usuario = request.user

	if usuario.notificacion_set.filter(id = notificacion_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una subasta con identificador %s" % subasta_id)

	# Obtenemos la notificacion
	notificacion = usuario.notificacion_set.get(id = notificacion_id)

	# Borramos
	notificacion.delete()

	return devolverMensaje(request, "Notificacion borrada", "/cuentas/notificaciones/listar/")

########################################################################

@login_required
def ver_notificacion(request, notificacion_id):
	''' Muestra los datos de una notificacion y la marca como leida '''
	# Obtenemos el usuario
	usuario = request.user

	if usuario.notificacion_set.filter(id = notificacion_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una subasta con identificador %s" % subasta_id)

	# Obtenemos la notificacion
	notificacion = usuario.notificacion_set.get(id = notificacion_id)
	notificacion.mensaje = notificacion.getMensaje()

	# Marcamos como leida
	notificacion.leida = True
	notificacion.save()

	return render_to_response("juego/notificaciones/ver.html", { "usuario" : usuario, "notificacion" : notificacion })

########################################################################
