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

from gestion_sistema.decorators import actualizarLiga

from models import Subasta
from forms import SubastaForm, PujarForm
from gestion_sistema.gestion_jugador.models import Jugador
from gestion_sistema.gestion_liga.models import Liga
from gestion_sistema.gestion_equipo.models import Equipo

from gestion_base.func import devolverMensaje, redireccionar, generarPagina

########################################################################

@login_required
@actualizarLiga
def crear_subasta(request):
	''' Crea una subasta de un jugador '''
	usuario = request.user

	jugador = request.session['jugador_actual']

	if jugador.atributos.ofertado:
		return devolverMensaje(request, "Este jugador ya está en subasta", "/jugadores/ver/%d/" % jugador.id)

	if jugador.atributos.equipo.usuario != usuario:
		return devolverMensaje(request, "No eres propietario del equipo del jugador")

	if not jugador.atributos.equipo.liga.activada():
		return devolverMensaje(request, "Hasta que la liga no esté activada no pueden haber subastas")

	duracion_liga = jugador.atributos.equipo.liga.getNumJornadas();

	if request.method == 'POST':
		form = SubastaForm(jugador, request.POST)
		if form.is_valid():
			subasta = form.save(commit = False)

			#comision = subasta.puja * (subasta.getTiempoRestante() / (duracion_liga * 1.0))
			comision = 5

			if comision > jugador.atributos.equipo.dinero:
				return devolverMensaje(request, "No tienes suficiente dinero para pagar la comision", "/mercado/subastas/crear/%d/" % jugador.id)

			subasta.liga = jugador.atributos.equipo.liga
			subasta.estado = 0
			subasta.vendedor = jugador.atributos.equipo
			subasta.comprador = None
			subasta.atributos_jugador = jugador.atributos

			jugador.atributos.equipo.cobrar(comision)

			jugador.atributos.ofertado = True
			jugador.atributos.save()
			subasta.save()
			return devolverMensaje(request, "Se ha creado correctamente", "/mercado/subastas/ver/%d/" % subasta.id)
	else:
		form = SubastaForm(jugador)

	d = { "form": form, "jugador" : jugador, "duracion_liga" : duracion_liga }

	return generarPagina("juego/subastas/crear_subasta.html", d, request, True)

########################################################################

@login_required
@actualizarLiga
def ver_subastas_liga(request):
	''' Muestra las subastas de una liga '''
	usuario = request.user

	liga = request.session['liga_actual']

	subastas = liga.subasta_set.all()

	return generarPagina("juego/subastas/ver_subastas_liga.html", { "subastas" : subastas, "liga" : liga }, request)

########################################################################

@login_required
def ver_subasta_id(request, subasta_id):
	''' Muestra los datos de una subasta '''
	subastas = Subasta.objects.filter(id = subasta_id)
	if subastas.count() == 0:
		return devolverMensaje(request, "Error, no existe una subasta con identificador %s" % subasta_id)

	request.session['subasta_actual'] = subasta[0]

	return redireccion('/mercado/subastas/ver/')

########################################################################

@login_required
@actualizarLiga
def ver_subasta(request):
	''' Muestra los datos de una subasta '''
	# Obtenemos el usuario
	usuario = request.user

	# Obtenemos la subasta
	subasta = request.session['subasta_actual']

	# Equipo del usuario
	equipo_usuario = None
	form = None
	if usuario.equipo_set.filter(liga = subasta.liga).count():
		equipo_usuario = usuario.equipo_set.get(liga = subasta.liga)

	if subasta.vendedor != equipo_usuario:
		if request.method == 'POST':
			if not equipo_usuario:
				devolverMensaje('No puedes pujar en una liga en la que no juegas')
			form = PujarForm(subasta, equipo_usuario, request.POST)
			if form.is_valid():
				cantidad = form.cleaned_data['cantidad']
				subasta.pujar(equipo_usuario, cantidad)
				subasta.save()
				return devolverMensaje(request, "Cantidad apostada correctamente", "/mercado/subastas/ver/%d/" % subasta.id)
		else:
			form = PujarForm(subasta, equipo_usuario)

	d = {"equipo_usuario" : equipo_usuario,
		"subasta" : subasta,
		"form" : form,
		}
	return generarPagina("juego/subastas/ver_subasta.html", d, request, True)

########################################################################

@login_required
@actualizarLiga
def ver_subastas_equipo(request):
	''' Muestra las subastas de un equipo '''
	equipo = request.session['equipo_actual']

#	jugadores_en_subasta

#	subastas = equipo.subasta_set.all()
	subastas_comprador = equipo.subastas_como_comprador.all()
	subastas_vendedor = equipo.subastas_como_vendedor.all()
	d = {"subastas_comprador" : subastas_comprador,
		"subastas_vendedor" : subastas_vendedor,
		"equipo" : equipo,
		}
	return generarPagina("juego/subastas/ver_subastas_equipo.html", d, request)

########################################################################

@login_required
@actualizarLiga
def comprar_subasta(request):
	''' Muestra los datos de una subasta '''
	# Obtenemos el usuario
	usuario = request.user

	# Obtenemos la subasta
	subasta = request.session['subasta_actual']

	if not usuario.equipo_set.filter(liga = subasta.liga).count():
		return devolverMensaje(request, "Error, no tienes equipo en esta liga")

	if subasta.estado is not 0:
		return devolverMensaje(request, "Error, la subasta %s ya acabó" % subasta_id)

	if not subasta.precio_compra:
		return devolverMensaje(request, "Error, la subasta %s no puede comprarse directamente" % subasta_id)

	equipo = usuario.equipo_set.get(liga = subasta.liga)

	if subasta.vendedor == equipo:
		return devolverMensaje(request, "Error, no puedes comprarte tu propia subasta")

	if subasta.precio_compra > equipo.dinero:
		return devolverMensaje(request, "Error, no tienes dinero para comprar esta subasta", "/mercado/subastas/ver/%s/" % subasta_id)

	# Burocracia de comprar al jugador
	subasta.comprar(equipo)
	subasta.save()

	return devolverMensaje(request, "Ha comprado al jugador correctamente", "/mercado/subastas/ver/%s/" % subasta_id)

########################################################################

@login_required
@actualizarLiga
def mis_subastas(request):
	""" Muestra las subastas de un equipo """
	equipo = request.session['equipo_propio']

	subastas = equipo.subastas_como_vendedor.all()
	d = {"subastas" : subastas,
		}
	return generarPagina("juego/subastas/mis_subastas.html", d, request)

########################################################################

@login_required
@actualizarLiga
def mis_pujas(request):
	""" Muestra las subastas de un equipo """
	equipo = request.session['equipo_propio']

	subastas = equipo.subastas_como_comprador.all()
	d = {"subastas" : subastas,
		}
	return generarPagina("juego/subastas/mis_pujas.html", d, request)

########################################################################
