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

from models import Jugador

from gestion_base.func import devolverMensaje
from gestion_usuario.func import obtenerUsuario

########################################################################

@login_required
def ver_jugador(request, jugador_id):
	''' Muestra los datos de un jugador '''
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	if usuario == None:
		return devolverMensaje(request, "SHEEEEEEEEEE vuelve al redil.", "/admin/")

	if Jugador.objects.filter(id = jugador_id).count() == 0:
		return devolverMensaje(request, "Error, no existe un jugador con identificador %s" % jugador_id)

	# Obtenemos el jugador
	jugador = Jugador.objects.get(id = jugador_id)

	# Obtener mejor posición
	mejor_posicion = jugador.mejorPosicion()

	# Obtener edad
	anios, dias = jugador.obtenerEdad()

	# Obtenemos el equipo
	equipo = jugador.atributos.equipo

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("juego/jugadores/ver_jugador.html")
	c = Context({"equipo" : equipo,
				 "usuario" : usuario,
				 "jugador" : jugador,
				 "mejor_posicion" : mejor_posicion,
				 "anios" : anios,
				 "dias" : dias
				})
	return HttpResponse(t.render(c))

########################################################################
