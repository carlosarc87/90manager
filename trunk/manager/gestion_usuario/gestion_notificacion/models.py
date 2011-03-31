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

def getObjeto(conjunto, identificador):
	obj = None
	lista = conjunto.objects.filter(id = identificador)
	if lista.count() > 0:
		obj = lista[0]
	return obj

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
	LIGA_ACTIVADA             = 100

	SUBASTA_FINALIZADA        = 300
	SUBASTA_GANADA            = 301
	SUBASTA_SUPERADA          = 302
	SUBASTA_SUPERADA_COMPRADA = 303

	PARTIDO_FINALIZADO        = 400
	def getMensaje(self):
		''' Genera un mensaje dependiendo del tipo de la notificacion '''
		from func import TipoNotificacion
		from gestion_sistema.gestion_liga.models import Liga
		from gestion_sistema.gestion_partido.models import Partido
		from gestion_sistema.gestion_jugador.models import Jugador
		from gestion_mercado.gestion_subasta.models import Subasta

		msj = str(self.tipo) + " - No hay mensaje"

		if self.tipo == TipoNotificacion.LIGA_ACTIVADA:
			liga = Liga.objects.get(id = self.identificador)
			enlace = '<a href="/ligas/ver/%d/">' % self.identificador
			msj = "La liga %s%s</a> ha sido activada" % (enlace, liga.nombre)

		elif self.tipo == TipoNotificacion.SUBASTA_FINALIZADA:
			obj = getObjeto(Jugador, self.identificador)
			enlace = '<a href="/jugadores/ver/%d/">' % self.identificador
			msj = "Ha acabado la subasta por %s%s</a>" % (enlace, obj.apodo)

		elif self.tipo == TipoNotificacion.SUBASTA_GANADA:
			obj = getObjeto(Jugador, self.identificador)
			enlace = '<a href="/jugadores/ver/%d/">' % self.identificador
			msj = "Has ganado la subasta por %s%s</a>" % (enlace, obj.apodo)

		elif self.tipo == TipoNotificacion.SUBASTA_SUPERADA:
			obj = getObjeto(Subasta, self.identificador)
			if obj:
				enlace = '<a href="/mercado/subastas/ver/%d/">' % self.identificador
				msj = "Han superado tu puja en la subasta de %s%s</a>" % (enlace, obj.jugador.apodo)
			else:
				msj = "Han superado tu puja en una subasta que ya ha acabado"

		elif self.tipo == TipoNotificacion.SUBASTA_SUPERADA_COMPRADA:
			obj = getObjeto(Jugador, self.identificador)
			enlace = '<a href="/jugadores/ver/%d/">' % self.identificador
			msj = "Has comprado la subasta por %s%s</a>" % (enlace, obj.apodo)

		elif self.tipo == TipoNotificacion.PARTIDO_FINALIZADO:
			obj = getObjeto(Partido, self.identificador)
			enlace = '<a href="/partidos/ver/%d/">' % self.identificador
			msj = "Ha acabado el partido de la jornada %s%s</a>" % (enlace, obj.jornada.numero)

		return msj

########################################################################
