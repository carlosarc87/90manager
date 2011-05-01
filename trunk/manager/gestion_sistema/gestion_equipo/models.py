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
from django.db.models import Q, F

from gestion_sistema.gestion_liga.models import Liga
from gestion_usuario.models import Usuario

########################################################################

# Equipo
class Equipo(models.Model):
	''' Representa un equipo en el sistema '''
	nombre = models.CharField(max_length = 50)
	#tipo_club = models.PositiveIntField(default = 0)
	siglas = models.CharField(max_length = 3)

	usuario = models.ForeignKey(Usuario, null = True)
	liga = models.ForeignKey(Liga)

	dinero = models.IntegerField(default = 0, max_length = 15)

	# Funciones
	def pagar(self, cantidad):
		''' Paga una cantidad al equipo '''
		self.dinero += cantidad
		self.save()

	def cobrar(self, cantidad):
		''' Cobra una cantidad al equipo '''
		self.dinero -= cantidad
		self.save()

	def agregarJugador(self, jugador):
		''' Añade un jugador al equipo '''
		self.atributosvariablesjugador_set.add(jugador.atributos)

	def getJugadores(self):
		''' Devuelve los jugadores del equipo '''
		atributos = self.atributosvariablesjugador_set.all()
		jugadores = []
		for atrib in atributos:
			jugadores.append(atrib.jugador)
		return jugadores

	def getPartidos(self, liga):
		''' Devuelve los partidos de una liga en los que juega '''
		from gestion_sistema.gestion_partido.models import Partido
		q = Partido.objects.filter(Q(equipo_local = self) | Q(equipo_visitante = self))
		jornadas = list(liga.jornada_set.all())
		lista = q.filter(jornada__in = jornadas)
		return lista

	def getPartidosHastaJornada(self, jornada, incluida = False):
		''' Devuelve los partidos jugados hasta la jornada '''
		# Obtenemos la liga
		liga = jornada.liga
		# Obtenemos los partidos en los que juega
		partidos = self.getPartidos(liga)
		if not incluida:
			return partidos.filter(jornada__lt = jornada)
		else:
			return partidos.filter(jornada__lte = jornada)

	def getPartidosGanados(self, jornada, incluida = False):
		''' Devuelve los partidos ganados hasta la jornada '''
		# Partidos hasta la jornada
		partidos = self.getPartidosHastaJornada(jornada, incluida)
		# Partidos jugados
		partidos_jugados = partidos.filter(jugado = True)
		# Partidos ganados como visitante
		partidos_ganados = partidos_jugados.filter(
			Q(Q(equipo_local = self) & Q(goles_local__gt = F('goles_visitante'))) |
			Q(Q(equipo_visitante = self) & Q(goles_local__lt = F('goles_visitante'))))
		return partidos_ganados

	def getPartidosPerdidos(self, jornada, incluida = False):
		''' Devuelve los partidos perdidos hasta la jornada '''
		# Partidos hasta la jornada
		partidos = self.getPartidosHastaJornada(jornada, incluida)
		# Partidos jugados
		partidos_jugados = partidos.filter(jugado = True)
		# Partidos perdidos como visitante
		partidos_perdidos = partidos_jugados.filter(
			Q(Q(equipo_local = self) & Q(goles_local__lt = F('goles_visitante'))) |
			Q(Q(equipo_visitante = self) & Q(goles_local__gt = F('goles_visitante'))))
		return partidos_perdidos

	def getPartidosEmpatados(self, jornada, incluida = False):
		''' Devuelve los partidos empatados hasta la jornada '''
		# Partidos hasta la jornada
		partidos = self.getPartidosHastaJornada(jornada, incluida)
		# Partidos jugados
		partidos_jugados = partidos.filter(jugado = True)
		# Partidos perdidos como visitante
		partidos_empatados = partidos_jugados.filter(goles_local = F('goles_visitante'))
		return partidos_empatados

	def generarJugadoresAleatorios(self, sexo_permitido = 0, num_jugadores_inicial = 25, max_nivel = 50):
		''' Genera un conjunto de jugadores aleatorios para el equipo '''
		from gestion_sistema.gestion_jugador.models import Jugador
		from gestion_sistema.gestion_jugador.func import nombreJugadorAleatorio, listaNombres
		from datetime import date, timedelta
		from random import randint

		hombres_participan = False
		mujeres_participan = False

		edad_min = 18
		edad_max = 35

		# Establecer variables dependiendo del sexo_permitido en la liga
		if sexo_permitido == 0: # Solo hombres
			hombres_participan = True
			lista_nombres_hombres = listaNombres("nombres_hombres.txt")

		elif sexo_permitido == 1: # Solo mujeres
			mujeres_participan = True
			lista_nombres_mujeres = listaNombres("nombres_mujeres.txt")

		else: # Hombres y mujeres
			hombres_participan = True
			mujeres_participan = True
			lista_nombres_hombres = listaNombres("nombres_hombres.txt")
			lista_nombres_mujeres = listaNombres("nombres_mujeres.txt")

		# Array con todos los apellidos obtenidos del fichero dado
		lista_apellidos = listaNombres("apellidos.txt")

		# Array con todos los dorsales disponibles
		#dorsales_disponibles = range(1, 100)

		# Generar jugadores
		for j in range(1, num_jugadores_inicial + 1):
			# Establecer posición
			if (j % 10 == 1):
				posicion = "PORTERO"
			elif (j % 10 >= 2) and (j % 10 <= 4):
				posicion = "DEFENSA"
			elif (j % 10 >= 5) and (j % 10 <= 7):
				posicion = "CENTROCAMPISTA"
			else:
				posicion = "DELANTERO"

			# Establecer dorsal
			#dorsal = dorsales_disponibles.pop(randint(0, len(dorsales_disponibles) - 1))
			dorsal = j

			# Obtener datos de hombre o mujer según si participan o no
			if ((j % 2 == 0) and hombres_participan) or (mujeres_participan == False):
				lista_nombres = lista_nombres_hombres
				sexo = 'M'
			else:
				lista_nombres = lista_nombres_mujeres
				sexo = 'F'

			# Establecer variables del jugador
			nombre_aleatorio, apodo_aux = nombreJugadorAleatorio(lista_nombres, lista_apellidos)
			fecha_nacimiento = date.today() - timedelta(randint(edad_min, edad_max) * 365) + timedelta(randint(0, 364))

			# Reducir un poco el nivel máximo dependiendo de la edad
			hoy = date.today()
			edad = hoy - fecha_nacimiento
			anios = (int)(edad.days / 365)

			# Cada 2 años de diferencia con 28 se resta un punto al nivel máximo
			max_nivel_jug = max_nivel - (int)(abs(28 - anios) / 2)

			# Asignar variables al jugador
			jugador = Jugador(nombre = nombre_aleatorio, apodo = apodo_aux, fecha_nacimiento = fecha_nacimiento, sexo = sexo)
			jugador.save()
			atributos = jugador.generarAtributos(self, dorsal, posicion, max_nivel_jug)
			atributos.save()

			jugador.setAparienciaAleatoria()

			# Guardar jugador
			jugador.save()

			# Añadir jugador al equipo
			self.agregarJugador(jugador)

	def __unicode__(self):
		return self.nombre

########################################################################
