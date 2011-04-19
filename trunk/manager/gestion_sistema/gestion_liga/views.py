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
from django.db import transaction

from gestion_sistema.gestion_equipo.models import Equipo
from gestion_sistema.gestion_equipo.forms import EquipoForm

from models import Liga
from forms import LigaForm, ActivarLigaForm

from gestion_base.func import devolverMensaje, redireccionar, generarPagina

from gestion_usuario.models import Usuario
from gestion_usuario.gestion_notificacion.func import notificar, TipoNotificacion

########################################################################

@login_required
def ver_ligas_publicas(request):
	''' Muestra las ligas publicas que haya en el sistema '''
	# Obtenemos las ligas
	ligas = Liga.objects.filter(publica = True, jornada = None)

	for liga in ligas:
		liga.inscritos = liga.equipo_set.all().count()

	d = { "ligas" : ligas }
	return generarPagina("juego/ligas/ver_ligas_publicas.html", d, request)

########################################################################

@login_required
def ver_liga(request):
	''' Muestra los datos de una liga determinada '''
	# Obtenemos el usuario
	usuario = request.user

	liga = request.session['liga_actual']

	# Obtenemos los equipos que juegan en la liga
	equipos = liga.equipo_set.all()

	# Obtenemos las jornadas
	jornadas = liga.getJornadas()

	# Obtenemos las jornadas no jugadas
	jornadas_restantes = liga.getJornadas().filter(jugada = False)

	activada = liga.activada()
	jornada_actual = None

	clasificacion = None

	liga_acabada = False

	es_creador = liga.creador == usuario

	# Comprobamos si el jugador tiene un equipo en esta liga
	equipo_propio = liga.equipo_set.filter(usuario = usuario)
	if len(equipo_propio) > 0:
		equipo_propio = equipo_propio[0]
	else:
		equipo_propio = None

	request.session['equipo_propio'] = equipo_propio

	if activada:
		# Comprobamos si la liga ha acabado
		jornada_actual = liga.getJornadaActual()
		jornada_anterior = None

		# Si la liga ha acabado
		if not jornada_actual:
			liga_acabada = True
		else:
			if jornada_actual.numero >= 2:
				jornada_anterior = liga.getJornadas().get(numero = jornada_actual.numero)
				clasificacion_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
				clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: dato.puntos, reverse = True)
			elif jornada_actual.numero == 1: # Generar clasificacion vacía
				clasificacion_sin_ordenar = jornada_actual.clasificacionequipojornada_set.all()
				clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: dato.puntos, reverse = True)

		if liga_acabada:
			jornada_anterior = liga.getJornadas()[liga.getNumJornadas() - 1]
			clasificacion_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
			clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: dato.puntos, reverse = True)

		if clasificacion is not None:
			# Calcular variables extra para la clasificación
			posicion = 1

			ultima_posicion_ascenso = 1
			primera_posicion_descenso = len(clasificacion)

			for c in clasificacion:
				c.posicion = posicion

				# Comprobar si es posición de ascenso
				if c.posicion <= ultima_posicion_ascenso:
					c.posicion_ascenso = True
				else:
					c.posicion_ascenso = False

				# Comprobar si es posición de descenso
				if c.posicion >= primera_posicion_descenso:
					c.posicion_descenso = True
				else:
					c.posicion_descenso = False

				c.goles_diferencia = c.goles_favor - c.goles_contra

				if jornada_anterior is not None:
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

	# Cargamos la plantilla con los parametros y la devolvemos
	d = {"liga" : liga,
				 "equipos" : equipos,
				 "jornadas" : jornadas,
				 "jornada_actual" : jornada_actual,
				 "jornadas_restantes" : jornadas_restantes,
				 "activada" : activada,
				 "equipo_propio" : equipo_propio,
				 "clasificacion" : clasificacion,
				 "liga_acabada" : liga_acabada,
				 "es_creador" : es_creador
				}
	return generarPagina("juego/ligas/ver_liga.html", d, request)

########################################################################

@login_required
def ver_liga_id(request, liga_id):
	if Liga.objects.filter(id = liga_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una liga con identificador %s" % liga_id)

	# Obtenemos la liga
	liga = Liga.objects.get(id = liga_id)
	request.session['liga_actual'] = liga
	return redireccionar("/ligas/ver/")

########################################################################

@login_required
def avanzar_jornada_liga(request):
	''' Avanza una liga de jornada actual '''
	# Obtenemos el usuario
	usuario = request.user

	# Obtenemos la liga
	liga = request.session['liga_actual']

	if liga.creador != usuario:
		return devolverMensaje(request, "No eres el creador de esta liga")

	# Obtenemos las jornadas no jugadas
	jornadas = liga.getJornadas().filter(jugada = False)

	if jornadas.count() == 0:
		return devolverMensaje(request, "Esta liga ya esta acabada", "/ligas/ver/%d/" % liga.id)

	liga.avanzarJornada()

	return redireccionar("/ligas/ver/%s/" % (liga.id))

########################################################################

@login_required
def crear_liga(request):
	''' Muestra y gestiona el formulario para crear una liga '''
	usuario = request.user

	if request.method == 'POST':
		form = LigaForm(request.POST)
		if form.is_valid():
			liga = form.save(commit = False)
			liga.creador = Usuario.objects.get(id = request.user.id)
			liga.save()

			return devolverMensaje(request, "Se ha creado correctamente", "/ligas/ver/%d/" % liga.id)
	else:
		form = LigaForm()

	d = {"form" : form }
	return generarPagina("juego/ligas/crear_liga.html", d, request, True, False)

########################################################################

@login_required
@transaction.commit_on_success
def activar_liga(request):
	''' Formulario para activar una liga '''
	usuario = request.user

	# Obtenemos la liga
	liga = request.session['liga_actual']

	if liga.creador != usuario:
		return devolverMensaje(request, "Error, solo el creador de la liga puede activarla")

	if liga.activada():
		return devolverMensaje(request, "Ya esta activada esta liga", "/ligas/ver/%d/" % liga.id)

	if request.method == 'POST':
		form = ActivarLigaForm(request.POST, instance=liga)
		if form.is_valid():
			liga = form.save(commit = False)
			#equipos_descartados = form.cleaned_data['equipos']
			#for equipo in equipos_descartados:
			#	Equipo.delete(Equipo.objects.get(id = equipo)) # A lo bruten xD
			liga.save()
			liga.rellenarLiga()
			liga.generarJornadas()

			# Generar primera clasificacion de la liga
			jornada = liga.getJornadaActual()
			jornada.generarClasificacion()

			for equipo in liga.equipo_set.exclude(usuario = None):
				notificar(equipo.usuario, tipo = TipoNotificacion.LIGA_ACTIVADA, identificador = liga.id, liga = liga)

			liga.save()

			return devolverMensaje(request, "Se ha generado la liga correctamente", "/ligas/ver/%d/" % liga.id)
	else:
		form = ActivarLigaForm(instance = liga)

	d = {"form" : form, "liga" : liga }
	return generarPagina("juego/ligas/activar_liga.html", d, request, True)

########################################################################
