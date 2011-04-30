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

from gestion_sistema.decorators import actualizarLiga, comprobarSesion

from gestion_base.func import devolverMensaje, redireccionar, generarPagina

########################################################################

@login_required
def ver_jugador_id(request, jugador_id):
	''' Muestra los datos de un jugador '''
	# Obtenemos el usuario
	usuario = request.user

	jugadores = Jugador.objects.filter(id = jugador_id)

	if jugadores.count() == 0:
		return devolverMensaje(request, "Error, no existe un jugador con identificador %s" % jugador_id, 0)

	# Obtenemos el jugador
	request.session['jugador_actual'] = jugadores[0]

	return redireccionar('/jugadores/ver/')

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['jugador_actual'])
def ver_jugador(request):
	''' Muestra los datos de un jugador '''
	# Obtenemos el usuario
	usuario = request.user

	jugador = request.session['jugador_actual']
	
	valorMercado_mejor = jugador.valorMercado()

	# Obtener valores por posición
	valorMercado_PO = jugador.valorMercado("PORTERO")
	valorMercado_DF = jugador.valorMercado("DEFENSA")
	valorMercado_CC = jugador.valorMercado("CENTROCAMPISTA")
	valorMercado_DL = jugador.valorMercado("DELANTERO")

	# Obtener rendimiento por posición
	rendimiento_PO = (int)((valorMercado_PO * 100) / valorMercado_mejor)
	rendimiento_DF = (int)((valorMercado_DF * 100) / valorMercado_mejor)
	rendimiento_CC = (int)((valorMercado_CC * 100) / valorMercado_mejor)
	rendimiento_DL = (int)((valorMercado_DL * 100) / valorMercado_mejor)

	# Obtener edad
	anios, dias = jugador.getEdad()

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
				 "anios" : anios,
				 "dias" : dias,
				 "rendimiento_PO" : rendimiento_PO,
				 "rendimiento_DF" : rendimiento_DF,
				 "rendimiento_CC" : rendimiento_CC,
				 "rendimiento_DL" : rendimiento_DL,
				 "valorMercado_PO" : valorMercado_PO,
				 "valorMercado_DF" : valorMercado_DF,
				 "valorMercado_CC" : valorMercado_CC,
				 "valorMercado_DL" : valorMercado_DL,
				}
	return generarPagina(request, "juego/jugadores/ver_jugador.html", d)

########################################################################
