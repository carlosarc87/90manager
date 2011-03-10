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
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.db import transaction
from django.contrib.auth import authenticate, login

from django.db.models import Q

import datetime
import random

from models import Partido
from forms import PrepararEquipoLocalForm, PrepararEquipoVisitanteForm

from gestion_base.func import devolverMensaje
from gestion_usuario.func import obtenerUsuario

########################################################################

@login_required
def jugar_partido(request, partido_id):
	''' Juega un partido '''
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	if usuario == None:
		return devolverMensaje(request, "SHEEEEEEEEEE vuelve al redil.", "/admin/")

	if Partido.objects.filter(id = partido_id).count() == 0:
		return devolverMensaje(request, "Error, no existe un partido con identificador %s" % partido_id)

	partido = Partido.objects.get(id = partido_id)
	if partido.finalizado():
		return devolverMensaje(request, "Este partido ya se jugo", "/partidos/ver/%d/" % partido.id)

	jornada_actual = partido.jornada.liga.obtenerJornadaActual()
	if partido.jornada != jornada_actual:
		return devolverMensaje(request, "Este partido no se puede jugar ya que no es la jornada aun", "/partidos/ver/%d/" % partido.id)

	if partido.equipo_local.usuario != None:
		pass
#		if partido.titulares_local.count() != 11:
#			return devolverMensaje(request, "Eh, que tienes que preparar el equipo antes del partido", "/partidos/ver/%d/" % partido.id)
	else:
		partido.titulares_local = partido.equipo_local.jugador_set.all()[:11]

	if partido.equipo_visitante.usuario != None:
		pass
#		if partido.titulares_visitante.count() != 11:
#			return devolverMensaje(request, "Eh, que tienes que preparar el equipo antes del partido", "/partidos/ver/%d/" % partido.id)
	else:
		partido.titulares_visitante = partido.equipo_visitante.jugador_set.all()[:11]
	partido.jugar()
	partido.save()

	return ver_partido(request, partido_id)

########################################################################

@login_required
def ver_partido(request, partido_id):
	''' Muestra los datos de un partido '''
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	if usuario == None:
		return devolverMensaje(request, "SHEEEEEEEEEE vuelve al redil.", "/admin/")

	if Partido.objects.filter(id = partido_id).count() == 0:
		return devolverMensaje(request, "Error, no existe un partido con identificador %s" % partido_id)

	# Obtenemos el partido
	partido = Partido.objects.get(id = partido_id)
	sucesos_partido = partido.suceso_set.all()

	# Obtenemos la liga y la jornada
	jornada = partido.jornada
	liga = jornada.liga

	# Obtenemos los equipos que juegan en el partido
	equipo_local = partido.equipo_local
	equipo_visitante = partido.equipo_visitante

	titulares_local = None
	if partido.alineacion_local:
		titulares_local = partido.alineacion_local.titulares.all()

	titulares_visitante = None
	if partido.alineacion_visitante:
		titulares_visitante = partido.alineacion_visitante.titulares.all()

	# Comprobamos si el partido ha acabado
	finalizado = partido.finalizado()
	# Calculamos el resultado
	resultado = 0
	if finalizado:
		if partido.goles_local > partido.goles_visitante:
			resultado = "Ganador local"
		elif partido.goles_local < partido.goles_visitante:
			resultado = "Ganador visitante"
		else:
			resultado = "Empate"

	tiene_equipo = False
	if equipo_local.usuario == usuario:
		tiene_equipo = True
	elif equipo_visitante.usuario == usuario:
		tiene_equipo = True
	es_creador = liga.creador == usuario

	es_jugable = False
	jornada_actual = liga.obtenerJornadaActual()
	if partido.jornada == jornada_actual and not finalizado:
		es_jugable = True

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("partidos/ver_partido.html")
	c = Context({"jornada" : jornada,
				 "equipo_local" : equipo_local,
				 "equipo_visitante" : equipo_visitante,
				 "liga" : liga,
				 "partido" : partido,
				 "sucesos_partido" : sucesos_partido,
				 "usuario" : usuario,
				 "finalizado" : finalizado,
				 "resultado" : resultado,
				 "titulares_local" : titulares_local,
				 "titulares_visitante" : titulares_visitante,
				 "es_creador" : es_creador,
				 "tiene_equipo" : tiene_equipo,
				 "es_jugable" : es_jugable,
				})
	return HttpResponse(t.render(c))

########################################################################

@login_required
def preparar_partido(request, partido_id):
	''' Muestra los datos para preparar un partido '''
	partido = Partido.objects.get(id = partido_id)
	usuario = obtenerUsuario(request)
	if usuario == None:
		return devolverMensaje(request, "SHEEEEEEEEEE vuelve al redil.", "/admin/")

	if Partido.objects.filter(id = partido_id).count() == 0:
		return devolverMensaje(request, "Error, no existe un partido con identificador %s" % partido_id)

	# Comprobar que el partido no se haya jugado ya
	if partido.finalizado():
		return devolverMensaje(request, "Este partido ya acabo", "/partidos/ver/%d/" % partido.id)

	# Comprobar si el usuario juega en el partido
	if (partido.equipo_local.usuario == usuario): # Juega como local
		equipo = partido.equipo_local
		if request.method == 'POST':
			form = PrepararEquipoLocalForm(request.POST, instance = partido)
			if form.is_valid():
				form.save()
				titulares = form.cleaned_data["titulares_local"]
				suplentes = partido.equipo_local.jugador_set.all()
				for j in suplentes:
					if j in titulares:
						suplentes.remove(j)
				partido.crearAlineacion(True, titulares, suplentes)
				return devolverMensaje(request, "Se ha creado correctamente la alineacion", "/partidos/ver/%d/" % partido.id)
		else:
			form = PrepararEquipoLocalForm(instance = partido)

	elif (partido.equipo_visitante.usuario == usuario): # Juega como visitante
		equipo = partido.equipo_visitante
		if request.method == 'POST':
			form = PrepararEquipoVisitanteForm(request.POST, instance = partido)
			if form.is_valid():
				form.save()
				titulares = form.cleaned_data["titulares_visitante"]
				suplentes = partido.equipo_visitante.jugador_set.all()
				for j in suplentes:
					if j in titulares:
						suplentes.remove(j)
				partido.crearAlineacion(False, titulares, suplentes)
				return devolverMensaje(request, "Se ha creado correctamente la alineacion", "/partidos/ver/%d/" % partido.id)
		else:
			form = PrepararEquipoVisitanteForm(instance = partido)

	else: # No juega como naaaaaaaaaaaaaaa
		return devolverMensaje(request, "No tienes equipo en este partido", "/partidos/ver/%d/" % partido.id)

	return render_to_response("partidos/preparar_partido.html", {"form": form, "usuario" : usuario, "partido" : partido, "equipo" : equipo })

########################################################################
