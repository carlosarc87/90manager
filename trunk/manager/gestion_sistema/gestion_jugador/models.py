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
	nombre = models.CharField(max_length = 80)
	apodo = models.CharField(max_length = 30)
	equipo = models.ForeignKey(Equipo)

	numero = models.IntegerField(null = True, blank = True)

	ataque = models.IntegerField(null = False, blank = False)
	defensa = models.IntegerField(null = False, blank = False)
	velocidad = models.IntegerField(null = False, blank = False)
	pases = models.IntegerField(null = False, blank = False)
	anotacion = models.IntegerField(null = False, blank = False)
	portero = models.IntegerField(null = False, blank = False)

	transferible = models.BooleanField()

	def __unicode__(self):
		return self.nombre

	def setHabilidadesAleatorias(self, posicion, nivel):
		if (posicion == "DELANTERO"):
			self.ataque = randint((int)(nivel * 0.8), nivel)
			self.defensa = randint(0, (int)(nivel * 0.2))
			self.velocidad = randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.pases = randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.anotacion = randint((int)(nivel * 0.8), nivel)
			self.portero = randint(0, (int)(nivel * 0.2))

		elif (posicion == "CENTROCAMPISTA"):
			self.ataque = randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.defensa = randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.velocidad = randint((int)(nivel * 0.8), nivel)
			self.pases = randint((int)(nivel * 0.8), nivel)
			self.anotacion = randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.portero = randint(0, (int)(nivel * 0.2))

		elif (posicion == "DEFENSA"):
			self.ataque = randint(0, (int)(nivel * 0.2))
			self.defensa = randint((int)(nivel * 0.8), nivel)
			self.velocidad = randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.pases = randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.anotacion = randint(0, (int)(nivel * 0.2))
			self.portero = randint(0, (int)(nivel * 0.2))

		elif (posicion == "PORTERO"):
			self.ataque = randint(0, (int)(nivel * 0.2))
			self.defensa = randint(0, (int)(nivel * 0.2))
			self.velocidad = randint(0, (int)(nivel * 0.2))
			self.pases = randint((int)(nivel * 0.4), (int)(nivel * 0.6))
			self.anotacion = randint(0, (int)(nivel * 0.2))
			self.portero = randint((int)(nivel * 0.8), nivel)

		else:
			self.ataque = randint(0, nivel)
			self.defensa = randint(0, nivel)
			self.velocidad = randint(0, nivel)
			self.pases = randint(0, nivel)
			self.anotacion = randint(0, nivel)
			self.portero = randint(0, nivel)

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
