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

from gestion_entrenador.gestion_liga.models import Liga

########################################################################

# Jornada
class Jornada(models.Model):
	''' Representa una jornada en el sistema '''
	numero = models.IntegerField()
	#fecha = models.DateField("Fecha")
	liga = models.ForeignKey(Liga)
	jugada = models.BooleanField()

	def obtenerClasificacion(self):
		''' Obtiene la clasificacion de la jornada '''
		if self.jugada:
			clasificaciones = []
			partidos = self.partido_set.all()
			if self.numero == 0: # Jornada 0
				for partido in partidos:
					clasificacion_local = ClasificacionEquipoJornada(jornada = self, equipo = partido.equipo_local, goles_favor = partido.goles_local, goles_contra = partido.goles_visitante, puntos = 0)
					clasificacion_visitante = ClasificacionEquipoJornada(jornada = self, equipo = partido.equipo_visitante, goles_favor = partido.goles_visitante, goles_contra = partido.goles_local, puntos = 0)
					if (partido.goles_local > partido.goles_visitante):
						clasificacion_local.puntos = 3
					elif (partido.goles_local < partido.goles_visitante):
						clasificacion_visitante.puntos = 3
					else:
						clasificacion_local.puntos = 1
						clasificacion_visitante.puntos = 1

					clasificacion_local.save()
					clasificacion_visitante.save()
					#print clasificacion_local.puntos
			else:
				for partido in partidos:
					jornada_anterior = self.liga.jornada_set.get(numero = self.numero - 1)
					clas_local_anterior = jornada_anterior.clasificacionequipojornada_set.get(equipo = partido.equipo_local)
					clas_visitante_anterior = jornada_anterior.clasificacionequipojornada_set.get(equipo = partido.equipo_visitante)

					clasificacion_local = ClasificacionEquipoJornada(jornada = self, equipo = partido.equipo_local, goles_favor = clas_local_anterior.goles_favor + partido.goles_local, goles_contra = clas_local_anterior.goles_contra + partido.goles_visitante, puntos = clas_local_anterior.puntos)
					clasificacion_visitante = ClasificacionEquipoJornada(jornada = self, equipo = partido.equipo_visitante, goles_favor = clas_visitante_anterior.goles_favor + partido.goles_visitante, goles_contra = clas_visitante_anterior.goles_contra + partido.goles_local, puntos = clas_visitante_anterior.puntos)
					if (partido.goles_local > partido.goles_visitante):
						clasificacion_local.puntos += 3
					elif (partido.goles_local < partido.goles_visitante):
						clasificacion_visitante.puntos += 3
					else:
						clasificacion_local.puntos += 1
						clasificacion_visitante.puntos += 1

					clasificacion_local.save()
					clasificacion_visitante.save()

			return True
		else:
			return False

	def __unicode__(self):
		return "Jornada %d de liga %d" % (self.numero, self.liga.id)

########################################################################
