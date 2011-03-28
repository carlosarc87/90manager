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
import random

from gestion_sistema.gestion_equipo.models import Equipo
from gestion_sistema.gestion_equipo.forms import EquipoForm

from models import Liga
from forms import LigaForm, ActivarLigaForm

from gestion_base.func import devolverMensaje
from gestion_usuario.models import Usuario

########################################################################

@login_required
def ver_ligas_publicas(request):
	''' Muestra las ligas publicas que haya en el sistema '''
	usuario = request.user
	# Obtenemos las ligas
	ligas = Liga.objects.filter(publica = True)

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("juego/ligas/ver_ligas_publicas.html")
	c = Context({"usuario" : usuario,
				 "ligas" : ligas
				})
	return HttpResponse(t.render(c))

########################################################################

@login_required
def ver_liga(request, liga_id):
	''' Muestra los datos de una liga determinada '''
	# Obtenemos el usuario
	usuario = request.user

	if Liga.objects.filter(id = liga_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una liga con identificador %s" % liga_id)

	# Obtenemos la liga
	liga = Liga.objects.get(id = liga_id)

	# Obtenemos los equipos que juegan en la liga
	equipos = liga.equipo_set.all()

	# Obtenemos las jornadas
	jornadas = liga.jornada_set.all()

	# Obtenemos las jornadas no jugadas
	jornadas_restantes = liga.jornada_set.filter(jugada = False)

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

	if activada:
		# Comprobamos si la liga ha acabado
		jornada_actual = liga.obtenerJornadaActual()
		jornada_anterior = None

		# Si la liga ha acabado
		if not jornada_actual:
			liga_acabada = True
		else:
			if jornada_actual.numero >= 2:
				jornada_anterior = liga.jornada_set.get(numero = jornada_actual.numero)
				clasificacion_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
				clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: dato.puntos, reverse = True)
			elif jornada_actual.numero == 1: # Generar clasificacion vacía
				clasificacion_sin_ordenar = jornada_actual.clasificacionequipojornada_set.all()
				clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: dato.puntos, reverse = True)

		if liga_acabada:
			jornada_anterior = liga.jornada_set.all()[len(liga.jornada_set.all()) - 1]
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
					if not liga_acabada:
						jornada_a_comprobar = jornada_actual
					else:
						jornada_a_comprobar = jornada_anterior
					c.partidos_ganados = len(c.equipo.getPartidosGanados(jornada_a_comprobar))
					c.partidos_empatados = len(c.equipo.getPartidosEmpatados(jornada_a_comprobar))
					c.partidos_perdidos = len(c.equipo.getPartidosPerdidos(jornada_a_comprobar))
				else:
					# Comor getPartidos es sin la jornada destino, pues decimos que compruebe hasta la 2
					jornada_a_comprobar = liga.jornada_set.get(numero = 2)
					c.partidos_ganados = len(c.equipo.getPartidosGanados(jornada_a_comprobar))
					c.partidos_empatados = len(c.equipo.getPartidosEmpatados(jornada_a_comprobar))
					c.partidos_perdidos = len(c.equipo.getPartidosPerdidos(jornada_a_comprobar))

				c.partidos_jugados = c.partidos_ganados + c.partidos_empatados + c.partidos_perdidos

				posicion += 1

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("juego/ligas/ver_liga.html")
	c = Context({"liga" : liga,
				 "equipos" : equipos,
				 "jornadas" : jornadas,
				 "usuario" : usuario,
				 "jornada_actual" : jornada_actual,
				 "jornadas_restantes" : jornadas_restantes,
				 "activada" : activada,
				 "equipo_propio" : equipo_propio,
				 "clasificacion" : clasificacion,
				 "liga_acabada" : liga_acabada,
				 "es_creador" : es_creador
				})
	return HttpResponse(t.render(c))

########################################################################

@login_required
def avanzar_jornada_liga(request, liga_id):
	''' Avanza una liga de jornada actual '''
	# Obtenemos el usuario
	usuario = request.user

	if Liga.objects.filter(id = liga_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una liga con identificador %s" % liga_id)

	# Obtenemos la liga
	liga = Liga.objects.get(id = liga_id)

	if liga.creador != usuario:
		return devolverMensaje(request, "No eres el creador de esta liga")

	# Obtenemos las jornadas no jugadas
	jornadas = liga.jornada_set.filter(jugada = False)

	if jornadas.count() == 0:
		return devolverMensaje(request, "Esta liga ya esta acabada", "/ligas/ver/%d/" % liga.id)

	liga.avanzarJornada()

	return HttpResponseRedirect("/ligas/ver/%s/" % (liga_id))

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

	c = RequestContext(request, {"form" : form, "usuario" : usuario })

	return render_to_response("juego/ligas/crear_liga.html", c)

########################################################################

@login_required
@transaction.commit_on_success
def activar_liga(request, liga_id):
	''' Formulario para activar una liga '''
	usuario = request.user

	if Liga.objects.filter(id = liga_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una liga con identificador %s" % liga_id)

	# Obtenemos la liga
	liga = Liga.objects.get(id = liga_id)

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
			jornada = liga.obtenerJornadaActual()
			jornada.generarClasificacion()

			return devolverMensaje(request, "Se ha generado la liga correctamente", "/ligas/ver/%d/" % liga.id)
	else:
		form = ActivarLigaForm(instance = liga)

	c = RequestContext(request, {"form" : form, "usuario" : usuario, "liga" : liga })

	return render_to_response("juego/ligas/activar_liga.html", c)


########################################################################
