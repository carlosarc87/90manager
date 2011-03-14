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
from django.db import models

from gestion_sistema.gestion_liga.models import Liga
from gestion_usuario.models import Usuario

########################################################################

# Equipo
class Equipo(models.Model):
	''' Representa un equipo en el sistema '''
	nombre = models.CharField(max_length = 50)
	usuario = models.ForeignKey(Usuario, null = True)
	liga = models.ForeignKey(Liga)

	# Funciones
	def agregarJugador(self, jugador):
		''' Añade un jugador al equipo '''
		self.jugador_set.add(jugador)

	def generarJugadoresAleatorios(self):
		''' Genera un conjunto de jugadores aleatorios para el equipo '''
		from gestion_sistema.gestion_jugador.models import Jugador
		from gestion_sistema.gestion_jugador.func import nombreJugadorAleatorio
		# Generar jugadores
		for j in range(1, 21):
			# Establecer posición
			if (j == 1 or j == 20):
				posicion = "PORTERO"
			elif ((j >= 2 and j <= 5) or (j >= 12 and j <= 14)):
				posicion = "DEFENSA"
			elif ((j >= 6 and j <= 9) or (j >= 15 and j <= 17)):
				posicion = "CENTROCAMPISTA"
			else:
				posicion = "DELANTERO"

			jugador = Jugador(equipo = self, nombre = nombreJugadorAleatorio(), transferible = False)
			jugador.setNumero(j)
			jugador.setPosicion(posicion)
			jugador.setHabilidadesAleatorias(posicion, 50)
			jugador.save()
			self.agregarJugador(jugador)

	def __unicode__(self):
		return self.nombre

########################################################################
