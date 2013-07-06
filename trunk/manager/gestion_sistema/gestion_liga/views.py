# -*- coding: utf-8 -*-
"""
Copyright 2013 by
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

from datetime import datetime

from gestion_sistema.decorators import actualizarLiga, comprobarSesion

from gestion_sistema.gestion_equipo.models import Equipo
from gestion_sistema.gestion_equipo.forms import EquipoForm

from models import Liga
from forms import LigaForm, ActivarLigaForm, CambiarFechaForm

from gestion_base.func import devolverMensaje, redireccionar, generarPagina, renderizar

from gestion_usuario.models import Usuario
from gestion_usuario.gestion_notificacion.func import notificar, Notificacion

########################################################################

@login_required
def ver_ligas_publicas(request):
	''' Muestra las ligas publicas que haya en el sistema '''
	# Obtenemos las ligas
	ligas = Liga.objects.filter(publica = True, jornada = None)

	for liga in ligas:
		liga.inscritos = liga.equipo_set.all().count()

	d = { "ligas" : ligas }
	return renderizar(request, "juego/ligas/ver_ligas_publicas.html", d)

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['liga_actual'])
def ver_liga(request):
	''' Muestra los datos de una liga determinada '''
	# Obtenemos el usuario
	usuario = request.user

	liga = request.session['liga_actual']

	# Obtenemos los equipos que juegan en la liga
	equipos = liga.equipo_set.all()
	equipos = sorted(equipos, key = lambda dato: dato.siglas)

	# Obtenemos las jornadas
	jornadas = liga.getJornadas()

	# Obtenemos las jornadas no jugadas
	jornadas_restantes = jornadas.filter(jugada = False)

	activada = liga.activada()
	jornada_actual = None

	clasificacion = None

	liga_acabada = False

	es_creador = liga.creador == usuario

	form_fecha = None

	if es_creador:
		if request.method == 'POST':
			form_fecha = CambiarFechaForm(request.POST)
			if form_fecha.is_valid():
				fecha_nueva = form_fecha.cleaned_data['fecha_nueva']
				liga.setFecha(fecha_nueva)
				return redireccionar('/ligas/ver/%d/' % liga.id)
		else:
			form_fecha = CambiarFechaForm()

	# Comprobamos si el jugador tiene un equipo en esta liga
	equipo_propio = liga.equipo_set.filter(usuario = usuario)
	if len(equipo_propio) > 0:
		equipo_propio = equipo_propio[0]
	else:
		equipo_propio = None

	request.session['equipo_propio'] = equipo_propio
	
	# Para la colocación de los equipos horizontalmente
	num_equipos = equipos.count
	max_equipos_fila = 20
		
	n = 0
	for equipo in equipos:
		if (n % max_equipos_fila == 0) and (n != num_equipos):
			equipo.terminar_fila = True
		else:
			equipo.terminar_fila = False
		n += 1

	# Si la liga está activada
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
				clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: (-dato.puntos, -(dato.goles_favor-dato.goles_contra), -dato.goles_favor))
			elif jornada_actual.numero == 1: # Generar clasificacion vacía
				clasificacion_sin_ordenar = jornada_actual.clasificacionequipojornada_set.all()

		if liga_acabada:
			jornada_anterior = liga.getJornadas()[liga.getNumJornadas() - 1]
			clasificacion_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
			clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: (-dato.puntos, -(dato.goles_favor-dato.goles_contra), -dato.goles_favor))

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
		 "es_creador" : es_creador,
		 "form_fecha" : form_fecha,
		}
	return generarPagina(request, "juego/ligas/ver_liga.html", d)

########################################################################

@login_required
def ver_liga_id(request, liga_id):
	if Liga.objects.filter(id = liga_id).count() == 0:
		return devolverMensaje(request, "Error, no existe una liga con identificador %s" % liga_id, 0)

	# Obtenemos la liga
	liga = Liga.objects.get(id = liga_id)
	request.session['liga_actual'] = liga
	return redireccionar("/ligas/ver/")

########################################################################

@login_required
@comprobarSesion(['liga_actual'])
def avanzar_jornada_liga(request):
	''' Avanza una liga de jornada actual '''
	return devolverMensaje(request, "Desactualizado, pendiente de eliminar", 0)
	# Obtenemos el usuario
	usuario = request.user

	# Obtenemos la liga
	liga = request.session['liga_actual']

	if liga.creador != usuario:
		return devolverMensaje(request, "No eres el creador de esta liga", 0)

	# Obtenemos las jornadas no jugadas
	jornadas = liga.getJornadas().filter(jugada = False)

	if jornadas.count() == 0:
		return devolverMensaje(request, "Esta liga ya esta acabada", 0, "/ligas/ver/%d/" % liga.id)

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
			liga.factor_tiempo = 24 / liga.factor_tiempo
			liga.save()
			return devolverMensaje(request, "Se ha creado correctamente", 1, "/ligas/ver/%d/" % liga.id)
	else:
		form = LigaForm()

	d = { "form" : form }
	return generarPagina(request, "juego/ligas/crear_liga.html", d, False)

########################################################################

@login_required
@transaction.commit_on_success
@comprobarSesion(['liga_actual'])
def activar_liga(request):
	''' Formulario para activar una liga '''
	usuario = request.user

	# Obtenemos la liga
	liga = request.session['liga_actual']

	if liga.creador != usuario:
		return devolverMensaje(request, "Error, solo el creador de la liga puede activarla", 0)

	if liga.activada():
		return devolverMensaje(request, "Ya esta activada esta liga", 0, "/ligas/ver/%d/" % liga.id)

	equipos = liga.equipo_set.all()

	if request.method == 'POST':
		liga.fecha_real_inicio = datetime.now()
		liga.save()
		liga.rellenarLiga()
		liga.generarJornadas()

		# Generar primera clasificacion de la liga
		jornada = liga.getJornadaActual()
		jornada.generarClasificacion()

		for equipo in liga.equipo_set.exclude(usuario = None):
			notificar(equipo.usuario, tipo = Notificacion.LIGA_ACTIVADA, identificador = liga.id)

		liga.save()

		return devolverMensaje(request, "Se ha generado la liga correctamente", 1, "/ligas/ver/%d/" % liga.id)

	d = { "liga" : liga, "equipos" : equipos }
	return generarPagina(request, "juego/ligas/activar_liga.html", d)

########################################################################
