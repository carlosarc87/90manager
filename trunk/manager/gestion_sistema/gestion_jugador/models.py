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
from random import randint

from gestion_sistema.gestion_equipo.models import Equipo

########################################################################

# Jugador
class Jugador(models.Model):
	''' Representa un jugador '''
	# Datos principales
	nombre = models.CharField(max_length = 80) # Nombre completo
	apodo = models.CharField(max_length = 30) # Apodo
	fecha_nacimiento = models.DateField() # Fecha de nacimiento
	sexo = models.CharField(max_length = 1) # Sexo ('M' - Masculino, 'F' - Femenino)

	# Datos equipo
	equipo = models.ForeignKey(Equipo) # Equipo al que pertenece
	numero = models.IntegerField(max_length = 2, null = True) # Dorsal en el equipo (0 - 99)
	ofertado = models.BooleanField(default = False) # Indica si está o no en la lista de jugadores transferibles

	# Habilidades de campo
	ataque = models.IntegerField(max_length = 3, blank = False) # Ataque (0 - 100)
	defensa = models.IntegerField(max_length = 3, blank = False) # Defensa (0 - 100)
	velocidad = models.IntegerField(max_length = 3, blank = False) # Velocidad (0 - 100)
	pases = models.IntegerField(max_length = 3, blank = False) # Pases (0 - 100)
	anotacion = models.IntegerField(max_length = 3, blank = False) # Anotación (0 - 100)
	portero = models.IntegerField(max_length = 3, blank = False) # Portero (0 - 100)

	# Habilidades físicas
	resistencia = models.IntegerField(max_length = 3, blank = False) # Moral (0 - 100)

	# Habilidades mentales
	agresividad = models.IntegerField(max_length = 3, blank = False) # Agresividad (0 - 100)
	concentracion = models.IntegerField(max_length = 3, blank = False) # Concentración (0 - 100)
	estabilidad = models.IntegerField(max_length = 3, blank = False) # Estabilidad (0 - 100)
	moral = models.IntegerField(max_length = 3, blank = False) # Moral (0 - 100)

	# Estado del jugador
	dias_lesionado = models.IntegerField(max_length = 3, default = 0, blank = False) # Total de días lesionado

	# Apariencia física
	altura = models.IntegerField(max_length = 3, blank = False) # Altura en cm.
	peso = models.IntegerField(max_length = 3, blank = False) # Peso en kg.
	color_piel = models.CharField(max_length = 30, blank = False) # Color de la piel
	color_pelo = models.CharField(max_length = 30, blank = False) # Color del pelo
	color_ojos = models.CharField(max_length = 30, blank = False) # Color de los ojos

	def __unicode__(self):
		return self.nombre

	def obtenerEdad(self):
		from datetime import date
		hoy = date.today()
		edad = hoy - self.fecha_nacimiento
		anios = (int)(edad.days / 365)
		dias = edad.days % 365
		return anios, dias

	def setAparienciaAleatoria(self):
		if self.sexo == 'M':
			self.altura = (randint(160, 200) + randint(160, 200)) / 2
			self.peso = (int) ((self.altura - 100) * (randint(8, 12) / 10.0))
		else:
			self.altura = (randint(155, 190) + randint(155, 190)) / 2
			self.peso = (int) ((self.altura - 110) * (randint(8, 12) / 10.0))

		# Color de la piel
		a = randint(1, 1000)
		if a <= 100:
			self.color_piel = "Blanca"
		elif a <= 200:
			self.color_piel = "Amarilla"
		elif a <= 700:
			self.color_piel = "Morena"
		elif a <= 900:
			self.color_piel = "Oscura"
		else:
			self.color_piel = "Negra"

		# Color del pelo
		a = randint(1, 1000)
		if a <= 250:
			self.color_pelo = "Negro"
		elif a <= 500:
			self.color_pelo = "Marrón oscuro"
		elif a <= 750:
			self.color_pelo = "Marrón claro"
		elif a <= 800:
			self.color_pelo = "Rojo"
		elif a <= 950:
			self.color_pelo = "Rubio"
		else:
			self.color_pelo = "Blanco"

		# Color de los ojos
		a = randint(1, 1000)
		if a <= 300:
			self.color_ojos = "Negros"
		elif a <= 600:
			self.color_ojos = "Marrones oscuros"
		elif a <= 850:
			self.color_ojos = "Marrones claros"
		elif a <= 900:
			self.color_ojos = "Verdes"
		elif a <= 950:
			self.color_ojos = "Grises"
		else:
			self.color_ojos = "Azules"

	def setHabilidadesAleatorias(self, posicion, nivel):
		# Habilidades de juego
		if (posicion == "DELANTERO"):
			self.ataque 	= randint((int)(nivel * 0.8), nivel)
			self.defensa 	= randint(0, (int)(nivel * 0.2))
			self.velocidad 	= randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.pases 		= randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.anotacion 	= randint((int)(nivel * 0.8), nivel)
			self.portero 	= randint(0, (int)(nivel * 0.2))

		elif (posicion == "CENTROCAMPISTA"):
			self.ataque 	= randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.defensa 	= randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.velocidad 	= randint((int)(nivel * 0.8), nivel)
			self.pases 		= randint((int)(nivel * 0.8), nivel)
			self.anotacion 	= randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.portero 	= randint(0, (int)(nivel * 0.2))

		elif (posicion == "DEFENSA"):
			self.ataque 	= randint(0, (int)(nivel * 0.2))
			self.defensa 	= randint((int)(nivel * 0.8), nivel)
			self.velocidad 	= randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.pases 		= randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.anotacion 	= randint(0, (int)(nivel * 0.2))
			self.portero 	= randint(0, (int)(nivel * 0.2))

		elif (posicion == "PORTERO"):
			self.ataque 	= randint(0, (int)(nivel * 0.2))
			self.defensa 	= randint(0, (int)(nivel * 0.2))
			self.velocidad 	= randint(0, (int)(nivel * 0.2))
			self.pases 		= randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.anotacion 	= randint(0, (int)(nivel * 0.2))
			self.portero 	= randint((int)(nivel * 0.8), nivel)

		else:
			self.ataque 	= randint(0, nivel)
			self.defensa 	= randint(0, nivel)
			self.velocidad 	= randint(0, nivel)
			self.pases 		= randint(0, nivel)
			self.anotacion 	= randint(0, nivel)
			self.portero 	= randint(0, nivel)

		# Habilidades físicas
		self.resistencia 	= randint(0, nivel)

		# Habilidades mentales
		self.agresividad 	= randint(0, 100)
		self.concentracion	= randint(0, 100)
		self.estabilidad 	= randint(0, 100)
		self.moral 			= 50

		return self

	def siglasPosicion(self):
		mejor_posicion = self.mejorPosicion();
		if mejor_posicion == 'PORTERO':
			return 'PO'
		elif mejor_posicion == 'DEFENSA':
			return 'DF'
		elif mejor_posicion == 'CENTROCAMPISTA':
			return 'CC'
		elif mejor_posicion == 'DELANTERO':
			return 'DL'
		else:
			return '-'

	def mejorPosicion(self):
		# Array donde se van a guardar las posiciones y sus valores según las habilidades del jugador
		posiciones = []

		portero = ["PORTERO", self.portero + (self.pases * 0.6)]
		posiciones.append(portero)

		defensa = ["DEFENSA", self.defensa + (((self.velocidad + self.pases) / 2.0) * 0.6)]
		posiciones.append(defensa)

		centrocampista = ["CENTROCAMPISTA", ((self.velocidad + self.pases) / 2.0) + (((self.ataque + self.defensa + self.anotacion) / 3.0) * 0.6)]
		posiciones.append(centrocampista)

		delantero = ["DELANTERO", ((self.ataque + self.anotacion) / 2.0) + (((self.velocidad + self.pases) / 2.0) * 0.6)]
		posiciones.append(delantero)

		num_posiciones = len(posiciones)

		# Obtener mejor posición
		mejor = posiciones[0][0]
		mejor_valor = posiciones[0][1]
		for pos in range(1, num_posiciones):
			if posiciones[pos][1] > mejor_valor:
				mejor = posiciones[pos][0]
				mejor_valor = posiciones[pos][1]

		return mejor

	def setNumero(self, numero):
		self.numero = numero

	def valorMercado(self):
		posicion = self.mejorPosicion()
		if (posicion == "PORTERO"):
			media_hab_principales = self.portero
			media_hab_secundarias = self.pases
			media_hab_poco_importantes = (self.ataque + self.defensa + self.velocidad + self.anotacion) / 4.0

		elif (posicion == "DEFENSA"):
			media_hab_principales = self.defensa
			media_hab_secundarias = (self.velocidad + self.pases) / 2.0
			media_hab_poco_importantes = (self.ataque + self.anotacion + self.portero) / 3.0

		elif (posicion == "CENTROCAMPISTA"):
			media_hab_principales = (self.velocidad + self.pases) / 2.0
			media_hab_secundarias = (self.ataque + self.defensa + self.anotacion) / 3.0
			media_hab_poco_importantes = self.portero

		elif (posicion == "DELANTERO"):
			media_hab_principales = (self.ataque + self.anotacion) / 2.0
			media_hab_secundarias = (self.velocidad + self.pases) / 2.0
			media_hab_poco_importantes = (self.defensa + self.portero) / 2.0

		else:
			media_hab_principales = 0
			media_hab_secundarias = 0
			media_hab_poco_importantes = 0

		return (int)((1.15 ** media_hab_principales) + (1.1 ** media_hab_secundarias) + (1.05 ** media_hab_poco_importantes))

########################################################################
