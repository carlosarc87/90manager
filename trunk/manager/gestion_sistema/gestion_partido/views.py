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
from django.db.models import Q

from gestion_sistema.decorators import actualizarLiga, comprobarSesion

from models import Partido, JugadorPartido, Suceso
from forms import PrepararEquipoForm

from gestion_base.func import devolverMensaje, redireccionar, generarPagina

########################################################################

@login_required
@comprobarSesion(['partido_actual'])
def jugar_partido(request):
	''' Juega un partido '''
	return devolverMensaje(request, "Desactualizado, pendiente de actualizacion", 0)
	# Obtenemos el usuario
	usuario = request.user

	partido = request.session['partido_actual']

	if partido.finalizado():
		return devolverMensaje(request, "Este partido ya se jugo", 0, "/partidos/ver/%d/" % partido.id)

	jornada_actual = partido.jornada.liga.getJornadaActual()
	if partido.jornada != jornada_actual:
		return devolverMensaje(request, "Este partido no se puede jugar ya que no es la jornada aun", "/partidos/ver/%d/" % partido.id)

	if partido.equipo_local.usuario != None:
		pass
#		if partido.titulares_local.count() != 11:
#			return devolverMensaje(request, "Eh, que tienes que preparar el equipo antes del partido", "/partidos/ver/%d/" % partido.id)
	else:
		partido.titulares_local = partido.equipo_local.getJugadores()[:11]

	if partido.equipo_visitante.usuario != None:
		pass
#		if partido.titulares_visitante.count() != 11:
#			return devolverMensaje(request, "Eh, que tienes que preparar el equipo antes del partido", "/partidos/ver/%d/" % partido.id)
	else:
		partido.titulares_visitante = partido.equipo_visitante.getJugadores()[:11]
	partido.jugar()
	partido.save()

	# Comprobamos si se acabó la jornada
	if not jornada_actual.quedanPartidosPorJugar():
		jornada_actual.liga.avanzarJornada()

	return redireccionar("/partidos/ver/%s/" % (partido.id))

########################################################################

@login_required
def ver_partido_id(request, partido_id):
	''' Muestra los datos de un partido '''
	# Obtenemos el usuario
	usuario = request.user

	partidos = Partido.objects.filter(id = partido_id)

	if partidos.count() == 0:
		return devolverMensaje(request, "Error, no existe un partido con identificador %s" % partido_id)

	request.session['partido_actual'] = partidos[0]

	return redireccionar('/partidos/ver/')

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['partido_actual'])
def ver_partido(request):
	''' Muestra los datos de un partido '''
	# Obtenemos el usuario
	usuario = request.user

	partido = request.session['partido_actual']

	# Obtener sucesos del partido
	partido.sucesos = partido.suceso_set.all()

	# Obtenemos la liga y la jornada
	jornada = partido.jornada
	liga = partido.liga

	# Obtenemos los equipos que juegan en el partido
	equipo_local = partido.equipo_local
	equipo_visitante = partido.equipo_visitante

	# Comprobar si tiene equipo en el partido y se puede editar la alineación
	editar = False
	tiene_equipo = False
	if equipo_local.usuario == usuario:
		tiene_equipo = True
		if partido.alineacion_local.estaPreparada():
			editar = True
	elif equipo_visitante.usuario == usuario:
		tiene_equipo = True
		if partido.alineacion_visitante.estaPreparada():
			editar = True
	es_creador = liga.creador == usuario

	# Comprobamos si el partido ha acabado
	finalizado = partido.finalizado()

	# Comprobar si se puede jugar el partido
	es_jugable = False
	jornada_actual = liga.getJornadaActual()
	if partido.jornada == jornada_actual and not finalizado:
		es_jugable = True

	# Si el partido ha finalizado
	if finalizado:
		# Obtener datos sobre los sucesos del partido
		for equipo in (equipo_local, equipo_visitante):
			sucesos = partido.suceso_set.filter(equipo = equipo)
			equipo.num_acciones = sucesos.count()

			# Regates
			equipo.regates_realizados = sucesos.filter(tipo = Suceso.REGATE, valor = 1).count()
			equipo.regates_fallados = sucesos.filter(tipo = Suceso.REGATE, valor = 0).count()

			if equipo.regates_realizados + equipo.regates_fallados == 0:
				equipo.porcentaje_regates_exito = 0
			else:
				equipo.porcentaje_regates_exito = (1.0 * equipo.regates_realizados) / (equipo.regates_realizados + equipo.regates_fallados)

			equipo.regates_totales = equipo.regates_realizados + equipo.regates_fallados

			# Pases
			equipo.pases_realizados = sucesos.filter(tipo = Suceso.PASE, valor = 1).count()
			equipo.pases_fallados = sucesos.filter(tipo = Suceso.PASE, valor = 0).count()

			if equipo.pases_realizados + equipo.pases_fallados == 0:
				equipo.porcentaje_pases_exito = 0
			else:
				equipo.porcentaje_pases_exito = (1.0 * equipo.pases_realizados) / (equipo.pases_realizados + equipo.pases_fallados)

			equipo.pases_totales = equipo.pases_realizados + equipo.pases_fallados

			# Disparos
			equipo.disparos_parados = sucesos.filter(tipo = Suceso.DISPARO, valor = 1).count()
			equipo.disparos_fuera = sucesos.filter(tipo = Suceso.DISPARO, valor = 0).count()
			equipo.goles = sucesos.filter(tipo = Suceso.GOL).count()

			equipo.remates_puerta = equipo.goles + equipo.disparos_parados + equipo.disparos_fuera
			equipo.balones_perdidos = equipo.regates_fallados + equipo.pases_fallados + equipo.disparos_parados + equipo.disparos_fuera

		equipo_local.balones_recuperados = equipo_visitante.regates_fallados + equipo_visitante.pases_fallados + equipo_visitante.disparos_parados
		equipo_visitante.balones_recuperados = equipo_local.regates_fallados + equipo_local.pases_fallados + equipo_local.disparos_parados
		#--------------------------------------------------

		# Porcentajes
		num_acciones_total = equipo_local.num_acciones + equipo_visitante.num_acciones
		for equipo in (equipo_local, equipo_visitante):
			equipo.porc_posesion = round((100.0 * equipo.num_acciones) / num_acciones_total, 1)
			equipo.porc_regates_exito = round((100.0 * equipo.regates_realizados) / equipo.regates_totales, 1)
			equipo.porc_pases_exito = round((100.0 * equipo.pases_realizados) / equipo.pases_totales, 1)

		for equipo, alineacion in ((equipo_local, partido.alineacion_local), (equipo_visitante, partido.alineacion_visitante)):
			# Obtener datos de los titulares del equipo
			equipo.titulares = alineacion.getDatosTitulares()

			equipo.valor_titulares = 0
			equipo.num_df = 0
			equipo.num_cc = 0
			equipo.num_dl = 0
			for t in equipo.titulares:
				# Valor total del equipo
				equipo.valor_titulares += t.atributos.valorMercado()

				# Número de jugadores por posición
				if t.posicion == JugadorPartido.DEFENSA:
					equipo.num_df += 1
				elif t.posicion == JugadorPartido.CENTROCAMPISTA:
					equipo.num_cc += 1
				elif t.posicion == JugadorPartido.DELANTERO:
					equipo.num_dl += 1

	d = {"jornada" : jornada,
		 "equipo_local" : equipo_local,
		 "equipo_visitante" : equipo_visitante,
		 "liga" : liga,
		 "partido" : partido,
		 "usuario" : usuario,
		 "finalizado" : finalizado,
		 "es_creador" : es_creador,
		 "tiene_equipo" : tiene_equipo,
		 "es_jugable" : es_jugable,
		 "editar" : editar,
		}
	return generarPagina(request, "juego/partidos/ver_partido.html", d)

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['partido_actual'])
def preparar_partido(request):
	''' Muestra los datos para preparar un partido '''
	usuario = request.user

	partido = request.session['partido_actual']

	# Comprobar que el partido no se haya jugado ya
	if partido.finalizado():
		return devolverMensaje(request, "Este partido ya acabo", 0, "/partidos/ver/%d/" % partido.id)

	# Comprobar si el usuario juega en el partido
	if (partido.equipo_local.usuario == usuario): # Juega como local
		equipo = partido.equipo_local
		alineacion = partido.alineacion_local
	elif (partido.equipo_visitante.usuario == usuario): # Juega como visitante
		equipo = partido.equipo_visitante
		alineacion = partido.alineacion_visitante
	else: # No juega como naaaaaaaaaaaaaaa
		return devolverMensaje(request, "No tienes equipo en este partido", 0, "/partidos/ver/%d/" % partido.id)

	editar = alineacion.estaPreparada();

	if request.method == 'POST':
		form = PrepararEquipoForm(alineacion, equipo, request.POST)
		if form.is_valid():
			delanteros = form.cleaned_data['delanteros']
			centrocampistas = form.cleaned_data['centrocampistas']
			defensas = form.cleaned_data['defensas']
			portero = form.cleaned_data['portero']
			suplentes = form.cleaned_data['suplentes']
			alineacion.setAlineacion(portero, defensas, centrocampistas, delanteros, suplentes)
			alineacion.save()
			# Preparar la alineacion perfectamente
			if editar:
				return devolverMensaje(request, "Se ha editado correctamente la alineacion", 1, "/partidos/ver/%d/" % partido.id)
			else:
				return devolverMensaje(request, "Se ha creado correctamente la alineacion", 1, "/partidos/ver/%d/" % partido.id)
	else:
		form = PrepararEquipoForm(alineacion, equipo)

	delanteros = alineacion.getDelanteros()
	centrocampistas = alineacion.getCentrocampistas()
	defensas = alineacion.getDefensas()
	portero = alineacion.getPortero()
	suplentes = alineacion.getSuplentes()

	jugadores = equipo.getJugadores()

	d = {"form": form,
		"editar" : editar,
		"partido" : partido,
		"equipo" : equipo,
		"jugadores" : jugadores,
		"delanteros" : delanteros,
		"defensas" : defensas,
		"portero" : portero,
		"centrocampistas" : centrocampistas,
		"suplentes" : suplentes
		}

	return generarPagina(request, "juego/partidos/preparar_partido.html", d)

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['partido_actual'])
def ver_repeticion_partido(request):
	''' Muestra la repeticion de un partido '''
	# Obtenemos el usuario
	usuario = request.user

	# Obtenemos el partido
	partido = request.session['partido_actual']

	# Obtener sucesos del partido
	sucesos = partido.suceso_set.all()

	# Obtenemos la liga y la jornada
	jornada = partido.jornada
	liga = jornada.liga

	# Obtenemos los equipos que juegan en el partido
	equipo_local = partido.equipo_local
	equipo_visitante = partido.equipo_visitante

	# Comprobamos si el partido ha acabado
	finalizado = partido.finalizado()

	# Si el partido ha finalizado
	if not finalizado:
		return devolverMensaje(request, "Error, el partido no acabó", 0, "/partidos/ver/%d/" % partido.id)

	siglas_local = partido.equipo_local.siglas
	siglas_visitante = partido.equipo_visitante.siglas

	d = {
		"jornada" : jornada,
		"liga" : liga,
		"partido" : partido,
		"sucesos" : sucesos,
		"siglas_local" : siglas_local,
		"siglas_visitante" : siglas_visitante
	}

	return generarPagina(request, "juego/partidos/ver_repeticion_partido.html", d)

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['liga_actual', 'equipo_propio'])
def ver_partidos_propios(request):
	""" Accede directamente al siguiente partido """

	liga = request.session['liga_actual']
	equipo = request.session['equipo_propio']

	partidos = liga.partido_set.filter(Q(equipo_local = equipo) | Q(equipo_visitante = equipo))

	partidos_jugados = partidos.filter(jugado = True)
	partidos_no_jugados = partidos.filter(jugado = False)
	if partidos_no_jugados.count() > 0:
		partido_actual = partidos_no_jugados[0]
	else:
		partido_actual = None

	d = {"partidos_jugados" : partidos_jugados,
		 "partidos_no_jugados" : partidos_no_jugados,
		 "partido_actual" : partido_actual,
		 }

	return generarPagina(request, "juego/partidos/listar_partidos_equipo.html", d)

########################################################################

@login_required
@actualizarLiga
@comprobarSesion(['liga_actual', 'equipo_propio'])
def proximo_partido(request):
	""" Accede directamente al siguiente partido """
	liga = request.session['liga_actual']
	equipo = request.session['equipo_propio']

	partidos = liga.partido_set.filter(jugado = False).filter(Q(equipo_local = equipo) | Q(equipo_visitante = equipo))

	if partidos.count() > 0:
		partido_actual = partidos[0]
	else:
		return devolverMensaje(request, "Error, no hay mas partidos por jugar en la liga", 0)

	return redireccionar('/partidos/ver/%s/' % (partido_actual.id))

########################################################################
