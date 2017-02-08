# -*- coding: utf-8 -*-
"""
Copyright 2017 by
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

from django.core.validators import MaxValueValidator
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

	# Apariencia física
	color_piel = models.CharField(max_length = 30) # Color de la piel
	color_pelo = models.CharField(max_length = 30) # Color del pelo
	color_ojos = models.CharField(max_length = 30) # Color de los ojos

	def generarAtributos(self, equipo, numero, posicion, max_nivel):
		''' Genera una instancia relacionada de atributos '''
		atributos = AtributosVariablesJugador(jugador = self, equipo = equipo, numero = numero)
		atributos.setNumero(numero)
		atributos.setHabilidadesAleatorias(posicion, max_nivel)

		return atributos

	def __unicode__(self):
		return self.nombre

	def setEquipo(self, equipo):
		self.atributos.equipo = equipo

	def getEdad(self):
		from datetime import date
		
		if self.atributos.equipo.liga.activada():
			fecha_actual_liga = self.atributos.equipo.liga.getFecha()
		else:
			fecha_actual_liga = self.atributos.equipo.liga.fecha_ficticia_inicio
			
		edad = fecha_actual_liga.date() - self.fecha_nacimiento
		anios = (int)(edad.days / 365.25)
		dias = (int)(edad.days % 365.25)
		
		return anios, dias

	def setAparienciaAleatoria(self):
		if self.sexo == 'M':
			self.atributos.altura = (int)((randint(160, 200) + randint(160, 200)) / 2)
			self.atributos.peso = (int)((self.atributos.altura - 100) * (randint(8, 12) / 10.0))
		else:
			self.atributos.altura = (int)((randint(150, 190) + randint(150, 190)) / 2)
			self.atributos.peso = (int)((self.atributos.altura - 110) * (randint(8, 12) / 10.0))

		# Color de la piel
		a = randint(1, 1000)
		if a <= 100:
			self.color_piel = "blanca"
		elif a <= 350:
			self.color_piel = "clara"
		elif a <= 700:
			self.color_piel = "morena"
		elif a <= 900:
			self.color_piel = "oscura"
		else:
			self.color_piel = "negra"

		# Color del pelo
		a = randint(1, 1000)
		if a <= 300:
			self.color_pelo = "negro"
		elif a <= 750:
			self.color_pelo = "marron"
		elif a <= 800:
			self.color_pelo = "rojo"
		elif a <= 950:
			self.color_pelo = "rubio"
		else:
			self.color_pelo = "blanco"

		# Color de los ojos
		a = randint(1, 1000)
		if a <= 300:
			self.color_ojos = "negros"
		elif a <= 850:
			self.color_ojos = "marrones"
		elif a <= 900:
			self.color_ojos = "verdes"
		elif a <= 950:
			self.color_ojos = "grises"
		else:
			self.color_ojos = "azules"

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
		
		return '-'

	def mejorPosicion(self):
		return self.atributos.mejorPosicion()

	def setNumero(self, numero):
		self.atributos.setNumero(numero)

	def getNivel(self, posicion = None):
		return self.atributos.getNivel(posicion)

	def valorMercado(self, posicion = None):
		return self.atributos.valorMercado(posicion)

	def setHabilidadesAleatorias(self, posicion, nivel):
		return self.atributos.setHabilidadesAleatorias(posicion, nivel)


########################################################################

class AtributosVariablesJugador(models.Model):
	''' Representa los atributos que pueden cambiar de un jugador a lo largo del tiempo '''
	# Datos equipo
	equipo = models.ForeignKey(Equipo) # Equipo al que pertenece
	jugador = models.OneToOneField(Jugador, related_name = 'atributos') # Jugador al que pertenecen

	numero = models.PositiveIntegerField(validators=[MaxValueValidator(99)], null = True) # Dorsal en el equipo (0 - 99)
	ofertado = models.BooleanField(default = False) # Indica si está o no en la lista de jugadores transferibles

	# Habilidades de campo
	ataque = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default = 0) # Ataque (0 - 100)
	defensa = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default = 0) # Defensa (0 - 100)
	velocidad = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default = 0) # Velocidad (0 - 100)
	pases = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default = 0) # Pases (0 - 100)
	anotacion = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default = 0) # Anotación (0 - 100)
	portero = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default = 0) # Portero (0 - 100)

	# Habilidades físicas
	resistencia = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default = 0) # Moral (0 - 100)

	# Habilidades mentales
	agresividad = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default = 0) # Agresividad (0 - 100)
	concentracion = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default = 0) # Concentración (0 - 100)
	estabilidad = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default = 0) # Estabilidad (0 - 100)
	moral = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default = 0) # Moral (0 - 100)

	# Atributos físicos
	altura = models.PositiveIntegerField(validators=[MaxValueValidator(300)], default = 0) # Altura en cm.
	peso = models.PositiveIntegerField(validators=[MaxValueValidator(200)], default = 0) # Peso en kg.

	# Para que no salgan habilidades con valor 0 el nivel debería ser al menos 10.
	def setHabilidadesAleatorias(self, posicion, nivel):
		# Habilidades de juego
		if (posicion == "DELANTERO"):
			self.ataque 	= randint((int)(nivel * 0.8), nivel)
			self.defensa 	= randint(1, (int)(nivel * 0.5))
			self.velocidad 	= randint((int)(nivel * 0.5), nivel)
			self.pases 		= randint((int)(nivel * 0.5), (int)(nivel * 0.7))
			self.anotacion 	= randint((int)(nivel * 0.5), nivel)
			self.portero 	= randint(1, (int)(nivel * 0.5))

		elif (posicion == "CENTROCAMPISTA"):
			self.ataque 	= randint((int)(nivel * 0.5), (int)(nivel * 0.7))
			self.defensa 	= randint((int)(nivel * 0.5), (int)(nivel * 0.7))
			self.velocidad 	= randint((int)(nivel * 0.5), nivel)
			self.pases 		= randint((int)(nivel * 0.8), nivel)
			self.anotacion 	= randint((int)(nivel * 0.5), nivel)
			self.portero 	= randint(1, (int)(nivel * 0.5))

		elif (posicion == "DEFENSA"):
			self.ataque 	= randint(1, (int)(nivel * 0.5))
			self.defensa 	= randint((int)(nivel * 0.8), nivel)
			self.velocidad 	= randint((int)(nivel * 0.5), nivel)
			self.pases 		= randint((int)(nivel * 0.5), (int)(nivel * 0.7))
			self.anotacion 	= randint(1, (int)(nivel * 0.5))
			self.portero 	= randint(1, (int)(nivel * 0.5))

		elif (posicion == "PORTERO"):
			self.ataque 	= randint(1, (int)(nivel * 0.5))
			self.defensa 	= randint(1, (int)(nivel * 0.5))
			self.velocidad 	= randint((int)(nivel * 0.5), nivel)
			self.pases 		= randint((int)(nivel * 0.5), (int)(nivel * 0.7))
			self.anotacion 	= randint(1, (int)(nivel * 0.5))
			self.portero 	= randint((int)(nivel * 0.8), nivel)

		else:
			self.ataque 	= randint(1, nivel)
			self.defensa 	= randint(1, nivel)
			self.velocidad 	= randint(1, nivel)
			self.pases 		= randint(1, nivel)
			self.anotacion 	= randint(1, nivel)
			self.portero 	= randint(1, nivel)

		# Habilidades físicas
		self.resistencia 	= randint(1, nivel)

		# Habilidades mentales
		self.agresividad 	= randint(1, 100)
		self.concentracion	= randint(1, 100)
		self.estabilidad 	= randint(1, 100)
		self.moral 			= randint(1, 100)

		return self

	def mejorPosicion(self):
		# Array donde se van a guardar las posiciones y sus valores según las habilidades del jugador
		posiciones = []
		
		# PORTERO
		portero = ["PORTERO", self.getNivel("PORTERO")]
		posiciones.append(portero)

		# DEFENSA
		defensa = ["DEFENSA", self.getNivel("DEFENSA")]
		posiciones.append(defensa)

		# CENTROCAMPISTA
		centrocampista = ["CENTROCAMPISTA", self.getNivel("CENTROCAMPISTA")]
		posiciones.append(centrocampista)
		
		# DELANTERO
		delantero = ["DELANTERO", self.getNivel("DELANTERO")]
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

	def getNivel(self, posicion = None):
		if not posicion:
			posicion = self.mejorPosicion()

		if posicion == "PORTERO":
			media_hab_principales = self.portero
			media_hab_secundarias = self.pases
			media_hab_poco_importantes = (self.ataque + self.defensa + self.velocidad + self.anotacion) / 4.0

		elif posicion == "DEFENSA":
			media_hab_principales = self.defensa
			media_hab_secundarias = (self.velocidad + self.pases) / 2.0
			media_hab_poco_importantes = (self.ataque + self.anotacion + self.portero) / 3.0

		elif posicion == "CENTROCAMPISTA":
			media_hab_principales = self.pases
			media_hab_secundarias = (self.ataque + self.defensa + self.velocidad + self.anotacion) / 4.0
			media_hab_poco_importantes = self.portero

		elif posicion == "DELANTERO":
			media_hab_principales = self.ataque
			media_hab_secundarias = (self.velocidad + self.pases + self.anotacion) / 3.0
			media_hab_poco_importantes = (self.defensa + self.portero) / 2.0

		else:
			media_hab_principales = 0
			media_hab_secundarias = 0
			media_hab_poco_importantes = 0

		return (int)((0.8 * media_hab_principales) + (0.15 * media_hab_secundarias) + (0.05 * media_hab_poco_importantes))
	
	def coeficienteJuventud(self, edad):
		coeficiente = 1 - (abs(edad - 23) / 10)
		
		if coeficiente < 0:
			coeficiente = 0
		
		return coeficiente
		
	def coeficientePosicion(self, posicion):
		coeficiente = 0.5
		
		if posicion == "CENTROCAMPISTA":
			coeficiente = 0.75
		elif posicion == "DELANTERO":
			coeficiente = 1
		
		return coeficiente
		
	def calidadFutbolistica(self, nivel, coeficiente_posicion):
		# Valor de nivel (0 = segunda division - 10 = mejor del mundo)
		valor_nivel = (nivel - 60) / 4
		
		if valor_nivel < 0:
			valor_nivel = 0.000005 * nivel
		
		# Devolver un valor de 0 a 10
		return (valor_nivel * coeficiente_posicion) / 10
		
	def valorImagenFisica(self, nivel):
		# De momento no hay atributos físicos suficientes para establecer otros valores
		# Devolver un valor de 0 a 2
		v = 1.2
		return ((v ** nivel) / (v ** 100)) * 2
		
	def valorEspectacularidad(self, nivel):
		# De momento no hay atributos suficientes para establecer otros valores
		# Devolver un valor de 0 a 2
		v = 1.2
		return ((v ** nivel) / (v ** 100)) * 2
		
	def valorLogrosDeportivos(self, nivel):
		# De momento no hay atributos suficientes para establecer otros valores
		# Devolver un valor de 0 a 2
		v = 1.2
		return ((v ** nivel) / (v ** 100)) * 2
		
	def valorPopularidadPaisOrigen(self, nivel):
		# De momento no hay atributos suficientes para establecer otros valores
		# Devolver un valor de 0 a 2
		v = 1.2
		return ((v ** nivel) / (v ** 100)) * 2
		
	def valorMediatico(self, CF, nivel):
		CF = CF * 0.4
		FIS = self.valorImagenFisica(nivel)
		ESP = self.valorEspectacularidad(nivel)
		DEP = self.valorLogrosDeportivos(nivel)
		NAC = self.valorPopularidadPaisOrigen(nivel)
		
		valor_mediatico = (CF + FIS + ESP + DEP + NAC) / 10
		
		return valor_mediatico
	
	# Cálculos obtenidos de: http://futbolfinanzas.com/calculo-del-valor-de-mercado-de-los-futbolistas-de-elite/
	def valorMercado(self, posicion = None):
		if not posicion:
			posicion = self.mejorPosicion()

		max_valor_mercado = 100000000 # Máximo valor del mercado
		anios, dias = self.jugador.getEdad()
		nivel = self.getNivel(posicion)
		
		CJ = self.coeficienteJuventud(anios)
		CP = self.coeficientePosicion(posicion)
		CF = self.calidadFutbolistica(nivel, CP)
		VM = self.valorMediatico(CF, nivel)
		
		valor_mercado = (int)((CJ * (CF * (max_valor_mercado / 2))) + (VM * (max_valor_mercado / 2)))
		
		return valor_mercado

	def clone(self):
		''' Devuelve una copia de si mismo '''
		from django.db.models import AutoField
		obj = self
		initial = dict([(f.name, getattr(obj, f.name))
					for f in obj._meta.fields
					if not isinstance(f, AutoField) and\
						not f in list(obj._meta.parents.values())])
		return obj.__class__(**initial)

########################################################################
