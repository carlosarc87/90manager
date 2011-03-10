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
	nombre = models.CharField(max_length = 200)
	num_equipos = models.IntegerField(null=True, default=0)
	publica = models.BooleanField(default=True) # Visibilidad de la liga

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

	def agregarEquipo(self, equipo):
		''' Agrega un equipo a la liga '''
		self.equipos_set.add(equipo)

	def __unicode__(self):
		''' Devuelve una cadena de texto que representa la clase '''
		return self.nombre

########################################################################
