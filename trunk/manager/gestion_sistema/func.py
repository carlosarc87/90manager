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
from django.db import transaction

########################################################################

@transaction.commit_manually()
def calcularCambios(request):
	""" Calcula los cambios realizados en una liga """
	liga = request.session['liga_actual']
	if liga.activada():
		fecha = liga.getFecha()
		# Calculos de subastas

		# Traspasos de jugadores
		# Tomar en cuenta alineaciones en las que se cambia un jugador

		# Avanzar Jornadas
		print "Analizando jornadas"
		jornadas_acabadas = liga.jornada_set.filter(jugada = False, fecha_fin__lt = liga.getFecha())
		for jornada in jornadas_acabadas:
			print "Avanzando jornada", jornada
			liga.avanzarJornada()

		# Jugar Partidos de esta jornada
		print "Analizando partidos acabados"
		partidos_acabados = liga.partido_set.filter(jugado = False, fecha_fin__lt = liga.getFecha())
		for partido in partidos_acabados:
			print "Jugando el partido", partido
			partido.jugar()

		print "Fin"
		#partidos_iniciados = liga.partido_set.filter(jugado = False, fecha_inicio__lt = liga.getFecha())
		# Iniciar partidos
		# bla bla bla
		# Comprobar subastas
		print "Analizando subastas"
		subastas = liga.subasta_set.filter(fecha_fin__lt = liga.getFecha())
		for subasta in subastas:
			subasta.finalizar()
			subasta.delete()
		transaction.commit()
		return True
	else:
		return False

########################################################################
