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

from gestion_sistema.gestion_calendario.models import Evento

from gestion_sistema.gestion_liga.models import Liga

########################################################################

# Jornada
class Jornada(Evento):
	''' Representa una jornada en el sistema '''
	numero = models.PositiveIntegerField()
	jugada = models.BooleanField(default = False)

	def obtenerClasificacionEquipo(self, equipo):
		''' Devuelve la posicion actual de un equipo en la jornada '''
		return self.clasificacionequipojornada_set.get(equipo = equipo)

	def quedanPartidosPorJugar(self):
		''' Devuelve si quedan partidos por jugar '''
		return self.partido_set.filter(jugado = False).count() > 0

	def generarClasificacion(self):
		''' Genera la clasificacion vacia de la jornada '''
		from gestion_sistema.gestion_clasificacion.models import ClasificacionEquipoJornada
		partidos = self.partido_set.all()
		if self.numero == 1: # Jornada 1
			for partido in partidos:
				clasificacion_local = ClasificacionEquipoJornada(jornada = self, equipo = partido.equipo_local, goles_favor = 0, goles_contra = 0, puntos = 0)
				clasificacion_visitante = ClasificacionEquipoJornada(jornada = self, equipo = partido.equipo_visitante, goles_favor = 0, goles_contra = 0, puntos = 0)

				clasificacion_local.save()
				clasificacion_visitante.save()
		else:
			for partido in partidos:
				jornada_anterior = self.liga.jornada_set.get(numero = self.numero - 1)
				clas_local_anterior = jornada_anterior.clasificacionequipojornada_set.get(equipo = partido.equipo_local)
				clas_visitante_anterior = jornada_anterior.clasificacionequipojornada_set.get(equipo = partido.equipo_visitante)

				clasificacion_local = ClasificacionEquipoJornada(jornada = self, equipo = partido.equipo_local, goles_favor = clas_local_anterior.goles_favor, goles_contra = clas_local_anterior.goles_contra, puntos = clas_local_anterior.puntos)
				clasificacion_visitante = ClasificacionEquipoJornada(jornada = self, equipo = partido.equipo_visitante, goles_favor = clas_visitante_anterior.goles_favor, goles_contra = clas_visitante_anterior.goles_contra, puntos = clas_visitante_anterior.puntos)

				clasificacion_local.save()
				clasificacion_visitante.save()

	def jugarPartidosRestantes(self):
		''' Juega todos los partidos de la jornada que no se han finalizado '''
		partidos = self.partido_set.all()
		for partido in partidos:
			if not partido.finalizado():
				partido.jugar()
		self.jugada = True
		self.save()

	def mantenerAlineaciones(self, jornada_anterior):
		''' Mantiene las alineaciones de los jugadores para los partidos de esta jornada '''
		# Cogemos los partidos que tengan algun equipo
		partidos = self.partido_set.exclude(equipo_local__usuario = None, equipo_visitante__usuario = None)
		for partido in partidos:
			if partido.equipo_local is not None:
				equipo = partido.equipo_local
				# Cogemos el partido que jugó la jornada anterior
				qs = jornada_anterior.partido_set.filter(equipo_local = equipo)
				if qs.count() > 0:
					partido_anterior = qs[0]
					alineacion_anterior = partido_anterior.alineacion_local
				else:
					qs = jornada_anterior.partido_set.filter(equipo_visitante = equipo)
					partido_anterior = qs[0]
					alineacion_anterior = partido_anterior.alineacion_visitante

				# Una vez que tenemos la alineacion, copiamos para esta
				partido.alineacion_local.copiarAlineacion(alineacion_anterior)
			if partido.equipo_visitante is not None:
				equipo = partido.equipo_visitante
				# Cogemos el partido que jugó la jornada anterior
				qs = jornada_anterior.partido_set.filter(equipo_local = equipo)
				if qs.count() > 0:
					partido_anterior = qs[0]
					alineacion_anterior = partido_anterior.alineacion_local
				else:
					qs = jornada_anterior.partido_set.filter(equipo_visitante = equipo)
					partido_anterior = qs[0]
					alineacion_anterior = partido_anterior.alineacion_visitante

				# Una vez que tenemos la alineacion, copiamos para esta
				partido.alineacion_visitante.copiarAlineacion(alineacion_anterior)
			partido.save()

	def __unicode__(self):
		return "Jornada %d de liga %d" % (self.numero, self.liga.id)

########################################################################
