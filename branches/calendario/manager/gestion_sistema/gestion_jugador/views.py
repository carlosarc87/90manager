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
from django.contrib.auth.decorators import login_required

from models import Jugador

from gestion_base.func import devolverMensaje, redireccionar, generarPagina

########################################################################

@login_required
def ver_jugador_id(request, jugador_id):
	''' Muestra los datos de un jugador '''
	# Obtenemos el usuario
	usuario = request.user

	jugadores = Jugador.objects.filter(id = jugador_id)

	if jugadores.count() == 0:
		return devolverMensaje(request, "Error, no existe un jugador con identificador %s" % jugador_id)

	# Obtenemos el jugador
	request.session['jugador_actual'] = jugadores[0]

	return redireccionar('/jugadores/ver/')

########################################################################

@login_required
def ver_jugador(request):
	''' Muestra los datos de un jugador '''
	# Obtenemos el usuario
	usuario = request.user

	jugador = request.session['jugador_actual']

	# Obtener mejor posición
	mejor_posicion = jugador.mejorPosicion()

	# Obtener edad
	anios, dias = jugador.obtenerEdad()

	# Obtenemos el equipo
	equipo = jugador.atributos.equipo

	# Obtenemos si está en subasta
	subasta = None
	if jugador.atributos.ofertado:
		subasta = jugador.atributos.subasta

	d = {"equipo" : equipo,
				 "usuario" : usuario,
				 "jugador" : jugador,
				 "subasta" : subasta,
				 "mejor_posicion" : mejor_posicion,
				 "anios" : anios,
				 "dias" : dias
				}
	return generarPagina("juego/jugadores/ver_jugador.html", d, request)

########################################################################
