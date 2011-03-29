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

from gestion_usuario.models import Usuario

import random

########################################################################

# Liga
class Liga(models.Model):
	''' Representa una liga '''
	creador = models.ForeignKey(Usuario)
	nombre = models.CharField(max_length = 50)
	num_equipos = models.IntegerField(null = True, default = 0)
	publica = models.BooleanField(default = True) # Visibilidad de la liga

	# Reglas liga
	sexo_permitido = models.IntegerField(default = 0)
	permitir_bots = models.BooleanField(default = True) # Indica si se permiten (1) o no (0) bots en las ligas
	inteligencia_bots = models.IntegerField(default = 3, null = True) # Nivel de inteligencia de los bots (1 - 5(muy alto))
	tipo_avance_jornadas = models.IntegerField(default = 0) # Tipo de avance de las jornadas (0 - Manual, 1 - Auto, 2 - Esperar hora)

	# Reglas equipos
	dinero_inicial = models.IntegerField(default = 20000, max_length = 15)
	num_jugadores_inicial = models.IntegerField(default = 20, max_length = 3)
	nivel_max_jugadores_inicio = models.IntegerField(default = 50, max_length = 3) # Nivel máximo inicial de los jugadores al comienzo de la liga (10 - 100)

	def activada(self):
		''' Devuelve si una liga ya ha empezado a jugarse '''
		return self.jornada_set.count() > 0

	def obtenerJornadaActual(self):
		''' Devuelve la jornada actual de la liga o None en caso de haber acabado '''
		# Obtenemos las jornadas no jugadas
		jornadas_restantes = self.jornada_set.filter(jugada = False)
		jornada_actual = None
		if len(jornadas_restantes) > 0:
			# No ha acabado aun
			jornada_actual = jornadas_restantes[0]
		return jornada_actual

	def rellenarLiga(self):
		''' Rellena los huecos vacios de una liga con equipos controlados por bots '''
		# Generar los equipos
		from gestion_sistema.gestion_equipo.func import listaNombres, nombreEquipoAleatorio
		from gestion_sistema.gestion_equipo.models import Equipo

		# -------------------------------------------------
		# Obtener listas de nombres
		# -------------------------------------------------
		# Tipo club
		lista_nombres_tipo_club = listaNombres('nombres_equipos/tipo_club.txt') # Tipos de club
		lon_lista_nombres_tipo_club = len(lista_nombres_tipo_club)

		# Parte 1
		lista_parte1 = []

		# Animales
		lista_nombres_animales = listaNombres('nombres_equipos/animales.txt')
		lista_parte1 += lista_nombres_animales

		# Razas
		lista_nombres_razas = listaNombres('nombres_equipos/razas.txt')
		lista_parte1 += lista_nombres_razas

		# Objetos
		lista_nombres_objetos = listaNombres('nombres_equipos/objetos.txt')
		lista_parte1 += lista_nombres_objetos

		lon_lista_parte1 = len(lista_parte1)

		# Parte 2
		lista_parte2 = []

		# Colores
		lista_nombres_colores = listaNombres('nombres_equipos/colores.txt')
		lista_parte2 += lista_nombres_colores

		# Formas
		lista_nombres_formas = listaNombres('nombres_equipos/formas.txt')
		lista_parte2 += lista_nombres_formas
		# -------------------------------------------------

		for i in range(self.equipo_set.count(), self.num_equipos):
			nombre_eq, siglas_eq = nombreEquipoAleatorio(lista_nombres_tipo_club, lista_parte1, lista_parte2)
			
			# Comprobar que las siglas no se repitan
			equipos_liga = self.equipo_set.all()
			lista_equipos = []
			for e in equipos_liga:
				lista_equipos.append(e.siglas)
			
			c = 1
			while lista_equipos.count(siglas_eq) > 0:
				siglas_eq = siglas_eq[:1] + str(c)
				c += 1
			
			equipo = Equipo(nombre = nombre_eq, siglas = siglas_eq, usuario = None, liga = self, dinero = self.dinero_inicial)
			equipo.save()
			equipo.generarJugadoresAleatorios(self.sexo_permitido, self.num_jugadores_inicial, self.nivel_max_jugadores_inicio)

	def generarJornadas(self):
		''' Genera las jornadas de una liga '''
		from gestion_sistema.gestion_jornada.models import Jornada
		from gestion_sistema.gestion_partido.models import Partido

		jornadas = []
		num_jornadas_ida = self.num_equipos - 1
		num_emparejamientos_jornada = self.num_equipos / 2
		# Creamos una copia de los equipos
		id_equipos = list(self.equipo_set.all())
		random.shuffle(id_equipos)

		# Crear jornadas de la ida
		j = 0
		while j < num_jornadas_ida:
			emparejamientos_jornada = []
			for emp in range(0, num_emparejamientos_jornada):
				# Alternar local y visitante
				if (j % 2) == 0:
					emparejamiento = [id_equipos[self.num_equipos - emp - 1], id_equipos[emp]]
				else:
					emparejamiento = [id_equipos[emp], id_equipos[self.num_equipos - emp - 1]]
				# Annadir emparejamiento a la lista de emparejamientos de la jornada
				emparejamientos_jornada.append(emparejamiento)
			# Annadir todos los emparejamientos a la jornada
			jornadas.append(emparejamientos_jornada)

			# Colocar segundo equipo al final del vector. El primer equipo siempre queda fijo
			equipo_pal_fondo = id_equipos.pop(1)
			id_equipos.append(equipo_pal_fondo)
			j += 1

		# Jornadas de la vuelta
		ultima_jornada = num_jornadas_ida * 2
		while (j < ultima_jornada):
			emparejamientos_jornada = []
			for emp in range(0, num_emparejamientos_jornada):
				emparejamiento = [jornadas[j - num_jornadas_ida][emp][1], jornadas[j - num_jornadas_ida][emp][0]]
				emparejamientos_jornada.append(emparejamiento)
			# Annadir todos los emparejamientos a la jornada
			jornadas.append(emparejamientos_jornada)
			j += 1

		# Guardar jornadas y partidos
		for i in range(len(jornadas)):
			jornada = Jornada(liga = self, numero = i + 1, jugada = False)
			jornada.save()
			for emparejamiento in jornadas[i]:
				partido = Partido(jornada = jornada, equipo_local = emparejamiento[0], equipo_visitante = emparejamiento[1], jugado = False)
				partido.save()

	def agregarEquipo(self, equipo):
		''' Agrega un equipo a la liga '''
		self.equipos_set.add(equipo)

	def avanzarJornada(self):
		''' Avanza una jornada en la liga '''
		# Sacar primera jornada no jugada
		jornada = self.obtenerJornadaActual()
		if not jornada:
			return False

		jornada.jugarPartidosRestantes()

		# Actualizar subastas
		for subasta in self.subasta_set.all():
			subasta.expira -= 1
			if subasta.expira == 0:
				# Completar el traslado
				subasta.finalizar()
				subasta.delete()
			else:
				subasta.save()

		# Generar los datos de clasificacion de la siguiente jornada
		siguiente_jornada = self.obtenerJornadaActual()
		if siguiente_jornada:
			siguiente_jornada.generarClasificacion()
			siguiente_jornada.mantenerAlineaciones(jornada)

		return True

	def __unicode__(self):
		''' Devuelve una cadena de texto que representa la clase '''
		return self.nombre

########################################################################
