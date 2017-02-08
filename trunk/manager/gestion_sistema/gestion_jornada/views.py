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

from .models import Jornada

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
@comprobarSesion(['jornada_actual'])
@actualizarLiga
def ver_jornada(request):
	''' Muestra los datos de una jornada '''
	# Obtenemos el usuario
	usuario = request.user

	# Obtenemos la jornada
	jornada_actual = request.session['jornada_actual']

	# Obtenemos la liga
	liga = jornada_actual.liga
	es_creador = liga.creador == usuario
	
	if jornada_actual.numero > 1:
		jornada_anterior = liga.jornada_set.get(numero = jornada_actual.numero - 1)
	else:
		jornada_anterior = None
	
	# Si la liga ha acabado
	if not liga.getJornadaActual():
		liga_acabada = True
	else:
		liga_acabada = False

	# Obtenemos los encuentros que hay
	emparejamientos = jornada_actual.partido_set.all()
	
	# Obtenemos la clasificacion
	clasificacion = None
	clasificacion_anterior = None
	
	clasificacion_sin_ordenar = jornada_actual.clasificacionequipojornada_set.all()
	clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: (-dato.puntos, -(dato.goles_favor-dato.goles_contra), -dato.goles_favor))
	
	diccionario_equipos_clasificacion = dict()
	
	posicion = 1
	for c in clasificacion:
		diccionario_equipos_clasificacion[c.equipo] = c
		diccionario_equipos_clasificacion[c.equipo].posicion = posicion
		
		c.goles_diferencia = c.goles_favor - c.goles_contra

		if jornada_anterior != None:
			incluida = True
			
			if not liga_acabada:
				jornada_a_comprobar = jornada_actual
			else:
				jornada_a_comprobar = jornada_anterior
				incluida = True
				
			c.partidos_ganados = len(c.equipo.getPartidosGanados(jornada_a_comprobar, incluida))
			c.partidos_empatados = len(c.equipo.getPartidosEmpatados(jornada_a_comprobar, incluida))
			c.partidos_perdidos = len(c.equipo.getPartidosPerdidos(jornada_a_comprobar, incluida))

		else:
			c.partidos_ganados = len(c.equipo.getPartidosGanados(jornada_actual, True))
			c.partidos_empatados = len(c.equipo.getPartidosEmpatados(jornada_actual, True))
			c.partidos_perdidos = len(c.equipo.getPartidosPerdidos(jornada_actual, True))

		c.partidos_jugados = c.partidos_ganados + c.partidos_empatados + c.partidos_perdidos
		
		posicion += 1

	if jornada_anterior != None and jornada_anterior.jugada:
		clasificacion_anterior_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
		clasificacion_anterior = sorted(clasificacion_anterior_sin_ordenar, key = lambda dato: (-dato.puntos, -(dato.goles_favor-dato.goles_contra), -dato.goles_favor))
		
		posicion = 1
		for c in clasificacion_anterior:
			diccionario_equipos_clasificacion[c.equipo].diferencia_posicion_jornada_anterior = posicion - diccionario_equipos_clasificacion[c.equipo].posicion
			posicion += 1

	# Obtener jornada siguiente
	jornada_siguiente = liga.jornada_set.get(numero = jornada_actual.numero + 1)

	# Obtener si es la jornada actual
	# Es la jornada actual si se no se ha jugado y se jugó la anterior
	if jornada_anterior != None:
		es_jornada_actual = (jornada_anterior.jugada == True and jornada_actual.jugada == False)
	elif jornada_anterior == None and jornada_actual.jugada == False: # 1º jornada
		es_jornada_actual = True
	else:
		es_jornada_actual = False

	d = {"jornada_actual" : jornada_actual,
		 "emparejamientos" : emparejamientos,
		 "liga" : liga,
		 "usuario" : usuario,
		 "jornada_anterior" : jornada_anterior,
		 "jornada_siguiente" : jornada_siguiente,
		 "clasificacion" : clasificacion,
		 "es_creador" : es_creador,
		 "es_jornada_actual" : es_jornada_actual,
		 "diccionario_equipos_clasificacion" : diccionario_equipos_clasificacion
		}
	return generarPagina(request, "juego/jornadas/ver_jornada.html", d)

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['liga_actual'])
def ver_jornada_actual(request):
	""" Redirige a la jornada actual de la liga """
	# Obtenemos la liga
	liga = request.session['liga_actual']

	jornada = liga.getJornadaActual()
	if jornada is None:
		return devolverMensaje(request, "Error, la liga ya ha finalizado", 0)

	return redireccionar('/jornadas/ver/%s/' % (jornada.id))

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['liga_actual'])
def listar_jornadas(request):
	""" Muestra las jornadas de la liga """
	# Obtenemos la liga
	liga = request.session['liga_actual']
	jornadas = liga.getJornadas()
	
	for jornada in jornadas:
		jornada.partidos_jornada = jornada.partido_set.all()

	d = {
		"liga" : liga,
		"jornadas" : jornadas
	}
	
	return generarPagina(request, "juego/jornadas/listar_liga.html", d)

########################################################################
