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

from gestion_sistema.gestion_equipo.models import Equipo
from gestion_sistema.gestion_liga.models import Liga
from gestion_sistema.gestion_jugador.models import AtributosVariablesJugador

########################################################################

# Subasta
class Subasta(models.Model):
	''' Representa una subasta de un jugador en el sistema '''
	# Datos principales
	oferta = models.PositiveIntegerField(default = 0)
	precio_compra = models.PositiveIntegerField(null = True, blank = True)
	expira = models.PositiveIntegerField(default = 1)
	estado = models.PositiveIntegerField(max_length = 1, default = 0)

	vendedor = models.ForeignKey(Equipo, related_name = 'subastas_como_vendedor')
	comprador = models.ForeignKey(Equipo, related_name = 'subastas_como_comprador', null = True, blank = True)

	# Atributos del jugador que se subasta
	atributos_jugador = models.OneToOneField(AtributosVariablesJugador)

	liga = models.ForeignKey(Liga)

########################################################################