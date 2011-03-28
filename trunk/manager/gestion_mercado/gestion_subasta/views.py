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

from models import Subasta
from forms import SubastaForm
from gestion_sistema.gestion_jugador.models import Jugador
from gestion_sistema.gestion_liga.models import Liga
from gestion_sistema.gestion_equipo.models import Equipo

from gestion_base.func import devolverMensaje

########################################################################

@login_required
def crear_subasta(request, jugador_id):
	''' Crea una subasta de un jugador '''
	usuario = request.user

	if Jugador.objects.filter(id = jugador_id).count() == 0:
		return devolverMensaje(request, "Error, no existe un jugador con identificador %s" % jugador_id)

	jugador = Jugador.objects.get(id = jugador_id)

	if jugador.atributos.ofertado:
		return devolverMensaje(request, "Este jugador ya está en subasta", "/jugadores/ver/%d/" % jugador.id)

	if jugador.atributos.equipo.usuario != usuario:
		return devolverMensaje(request, "No eres propietario del equipo del jugador")

	if request.method == 'POST':
		form = SubastaForm(request.POST)
		if form.is_valid():
			subasta = form.save(commit = False)
			subasta.liga = jugador.atributos.equipo.liga
			subasta.estado = 0
			subasta.vendedor = jugador.atributos.equipo
			subasta.comprador = None
			subasta.atributos_jugador = jugador.atributos

			jugador.ofertado = True
			subasta.save()
			return devolverMensaje(request, "Se ha creado correctamente", "/mercado/subastas/ver/%d/" % subasta.id)
	else:
		form = SubastaForm()

	c = RequestContext(request, {"form": form, "usuario" : usuario, "jugador" : jugador })

	return render_to_response("juego/subastas/crear_subasta.html", c)

########################################################################

@login_required
def ver_subastas_liga(request, liga_id):
	''' Muestra las subastas de una liga '''
	usuario = request.user

	if Liga.objects.filter(id = liga_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una liga con identificador %s" % liga_id)

	liga = Liga.objects.get(id = liga_id)

	subastas = liga.subasta_set.all()

	return render_to_response("juego/subastas/ver_subastas_liga.html", {"usuario" : usuario, "subastas" : subastas, "liga" : liga })

########################################################################

@login_required
def ver_subasta(request, subasta_id):
	''' Muestra los datos de una subasta '''
	# Obtenemos el usuario
	usuario = request.user

	if Subasta.objects.filter(id = subasta_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una subasta con identificador %s" % subasta_id)

	# Obtenemos la subasta
	subasta = Subasta.objects.get(id = subasta_id)

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("juego/subastas/ver_subasta.html")
	c = Context({"usuario" : usuario,
				 "subasta" : subasta,
				})
	return HttpResponse(t.render(c))

########################################################################

@login_required
def ver_subastas_equipo(request, equipo_id):
	''' Muestra las subastas de un equipo '''
	usuario = request.user

	if Equipo.objects.filter(id = equipo_id).count() == 0:
		return devolverMensaje(request, "Error, no existe un equipo con identificador %s" % equipo_id)

	equipo = Equipo.objects.get(id = equipo_id)

#	jugadores_en_subasta

#	subastas = equipo.subasta_set.all()
	subastas = equipo.subastas_como_vendedor.all()

	return render_to_response("juego/subastas/ver_subastas_equipo.html", {"usuario" : usuario, "subastas" : subastas, "equipo" : equipo })

########################################################################

