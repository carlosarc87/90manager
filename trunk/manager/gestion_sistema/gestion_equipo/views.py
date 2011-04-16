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

from models import Equipo
from forms import EquipoForm

from gestion_base.func import devolverMensaje, redireccionar, generarPagina

from gestion_sistema.gestion_liga.models import Liga
from gestion_sistema.gestion_jugador.models import Jugador
from gestion_sistema.gestion_jugador.func import nombreJugadorAleatorio

########################################################################

@login_required
def ver_equipo_id(request, equipo_id):
	''' Muestra los datos de un equipo '''
	# Obtenemos el usuario
	equipos = Equipo.objects.filter(id = equipo_id)

	if equipos.count() == 0:
		return devolverMensaje(request, "Error, no existe un equipo con identificador %s" % equipo_id)

	# Obtenemos el equipo
	request.session['equipo_actual'] = equipos[0]

	return redireccionar("/equipos/ver")

########################################################################

@login_required
def ver_equipo(request):
	''' Muestra los datos de un equipo '''
	# Obtenemos el usuario
	usuario = request.user

	equipo = request.session['equipo_actual']

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

	if len(jugadores) > 0:
		edad_media_equipo = (suma_edad * 1.0) / len(jugadores)
	else:
		edad_media_equipo = 0

	# Obtenemos la liga
	liga = equipo.liga

	d = {"usuario" : usuario,
				 "liga" : liga,
				 "equipo" : equipo,
				 "jugadores" : jugadores,
				 "valor_equipo" : valor_equipo,
				 "edad_media_equipo" : edad_media_equipo
				}
	return generarPagina("juego/equipos/ver_equipo.html", d, request)

########################################################################

@login_required
def crear_equipo(request):
	''' Muestra la pagina para crear un equipo '''
	usuario = request.user

	liga = request.session['liga_actual']

	if liga.activada():
		return devolverMensaje(request, "Esta liga ya no acepta mas equipos", "/ligas/ver/%d/" % liga.id)

	if liga.equipo_set.filter(usuario = usuario).count() > 0:
		return devolverMensaje(request, "Ya tienes un equipo en esta liga", "/ligas/ver/%d/" % liga.id)

	if request.method == 'POST':
		form = EquipoForm(liga, request.POST)
		if form.is_valid():
			equipo = form.save(commit = False)
			equipo.usuario = usuario
			equipo.liga = liga
			equipo.dinero = liga.dinero_inicial
			equipo.save()
			equipo.generarJugadoresAleatorios(liga.sexo_permitido, liga.num_jugadores_inicial, liga.nivel_max_jugadores_inicio)
			return devolverMensaje(request, "Se ha creado correctamente", "/equipos/ver/%d/" % equipo.id)
	else:
		form = EquipoForm(liga)

	d = {"form": form, "usuario" : usuario, "liga" : liga }
	return generarPagina("juego/equipos/crear_equipo.html", d, request, True)

########################################################################

