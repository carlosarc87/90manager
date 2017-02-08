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

# Vistas del sistema
from django.contrib.auth.decorators import login_required

from gestion_sistema.decorators import actualizarLiga

from gestion_base.func import devolverMensaje, redireccionar, generarPagina

from gestion_sistema.gestion_liga.models import Liga

########################################################################

@login_required
def listar_notificaciones(request):
	''' Lista todas las notificaciones de un usuario '''
	usuario = request.user

	notificaciones = usuario.notificacion_set.all()

	return generarPagina(request, "juego/notificaciones/listar.html", { "notificaciones" : notificaciones })

########################################################################

@login_required
def listar_notificaciones_tablon(request):
	''' Lista todas las notificaciones sin liga de un usuario '''
	usuario = request.user

	notificaciones = usuario.notificacion_set.filter(liga = None)

	return generarPagina(request, "juego/notificaciones/listar.html", { "notificaciones" : notificaciones })

########################################################################

@login_required
@actualizarLiga
def listar_notificaciones_liga(request):
	''' Muestra las notificaciones de una liga '''
	usuario = request.user

	liga = request.session['liga_actual']

	notificaciones = usuario.notificacion_set.filter(liga = liga)

	return generarPagina(request, "juego/notificaciones/listar_liga.html", { "notificaciones" : notificaciones })

########################################################################

@login_required
def borrar_notificacion(request, notificacion_id):
	''' Borra una notificacion '''
	# Obtenemos el usuario
	usuario = request.user

	if usuario.notificacion_set.filter(id = notificacion_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una notificación con identificador %s" % subasta_id)

	# Obtenemos la notificacion
	notificacion = usuario.notificacion_set.get(id = notificacion_id)

	# Borramos
	notificacion.delete()

	return devolverMensaje(request, "La notificación ha sido eliminada", "/cuentas/notificaciones/listar_liga/")

########################################################################

@login_required
def ver_notificacion(request, notificacion_id):
	''' Marca una notificación como leída y redirecciona a su contenido '''
	# Obtenemos el usuario
	usuario = request.user

	if usuario.notificacion_set.filter(id = notificacion_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una subasta con identificador %s" % subasta_id)

	# Obtenemos la notificacion
	notificacion = usuario.notificacion_set.get(id = notificacion_id)
	direccion = notificacion.getURL()

	if not notificacion.leida:
		# Marcamos como leida
		notificacion.leida = True
		notificacion.save()

	return redireccionar(direccion)

########################################################################
