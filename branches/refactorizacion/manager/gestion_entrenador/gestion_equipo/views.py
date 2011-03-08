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

from gestion_entrenador.gestion_equipo.models import Equipo
from gestion_entrenador.gestion_equipo.forms import EquipoForm

########################################################################

@login_required
def ver_equipo(request, equipo_id):
	''' Muestra los datos de un equipo '''
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	if usuario == None:
		return devolverMensaje(request, "SHEEEEEEEEEE vuelve al redil.", "/admin/")

	if Equipo.objects.filter(id = equipo_id).count() == 0:
		return devolverMensaje(request, "Error, no existe un equipo con identificador %s" % equipo_id)

	# Obtenemos el equipo
	equipo = Equipo.objects.get(id = equipo_id)

	# Obtenemos los jugadores
	jugadores = equipo.jugador_set.all()
	valor_equipo = 0
	for jugador in jugadores:
		valor_equipo += jugador.valorMercado()

	# Obtenemos la liga
	liga = equipo.liga

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("equipos/ver_equipo.html")
	c = Context({"usuario" : usuario,
				 "liga" : liga,
				 "equipo" : equipo,
				 "jugadores" : jugadores,
				 "valor_equipo" : valor_equipo
				})
	return HttpResponse(t.render(c))

########################################################################

@login_required
def crear_equipo(request, liga_id):
	''' Muestra la pagina para crear un equipo '''
	usuario = obtenerUsuario(request)
	if usuario == None:
		return devolverMensaje(request, "SHEEEEEEEEEE vuelve al redil.", "/admin/")

	if Liga.objects.filter(id = liga_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una liga con identificador %s" % liga_id)

	liga = Liga.objects.get(id = liga_id)

	if liga.activada():
		return devolverMensaje(request, "Esta liga ya no acepta mas equipos", "/ligas/ver/%d/" % liga.id)

	if liga.equipo_set.filter(usuario = usuario).count() > 0:
		return devolverMensaje(request, "Ya tienes un equipo en esta liga", "/ligas/ver/%d/" % liga.id)

	if request.method == 'POST':
		form = EquipoForm(request.POST)
		if form.is_valid():
			equipo = form.save(commit = False)
			equipo.usuario = usuario
			equipo.liga = liga
			equipo.save()
			# Annadir 20 jugadores aleatorios
			for j in range(1, 20):
				# Establecer posición
				if (j == 1 or j == 20):
					posicion = "PORTERO"
				elif ((j >= 2 and j <= 5) or (j >= 12 and j <= 14)):
					posicion = "DEFENSA"
				elif ((j >= 6 and j <= 9) or (j >= 15 and j <= 17)):
					posicion = "CENTROCAMPISTA"
				else:
					posicion = "DELANTERO"

				# Establecer si es titular o suplente
				if (j <= 11):
					titular = True
					suplente = False
				else:
					titular = False
					suplente = True

				jugador = Jugador(equipo = equipo, nombre = nombreJugadorAleatorio(), titular = titular, suplente = suplente, transferible = False)
				jugador.setNumero(j)
				jugador.setPosicion(posicion)
				jugador.setHabilidadesAleatorias(posicion, 50)
				jugador.save()
				equipo.agregarJugador(jugador)
			return devolverMensaje(request, "Se ha creado correctamente", "/equipos/ver/%d/" % equipo.id)
	else:
		form = EquipoForm()

	return render_to_response("equipos/crear_equipo.html", {"form": form, "usuario" : usuario, "liga" : liga })

########################################################################

