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
from gestion_sistema.gestion_liga.models import Liga

########################################################################

# Notificacion
class Notificacion(models.Model):
	''' Representa una notificacion de algun elemento de una liga para un usuario '''
	# Usuario notificado
	usuario = models.ForeignKey(Usuario)
	# Liga (en su caso) desde la que se envia la notificacion
	liga = models.ForeignKey(Liga, null = True, blank = True)
	# Tipo de notificacion
	tipo = models.PositiveIntegerField(default = 0)
	# Id a la que redirecciona (segun el tipo de notificacion sera de tipo partido o subasta, etc
	identificador = models.PositiveIntegerField()
	# Indica que se ha leido la notificacion
	leida = models.BooleanField(default = False)
	# Fecha real de emision de la notificacion
	fecha_emision = models.DateTimeField()

	def getMensaje(self):
		''' Genera un mensaje dependiendo del tipo de la notificacion '''
		from func import TipoNotificacion
		return "Tipo: " + str(self.tipo)

########################################################################
