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

import datetime
import random

from models import Equipo
from forms import EquipoForm

from gestion_base.func import devolverMensaje
from gestion_usuario.func import obtenerUsuario
from gestion_sistema.gestion_liga.models import Liga
from gestion_sistema.gestion_jugador.models import Jugador
from gestion_sistema.gestion_jugador.func import nombreJugadorAleatorio

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
	jugadores = equipo.getJugadores()

	# Obtener datos de los jugadores
	suma_edad = 0
	valor_equipo = 0
	for jugador in jugadores:
		# Valor total del equipo
		valor_equipo += jugador.valorMercado()

		# Edad del equipo
		anios, dias = jugador.obtenerEdad()
		suma_edad = suma_edad + anios

	edad_media_equipo = (suma_edad * 1.0) / len(jugadores)

	# Obtenemos la liga
	liga = equipo.liga

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("juego/equipos/ver_equipo.html")
	c = Context({"usuario" : usuario,
				 "liga" : liga,
				 "equipo" : equipo,
				 "jugadores" : jugadores,
				 "valor_equipo" : valor_equipo,
				 "edad_media_equipo" : edad_media_equipo
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
			equipo.generarJugadoresAleatorios(liga.sexo_permitido, liga.num_jugadores_inicial, liga.nivel_max_jugadores_inicio)
			return devolverMensaje(request, "Se ha creado correctamente", "/equipos/ver/%d/" % equipo.id)
	else:
		form = EquipoForm()

	return render_to_response("juego/equipos/crear_equipo.html", {"form": form, "usuario" : usuario, "liga" : liga })

########################################################################

