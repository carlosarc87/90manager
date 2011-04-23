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

from models import Jornada

from gestion_sistema.decorators import actualizarLiga, comprobarSesion

from gestion_base.func import devolverMensaje, redireccionar, generarPagina

########################################################################

@login_required
def ver_jornada_id(request, jornada_id):
	''' Muestra los datos de una jornada '''
	jornadas = Jornada.objects.filter(id = jornada_id)

	if jornadas.count() == 0:
		return devolverMensaje(request, "Error, no existe una jornada con identificador %s" % jornada_id, 0)

	request.session['jornada_actual'] = jornadas[0]

	return redireccionar('/jornadas/ver/')

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['jornada_actual'])
def ver_jornada(request):
	''' Muestra los datos de una jornada '''
	# Obtenemos el usuario
	usuario = request.user

	# Obtenemos la jornada
	jornada = request.session['jornada_actual']

	# Obtenemos la liga
	liga = jornada.liga
	es_creador = liga.creador == usuario

	# Obtenemos los encuentros que hay
	emparejamientos = jornada.partido_set.all()
	# Obtenemos la clasificacion
	clasificacion = None
	clasificacion_anterior = None
#	if jornada.jugada:
	clasificacion_sin_ordenar = jornada.clasificacionequipojornada_set.all()
	# Funcion sorted devuelve una COPIA de la lista ordenada
	clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: dato.puntos, reverse = True)

	if jornada.numero >= 2:
		jornada_anterior = liga.jornada_set.get(numero = jornada.numero - 1)
		if jornada_anterior.jugada:
			clasificacion_anterior_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
			clasificacion_anterior = sorted(clasificacion_anterior_sin_ordenar, key = lambda dato: dato.puntos, reverse = True)

	jornada_anterior = liga.jornada_set.filter(numero = jornada.numero - 1)
	if jornada_anterior.count() > 0:
		jornada_anterior = jornada_anterior[0]
	else:
		jornada_anterior = None

	jornada_siguiente = liga.jornada_set.filter(numero = jornada.numero + 1)
	if jornada_siguiente.count() > 0:
		jornada_siguiente = jornada_siguiente[0]
	else:
		jornada_siguiente = None

	# Es la jornada actual si se jugo la anterior pero no si misma
	if jornada_anterior != None:
		es_jornada_actual = jornada_anterior.jugada == True and jornada.jugada == False
	elif jornada_anterior == None and jornada.jugada == False: # 1º jornada
		es_jornada_actual = True
	else:
		es_jornada_actual = False

	d = {"jornada" : jornada,
				 "emparejamientos" : emparejamientos,
				 "liga" : liga,
				 "usuario" : usuario,
				 "jornada_anterior" : jornada_anterior,
				 "jornada_siguiente" : jornada_siguiente,
				 "clasificacion" : clasificacion,
				 "clasificacion_anterior" : clasificacion_anterior,
				 "es_creador" : es_creador,
				 "es_jornada_actual" : es_jornada_actual,
				}
	return generarPagina("juego/jornadas/ver_jornada.html", d, request)

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['liga_actual'])
def listar_jornadas(request):
	""" Muestra las jornadas de la liga """
	# Obtenemos la liga
	liga = request.session['liga_actual']
	jornadas = liga.getJornadas()

	d = { "jornadas" : jornadas }
	return generarPagina("juego/jornadas/listar_liga.html", d, request)

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['liga_actual'])
def jornada_actual(request):
	""" Redirige a la jornada actual de la liga """
	# Obtenemos la liga
	liga = request.session['liga_actual']

	jornada = liga.getJornadaActual()
	if jornada is None:
		return devolverMensaje(request, "Error, la liga ya acabó", 0)

	return redireccionar('/jornadas/ver/%s/' % (jornada.id))

########################################################################
