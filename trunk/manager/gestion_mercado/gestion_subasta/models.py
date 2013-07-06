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
from django.db import models

from gestion_sistema.gestion_equipo.models import Equipo
from gestion_sistema.gestion_liga.models import Liga
from gestion_sistema.gestion_jugador.models import AtributosVariablesJugador
from gestion_sistema.gestion_calendario.models import Evento

from gestion_usuario.gestion_notificacion.func import notificar, Notificacion

########################################################################

# Opciones disponibles
(ACTIVA, FINALIZADA, COMPRADA) = range(3)

# Subasta
class Subasta(Evento):
	''' Representa una subasta de un jugador en el sistema '''
	# Datos principales
	puja = models.PositiveIntegerField(default = 1)
	precio_compra = models.PositiveIntegerField(null = True, blank = True)
	estado = models.PositiveIntegerField(max_length = 1, default = 0)

	vendedor = models.ForeignKey(Equipo, related_name = 'subastas_como_vendedor')
	comprador = models.ForeignKey(Equipo, related_name = 'subastas_como_comprador', null = True, blank = True)

	# Atributos del jugador que se subasta
	atributos_jugador = models.OneToOneField(AtributosVariablesJugador)

	def comprar(self, equipo):
		''' Compra la subasta directamente con un equipo '''
		if self.tieneComprador():
			if self.comprador != equipo:
				notificar(self.comprador.usuario, TipoNotificacion.SUBASTA_SUPERADA_COMPRADA, identificador = self.atributos_jugador.jugador.id, liga = self.liga)
				self.comprador.pagar(self.subasta.puja)

		self.estado = COMPRADA # Indicar que se ha comprado
		self.comprador = equipo
		equipo.cobrar(self.precio_compra)

	def tieneComprador(self):
		''' Indica si alguien ha subastado '''
		return self.comprador != None

	def pujar(self, equipo, cantidad):
		''' Realiza una puja de un equipo '''
		# Notificar al anterior
		if self.tieneComprador():
			if self.comprador != equipo:
				notificar(self.comprador.usuario, Notificacion.SUBASTA_SUPERADA, identificador = self.id, liga = self.liga)
				self.comprador.pagar(self.subasta.puja)

		self.puja = cantidad
		self.comprador = equipo
		equipo.cobrar(cantidad)

	def finalizar(self):
		''' Finaliza y realiza los trámites oportunos de la subasta '''
		self.atributos_jugador.ofertado = False
		if self.tieneComprador():
			notificar(self.comprador.usuario, Notificacion.SUBASTA_GANADA, identificador = self.atributos_jugador.jugador.id, liga = self.liga)
			self.atributos_jugador.jugador.setEquipo(self.comprador)
			self.vendedor.pagar(self.puja)
		notificar(self.vendedor.usuario, Notificacion.SUBASTA_FINALIZADA, identificador = self.atributos_jugador.jugador.id, liga = self.liga)
		self.atributos_jugador.save()

	def getTiempoRestante(self):
		""" Devuelve el tiempo restante de la subasta """
		return self.fecha_fin - self.fecha_inicio

########################################################################
