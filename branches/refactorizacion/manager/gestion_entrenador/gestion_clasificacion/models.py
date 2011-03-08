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

from gestion_entrenador.gestion_equipo.models import Equipo
from gestion_entrenador.gestion_jornada.models import Jornada

########################################################################

class ClasificacionEquipoJornada(models.Model):
	''' Representa una posicion de un equipo en una jornada '''
	jornada = models.ForeignKey(Jornada)
	equipo = models.ForeignKey(Equipo)
	goles_favor = models.IntegerField()
	goles_contra = models.IntegerField()
	puntos = models.IntegerField()

	def __unicode__(self):
		''' Devuelve una cadena de texto que representa la clase '''
		return self.equipo.nombre + " en jornada: " + str(self.jornada.numero) + " de liga: " + str(self.jornada.liga.id)

########################################################################

