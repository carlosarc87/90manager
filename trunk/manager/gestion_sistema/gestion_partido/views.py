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

from models import Partido
from forms import PrepararEquipoForm

from gestion_base.func import devolverMensaje
from gestion_usuario.func import redireccionar, generarPagina

########################################################################

@login_required
def jugar_partido(request, partido_id):
	''' Juega un partido '''
	# Obtenemos el usuario
	usuario = request.user

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

	return redireccionar("/partidos/ver/%s/" % (partido_id))

########################################################################

@login_required
def ver_partido(request, partido_id):
	''' Muestra los datos de un partido '''
	# Obtenemos el usuario
	usuario = request.user

	if Partido.objects.filter(id = partido_id).count() == 0:
		return devolverMensaje(request, "Error, no existe un partido con identificador %s" % partido_id)

	# Obtenemos el partido
	partido = Partido.objects.get(id = partido_id)

	# Obtener sucesos del partido
	partido.sucesos = partido.suceso_set.all()

	# Obtenemos la liga y la jornada
	jornada = partido.jornada
	liga = jornada.liga

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
	jornada_actual = liga.obtenerJornadaActual()
	if partido.jornada == jornada_actual and not finalizado:
		es_jugable = True

	# Si el partido ha finalizado
	if finalizado:
		# Obtener datos sobre los sucesos del partido
		#--------------------------------------------------
		# Equipo local
		#--------------------------------------------------
		q = partido.suceso_set.filter(equipo = equipo_local)
		equipo_local.num_acciones = q.count()

		# Regates
		q = partido.suceso_set.filter(equipo = equipo_local, tipo = "Regate realizado")
		equipo_local.regates_realizados = q.count()
		q = partido.suceso_set.filter(equipo = equipo_local, tipo = "Regate fallado")
		equipo_local.regates_fallados = q.count()

		if equipo_local.regates_realizados + equipo_local.regates_fallados == 0:
			equipo_local.porcentaje_regates_exito = 0
		else:
			equipo_local.porcentaje_regates_exito = (1.0 * equipo_local.regates_realizados) / (equipo_local.regates_realizados + equipo_local.regates_fallados)

		equipo_local.regates_totales = equipo_local.regates_realizados + equipo_local.regates_fallados

		# Pases
		q = partido.suceso_set.filter(equipo = equipo_local, tipo = "Pase realizado")
		equipo_local.pases_realizados = q.count()
		q = partido.suceso_set.filter(equipo = equipo_local, tipo = "Pase fallado")
		equipo_local.pases_fallados = q.count()

		if equipo_local.pases_realizados + equipo_local.pases_fallados == 0:
			equipo_local.porcentaje_pases_exito = 0
		else:
			equipo_local.porcentaje_pases_exito = (1.0 * equipo_local.pases_realizados) / (equipo_local.pases_realizados + equipo_local.pases_fallados)

		equipo_local.pases_totales = equipo_local.pases_realizados + equipo_local.pases_fallados

		# Disparos
		q = partido.suceso_set.filter(equipo = equipo_local, tipo = "Disparo parado")
		equipo_local.disparos_parados = q.count()
		q = partido.suceso_set.filter(equipo = equipo_local, tipo = "Disparo fuera")
		equipo_local.disparos_fuera = q.count()
		q = partido.suceso_set.filter(equipo = equipo_local, tipo = "Gol")
		equipo_local.goles = q.count()
		#--------------------------------------------------

		# Equipo visitante
		#--------------------------------------------------
		q = partido.suceso_set.filter(equipo = equipo_visitante)
		equipo_visitante.num_acciones = q.count()

		# Regates
		q = partido.suceso_set.filter(equipo = equipo_visitante, tipo = "Regate realizado")
		equipo_visitante.regates_realizados = q.count()
		q = partido.suceso_set.filter(equipo = equipo_visitante, tipo = "Regate fallado")
		equipo_visitante.regates_fallados = q.count()

		if equipo_visitante.regates_realizados + equipo_visitante.regates_fallados == 0:
			equipo_visitante.porcentaje_regates_exito = 0
		else:
			equipo_visitante.porcentaje_regates_exito = (1.0 * equipo_visitante.regates_realizados) / (equipo_visitante.regates_realizados + equipo_visitante.regates_fallados)

		equipo_visitante.regates_totales = equipo_visitante.regates_realizados + equipo_visitante.regates_fallados

		# Pases
		q = partido.suceso_set.filter(equipo = equipo_visitante, tipo = "Pase realizado")
		equipo_visitante.pases_realizados = q.count()
		q = partido.suceso_set.filter(equipo = equipo_visitante, tipo = "Pase fallado")
		equipo_visitante.pases_fallados = q.count()

		if equipo_visitante.pases_realizados + equipo_visitante.pases_fallados == 0:
			equipo_visitante.porcentaje_pases_exito = 0
		else:
			equipo_visitante.porcentaje_pases_exito = (1.0 * equipo_visitante.pases_realizados) / (equipo_visitante.pases_realizados + equipo_visitante.pases_fallados)

		equipo_visitante.pases_totales = equipo_visitante.pases_realizados + equipo_visitante.pases_fallados

		# Disparos
		q = partido.suceso_set.filter(equipo = equipo_visitante, tipo = "Disparo parado")
		equipo_visitante.disparos_parados = q.count()
		q = partido.suceso_set.filter(equipo = equipo_visitante, tipo = "Disparo fuera")
		equipo_visitante.disparos_fuera = q.count()
		q = partido.suceso_set.filter(equipo = equipo_visitante, tipo = "Gol")
		equipo_visitante.goles = q.count()

		equipo_local.remates_puerta = equipo_local.goles + equipo_local.disparos_parados + equipo_local.disparos_fuera
		equipo_local.balones_perdidos = equipo_local.regates_fallados + equipo_local.pases_fallados + equipo_local.disparos_parados + equipo_local.disparos_fuera
		equipo_local.balones_recuperados = equipo_visitante.regates_fallados + equipo_visitante.pases_fallados + equipo_visitante.disparos_parados

		equipo_visitante.remates_puerta = equipo_visitante.goles + equipo_visitante.disparos_parados + equipo_visitante.disparos_fuera
		equipo_visitante.balones_perdidos = equipo_visitante.regates_fallados + equipo_visitante.pases_fallados + equipo_visitante.disparos_parados + equipo_visitante.disparos_fuera
		equipo_visitante.balones_recuperados = equipo_local.regates_fallados + equipo_local.pases_fallados + equipo_local.disparos_parados
		#--------------------------------------------------

		# Porcentajes
		equipo_local.porc_posesion = round((100.0 * equipo_local.num_acciones) / (equipo_local.num_acciones + equipo_visitante.num_acciones), 1)
		equipo_local.porc_regates_exito = round((100.0 * equipo_local.regates_realizados) / equipo_local.regates_totales, 1)
		equipo_local.porc_pases_exito = round((100.0 * equipo_local.pases_realizados) / equipo_local.pases_totales, 1)

		equipo_visitante.porc_posesion = round((100.0 * equipo_visitante.num_acciones) / (equipo_local.num_acciones + equipo_visitante.num_acciones), 1)
		equipo_visitante.porc_regates_exito = round((100.0 * equipo_visitante.regates_realizados) / equipo_visitante.regates_totales, 1)
		equipo_visitante.porc_pases_exito = round((100.0 * equipo_visitante.pases_realizados) / equipo_visitante.pases_totales, 1)

		# Obtener datos de los titulares del equipo local
		equipo_local.titulares = partido.alineacion_local.getDatosTitulares()

		equipo_local.valor_titulares = 0
		equipo_local.num_df = 0
		equipo_local.num_cc = 0
		equipo_local.num_dl = 0
		for t in equipo_local.titulares:
			# Valor total del equipo
			equipo_local.valor_titulares += t.atributos.valorMercado()

			# Número de jugadores por posición
			if t.posicion == 'DF':
				equipo_local.num_df += 1
			elif t.posicion == 'CC':
				equipo_local.num_cc += 1
			elif t.posicion == 'DL':
				equipo_local.num_dl += 1

		# Obtener valor total de los titulares del equipo visitante
		equipo_visitante.titulares = partido.alineacion_visitante.getDatosTitulares()

		equipo_visitante.valor_titulares = 0
		equipo_visitante.num_df = 0
		equipo_visitante.num_cc = 0
		equipo_visitante.num_dl = 0
		for t in equipo_visitante.titulares:
			# Valor total del equipo
			equipo_visitante.valor_titulares += t.atributos.valorMercado()

			# Número de jugadores por posición
			if t.posicion == 'DF':
				equipo_visitante.num_df += 1
			elif t.posicion == 'CC':
				equipo_visitante.num_cc += 1
			elif t.posicion == 'DL':
				equipo_visitante.num_dl += 1

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
	return generarPagina("juego/partidos/ver_partido.html", d, request)

########################################################################

@login_required
def preparar_partido(request, partido_id):
	''' Muestra los datos para preparar un partido '''
	partido = Partido.objects.get(id = partido_id)
	usuario = request.user

	if Partido.objects.filter(id = partido_id).count() == 0:
		return devolverMensaje(request, "Error, no existe un partido con identificador %s" % partido_id)

	# Comprobar que el partido no se haya jugado ya
	if partido.finalizado():
		return devolverMensaje(request, "Este partido ya acabo", "/partidos/ver/%d/" % partido.id)

	# Comprobar si el usuario juega en el partido
	if (partido.equipo_local.usuario == usuario): # Juega como local
		equipo = partido.equipo_local
		alineacion = partido.alineacion_local
	elif (partido.equipo_visitante.usuario == usuario): # Juega como visitante
		equipo = partido.equipo_visitante
		alineacion = partido.alineacion_visitante
	else: # No juega como naaaaaaaaaaaaaaa
		return devolverMensaje(request, "No tienes equipo en este partido", "/partidos/ver/%d/" % partido.id)

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
				return devolverMensaje(request, "Se ha editado correctamente la alineacion", "/partidos/ver/%d/" % partido.id)
			else:
				return devolverMensaje(request, "Se ha creado correctamente la alineacion", "/partidos/ver/%d/" % partido.id)
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

	return generarPagina("juego/partidos/preparar_partido.html", d, request, True)

@login_required
def ver_repeticion_partido(request, partido_id):
	''' Muestra la repeticion de un partido '''
	# Obtenemos el usuario
	usuario = request.user

	if Partido.objects.filter(id = partido_id).count() == 0:
		return devolverMensaje(request, "Error, no existe un partido con identificador %s" % partido_id)

	# Obtenemos el partido
	partido = Partido.objects.get(id = partido_id)

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
		return devolverMensaje(request, "Error, el partido no acabó", "/patidos/ver/%d/" % partido_id)

	d = { "sucesos" : sucesos }
	return generarPagina("juego/partidos/ver_repeticion_partido.html", d, request)

########################################################################
