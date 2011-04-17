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
from gestion_sistema.gestion_jugador.models import AtributosVariablesJugador
from gestion_sistema.gestion_jornada.models import Jornada
from gestion_sistema.gestion_clasificacion.models import ClasificacionEquipoJornada
from gestion_usuario.gestion_notificacion.func import notificar, TipoNotificacion

from random import randint
from func import probabilidadExito

POSICIONES = (
	('BA', 'BANQUILLO'),
	('PO', 'PORTERO'),
	('DF', 'DEFENSA'),
	('CC', 'CENTROCAMPISTA'),
	('DL', 'DELANTERO'),
)

########################################################################

class JugadorPartido(models.Model):
	''' Representa los atributos de un jugador en un partido '''
	# Datos principales
	atributos = models.ForeignKey(AtributosVariablesJugador)
	posicion = models.CharField(max_length = 2, choices = POSICIONES)

	def __unicode__(self):
		''' Devuelve una cadena representativa del objeto '''
		return self.posicion + " - " + self.jugador.nombre

########################################################################

class AlineacionEquipo(models.Model):
	''' Representa la alineación de un equipo en un partido '''
	equipo = models.ForeignKey(Equipo)
	jugadores = models.ManyToManyField(JugadorPartido, null = True, blank = True)

	def borrarAlineacion(self):
		''' Elimina la alineacion actual '''
		for jugador in self.jugadores.all():
			jugador.delete()

	def setAlineacion(self, portero, defensas, centrocampistas, delanteros, suplentes):
		''' Establece una alineacion de jugadores a partir de los ids '''
		self.borrarAlineacion()

		atributos = self.equipo.atributosvariablesjugador_set.get(jugador__id = portero)
		p = JugadorPartido(atributos = atributos, posicion = 'PO')
		p.save()
		self.jugadores.add(p)

		for id_jugador in defensas:
			atributos = self.equipo.atributosvariablesjugador_set.get(jugador__id = id_jugador)
			p = JugadorPartido(atributos = atributos, posicion = 'DF')
			p.save()
			self.jugadores.add(p)

		for id_jugador in centrocampistas:
			atributos = self.equipo.atributosvariablesjugador_set.get(jugador__id = id_jugador)
			p = JugadorPartido(atributos = atributos, posicion = 'CC')
			p.save()
			self.jugadores.add(p)

		for id_jugador in delanteros:
			atributos = self.equipo.atributosvariablesjugador_set.get(jugador__id = id_jugador)
			p = JugadorPartido(atributos = atributos, posicion = 'DL')
			p.save()
			self.jugadores.add(p)

		for id_jugador in suplentes:
			atributos = self.equipo.atributosvariablesjugador_set.get(jugador__id = id_jugador)
			p = JugadorPartido(atributos = atributos, posicion = 'BA')
			p.save()
			self.jugadores.add(p)

	def copiarAlineacion(self, alineacion):
		''' Copia la alineacion desde otra alineacion '''
		self.borrarAlineacion()
		for jugador in alineacion.jugadores.all():
			j = JugadorPartido(atributos = jugador.atributos, posicion = jugador.posicion)
			j.save()
			self.jugadores.add(j)


	def getTitulares(self):
		''' Devuelve los jugadores titulares '''
		datos = self.getDatosTitulares()
		lista = []
		for dato in datos:
			jugador = dato.atributos.jugador
			lista.append(jugador)
		return lista

	def getSuplentes(self):
		''' Devuelve los jugadores suplentes '''
		datos = self.getDatosSuplentes()
		lista = []
		for dato in datos:
			jugador = dato.atributos.jugador
			lista.append(jugador)
		return lista

	def getDelanteros(self):
		''' Devuelve los delanteros del equipo '''
		lista = self.jugadores.filter(posicion = 'DL')
		if len(lista) > 0:
			return lista
		return None

	def getCentrocampistas(self):
		''' Devuelve los centrocampistas del equipo '''
		lista = self.jugadores.filter(posicion = 'CC')
		if len(lista) > 0:
			return lista
		return None

	def getDefensas(self):
		''' Devuelve los defensas del equipo '''
		lista = self.jugadores.filter(posicion = 'DF')
		if len(lista) > 0:
			return lista
		return None

	def getPortero(self):
		''' Devuelve al portero del equipo '''
		lista = self.jugadores.filter(posicion = 'PO')
		if len(lista) > 0:
			return lista[0]
		return None

	#def getSuplentes(self):
		#''' Devuelve los suplentes del equipo '''
		#lista = self.jugadores.filter(posicion = 'BA')
		#if len(lista) > 0:
			#return lista
		#return None

	def getDatosTitulares(self):
		''' Devuelve los datos de los titulares '''
		return self.jugadores.all().exclude(posicion = 'BA')

	def getDatosSuplentes(self):
		''' Devuelve los datos de los suplentes '''
		return self.jugadores.filter(posicion = 'BA')

	def setAleatoria(self):
		jugadores_equipo = self.equipo.atributosvariablesjugador_set.all()
		jugadores_equipo = sorted(jugadores_equipo, key = lambda atributosvariablesjugador : atributosvariablesjugador.valorMercado(), reverse = True)

		# Listas para guardar jugadores por posición y poder obtener luego los mejores
		lista_PO = []
		lista_DF = []
		lista_CC = []
		lista_DL = []
		for jug in jugadores_equipo:
			# Añadir el jugador a una lista dependiendo de su posición
			if jug.mejorPosicion() == 'PORTERO':
				lista_PO.append(jug)
			if jug.mejorPosicion() == 'DEFENSA':
				lista_DF.append(jug)
			if jug.mejorPosicion() == 'CENTROCAMPISTA':
				lista_CC.append(jug)
			if jug.mejorPosicion() == 'DELANTERO':
				lista_DL.append(jug)

		# Comprobar qué formación es con la que el equipo tiene mejor valor
		# 1 PO, 3-5 DF, 2-5 CC, 1-5 DL
		#max_DF = 5
		#max_CC = 5
		#max_DL = 5

		#mejor = []

		# De momento poner una 4-4-2 con los jugadores que haya
		if len(lista_PO) > 0:
			jugador = JugadorPartido(atributos = lista_PO.pop(0), posicion = 'PO')
			jugador.save()
			self.jugadores.add(jugador)

		for i in range(0, 4):
			if len(lista_DF) > 0:
				jugador = JugadorPartido(atributos = lista_DF.pop(0), posicion = 'DF')
				jugador.save()
				self.jugadores.add(jugador)

		for i in range(0, 4):
			if len(lista_CC) > 0:
				jugador = JugadorPartido(atributos = lista_CC.pop(0), posicion = 'CC')
				jugador.save()
				self.jugadores.add(jugador)

		for i in range(0, 2):
			if len(lista_DL) > 0:
				jugador = JugadorPartido(atributos = lista_DL.pop(0), posicion = 'DL')
				jugador.save()
				self.jugadores.add(jugador)

		# Colocar DF
		#for DF in range(3, max_DF + 1):
			#alineacion = []
			#for i in range(0, DF):
				#mejor.append(defensas)

			#num_jug_colocados = 1 + DF

			## Colocar CC
			#for CC in range(2, max_CC + 1):
				#num_jug_colocados += CC

				## Calcular máximo de DL que se pueden colocar
				#DL = 11 - num_jug_colocados

				## Colocar DL
				#print DF + '-' + CC + '-' + DL + ' = ' + valor_alineacion

					# Calcular valor de la alineación


	def estaPreparada(self):
		return len(self.jugadores.all()) > 0

	def getValorAtaque(self):
		valor = 0
		titulares = self.getDatosTitulares()
		for t in titulares:
			posicion = t.posicion
			ataque = t.atributos.ataque

			if(posicion == "DF"):
				valor += (ataque * 0.25)
			elif(posicion == "CC"):
				valor += (ataque * 0.75)
			elif(posicion == "DL"):
				valor += ataque

		if len(titulares) == 0:
			return 0
		return (int)(valor / len(titulares))

	def getValorDefensa(self):
		valor = 0
		titulares = self.getDatosTitulares()
		for t in titulares:
			posicion = t.posicion
			defensa = t.atributos.defensa

			if(posicion == "DF"):
				valor += defensa
			elif(posicion == "CC"):
				valor += (defensa * 0.75)
			elif(posicion == "DL"):
				valor += (defensa * 0.25)

		if len(titulares) == 0:
			return 0
		return (int)(valor / len(titulares))

	def getValorPases(self):
		valor = 0
		titulares = self.getDatosTitulares()
		for t in titulares:
			posicion = t.posicion
			pases = t.atributos.pases
			if(posicion == "DF"):
				valor += (pases * 0.5)
			elif(posicion == "CC"):
				valor += pases
			elif(posicion == "DL"):
				valor += (pases * 0.5)

		if len(titulares) == 0:
			return 0
		return (int)(valor / len(titulares))

	def getValorVelocidad(self):
		valor = 0
		titulares = self.getDatosTitulares()
		for t in titulares:
			posicion = t.posicion
			velocidad = t.atributos.velocidad
			if(posicion == "DF"):
				valor += (velocidad * 0.5)
			elif(posicion == "CC"):
				valor += velocidad
			elif(posicion == "DL"):
				valor += (velocidad * 0.5)

		if len(titulares) == 0:
			return 0
		return (int)(valor / len(titulares))

	def getValorAnotacion(self):
		valor = 0
		titulares = self.getDatosTitulares()
		for t in titulares:
			posicion = t.posicion
			anotacion = t.atributos.anotacion
			if(posicion == "DF"):
				valor += (int)(anotacion * 0.25)
			elif(posicion == "CC"):
				valor += (int)(anotacion * 0.75)
			elif(posicion == "DL"):
				valor += anotacion

		if len(titulares) == 0:
			return 0
		return (int)(valor / len(titulares))

	def getValorPortero(self):
		valor = 0
		titulares = self.getDatosTitulares()
		for t in titulares:
			posicion = t.posicion

			if(posicion == "PO"):
				return t.atributos.portero

		return 0

	def getValorMoral(self):
		valor = 0
		titulares = self.getDatosTitulares()
		for t in titulares:
			valor += t.atributos.moral

		if len(titulares) == 0:
			return 0
		return (int)(valor / len(titulares))

########################################################################

# Partido
class Partido(models.Model):
	''' Representa un partido en el sistema '''
	#hora_inicio = models.TimeField("Hora de inicio")
	jornada = models.ForeignKey(Jornada)
	equipo_local = models.ForeignKey(Equipo, related_name = "Local")
	equipo_visitante = models.ForeignKey(Equipo, related_name = "Visitante")

	alineacion_local = models.ForeignKey(AlineacionEquipo, related_name = "AlineacionLocal")
	alineacion_visitante = models.ForeignKey(AlineacionEquipo, related_name = "AlineacionVisitante")

	goles_local = models.PositiveIntegerField(null = True, blank = True)
	goles_visitante = models.PositiveIntegerField(null = True, blank = True)

	jugado = models.BooleanField(default = False)

	def __init__(self, *args, **kwargs):
		super(Partido, self).__init__(*args, **kwargs)
		if not self.alineacion_local_id:
			self.alineacion_local = AlineacionEquipo(equipo = self.equipo_local)
			self.alineacion_visitante = AlineacionEquipo(equipo = self.equipo_visitante)
			self.alineacion_local.save()
			self.alineacion_visitante.save()
			self.alineacion_local_id = self.alineacion_local.id
			self.alineacion_visitante_id = self.alineacion_visitante.id

	def finalizado(self):
		''' Indica si un partido ya ha acabado '''
		return self.jugado

	def jugar(self):
		''' Juega el partido '''
		num_goles = [0, 0]

		if not self.alineacion_local.estaPreparada():
			self.alineacion_local.setAleatoria()

		if not self.alineacion_visitante.estaPreparada():
			self.alineacion_visitante.setAleatoria()

		# Obtener alineaciones de los 2 equipos
		alineacion_local = self.alineacion_local
		alineacion_visitante = self.alineacion_visitante

		# Obtener jugadores titulares y suplentes de los 2 equipos
		titulares_local = self.alineacion_local.getDatosTitulares()
		suplentes_local = self.alineacion_local.getDatosSuplentes()
		titulares_visitante = self.alineacion_visitante.getDatosTitulares()
		suplentes_visitante = self.alineacion_visitante.getDatosSuplentes()

		alineacion = [alineacion_local, alineacion_visitante]

		num_parte = 1 # Parte de partido que se está jugando

		# Inicializar variables para el partido
		# --------------------------------------
		# Se incrementa un 10% la moral de los locales
		moral = [(1 + ((alineacion[0].getValorMoral() - 50) / 500.0))  * 1.1, 1 + ((alineacion[1].getValorMoral() - 50) / 500.0)]

		ataque = [(int) (alineacion[0].getValorAtaque() * moral[0]), (int) (alineacion[1].getValorAtaque() * moral[1])]
		defensa = [(int) (alineacion[0].getValorDefensa() * moral[0]), (int) (alineacion[1].getValorDefensa() * moral[1])]
		pases = [(int) (alineacion[0].getValorPases() * moral[0]), (int) (alineacion[1].getValorPases() * moral[1])]
		velocidad = [(int) (alineacion[0].getValorVelocidad() * moral[0]), (int) (alineacion[1].getValorVelocidad() * moral[1])]
		anotacion = [(int) (alineacion[0].getValorAnotacion() * moral[0]), (int) (alineacion[1].getValorAnotacion() * moral[1])]
		portero = [(int) (alineacion[0].getValorPortero() * moral[0]), (int) (alineacion[1].getValorPortero() * moral[1])]

		# --------------------------------------

		los_gatos_nos_dominaran = True
		if not los_gatos_nos_dominaran:
			print "-------------------------------------------"
			print alineacion[0].equipo.nombre
			print "Ataque: " + str(ataque[0])
			print "Defensa: " + str(defensa[0])
			print "Pases: " + str(pases[0])
			print "Velocidad: " + str(velocidad[0])
			print "Anotacion: " + str(anotacion[0])
			print "Portero: " + str(portero[0])
			print "-------------------------------------------"
			print alineacion[1].equipo.nombre
			print "Ataque: " + str(ataque[1])
			print "Defensa: " + str(defensa[1])
			print "Pases: " + str(pases[1])
			print "Velocidad: " + str(velocidad[1])
			print "Anotacion: " + str(anotacion[1])
			print "Portero: " + str(portero[1])
			print "-------------------------------------------"

		# Continuar jugando mientras no se hayan acabado las 2 partes del partido
		while(num_parte <= 2):
			# Establecer equipo que comienza a jugar la parte
			if(num_parte == 1):
				# Sortear equipo que comienza
				equipo_comienza = randint(0, 1)
				id_equipo_atacante = equipo_comienza
				segundos_jugados = 0
			else:
				if(equipo_comienza == 0): id_equipo_atacante = 1
				else: id_equipo_atacante = 0
				segundos_jugados = 45 * 60

			if id_equipo_atacante == 0:
				equipo_suceso = self.equipo_local
			else:
				equipo_suceso = self.equipo_visitante

			texto = "Equipo comienza"
			#print texto
			suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
			self.suceso_set.add(suceso)

			# Iniciar variables
			seg_restantes = 45 * 60
			seg_descuento = 0
			tiempo_descuento = False

			# Continuar jugando mientras no se haya acabado todo el tiempo de la parte actual
			while(seg_restantes > 0):
				# Establecer id del defensor
				if(id_equipo_atacante == 0): id_equipo_defensor = 1
				else: id_equipo_defensor = 0

				if id_equipo_atacante == 0:
					equipo_suceso = self.equipo_local
				else:
					equipo_suceso = self.equipo_visitante

				# Crear jugada
				num_acciones = (randint(2, 18) + randint(2, 18) + randint(2, 18)) / 3
				seg_accion = 2 + (int)((100.0 - velocidad[id_equipo_atacante]) / 10) + randint(0, 2)

				if num_acciones <= 4:
					texto = "Contraataque"
					#print texto
					suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
					self.suceso_set.add(suceso)

				#print "\t" + "num_acciones: " + str(num_acciones) + " (" + str(seg_accion) + " seg / accion)"
				formula = ataque[id_equipo_atacante] / (10.0 * pases[id_equipo_atacante])
				prob_regate = probabilidadExito(formula)
				#print "Prob Pase/Regate (" + str(prob_regate) + "%) "
				accion = 1
				while (accion <= num_acciones) and (id_equipo_defensor != id_equipo_atacante):
					#print "\t" + str(accion) + ".- "

					# Realizar una de las acciones de la jugada completa
					if accion != num_acciones:
						# Calcular probabilidad de que la acción sea moverse con el balón, un pase o un regate
						p = randint(1, 120)
						# Regate
						if p <= prob_regate:
							formula = (1.0 * ataque[id_equipo_atacante] / defensa[id_equipo_defensor])
							prob_exito = probabilidadExito(formula)
							#print "Regate (" + str(prob_exito) + "%) "
							if(randint(1, 100) > prob_exito):
								id_equipo_atacante = id_equipo_defensor

								texto = "Regate fallado"
								#print texto
								suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
								self.suceso_set.add(suceso)
							else:
								texto = "Regate realizado"
								#print texto
								suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
								self.suceso_set.add(suceso)
						# Pase
						elif p <= 100:
							formula = (pases[id_equipo_atacante] * 2.0) / (defensa[id_equipo_defensor] + velocidad[id_equipo_defensor])
							prob_exito = probabilidadExito(formula)
							#print "Pase (" + str(prob_exito) + "%) "
							if(randint(1, 100) > prob_exito):
								id_equipo_atacante = id_equipo_defensor

								texto = "Pase fallado"
								#print texto
								suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
								self.suceso_set.add(suceso)
							else:
								texto = "Pase realizado"
								#print texto
								suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
								self.suceso_set.add(suceso)
						# Moverse con el balón
						else:
							texto = "Movimiento con balón"
							#print texto
							suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
							self.suceso_set.add(suceso)

					# Disparo a puerta
					else:
						# Calcular probabilidad de que el disparo vaya a portería (95% de la anotación)
						prob_exito = (20 + anotacion[id_equipo_atacante])
						if prob_exito > 100:
							prob_exito = 100
						prob_exito *= 0.95
						#print "Prob. disparo a porteria (" + str(prob_exito) + "%) "

						# Si el balón va a portería
						if(randint(1, 100) <= prob_exito):
							formula = (1.0 * anotacion[id_equipo_atacante] / portero[id_equipo_defensor])
							prob_exito = probabilidadExito(formula)
							#print "Disparo a puerta (" + str(prob_exito) + "%) "
							if(randint(1, 100) > prob_exito):
								texto = "Disparo parado"
								#print texto
								suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
								self.suceso_set.add(suceso)
							# Marcar gol
							else:
								num_goles[id_equipo_atacante] += 1

								texto = "Gol"
								#print texto
								suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
								self.suceso_set.add(suceso)

								# Tiempo perdido en la celebración del gol
								seg_restantes -= 30
								segundos_jugados += 30
								seg_descuento += 30
						# Fuera
						else:
							texto = "Disparo fuera"
							#print texto
							suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
							self.suceso_set.add(suceso)

							seg_descuento += 10

						# El equipo contrario se hace con el balón
						id_equipo_atacante = id_equipo_defensor

					seg_restantes -= seg_accion
					segundos_jugados += seg_accion
					accion += 1

				# Minutos de descuento
				if(seg_restantes <= 0):
					if(tiempo_descuento == False):
						tiempo_descuento = True
						min_descuento = 1 + (seg_descuento / 60)
						seg_restantes += ((min_descuento * 60) + randint(0, 30))

						texto = "TIEMPO DESCUENTO (" + str(min_descuento) + " minutos)"
						#print texto
						suceso = Suceso(segundo_partido = segundos_jugados - (segundos_jugados % 60), tipo = texto, equipo = equipo_suceso)
						self.suceso_set.add(suceso)
					else:
						texto = "FIN DE LA " + str(num_parte) + "ª PARTE"
						#print texto
						suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
						self.suceso_set.add(suceso)

			num_parte += 1

		self.goles_local = num_goles[0]
		self.goles_visitante = num_goles[1]
		self.jugado = True

		# Actualizar datos de la clasificacion dependiendo del ganador
		clasificacion_local = self.jornada.obtenerClasificacionEquipo(self.equipo_local)
		clasificacion_visitante = self.jornada.obtenerClasificacionEquipo(self.equipo_visitante)

		# Actualizar los goles
		clasificacion_local.goles_favor += self.goles_local
		clasificacion_local.goles_contra += self.goles_visitante
		clasificacion_visitante.goles_favor += self.goles_visitante
		clasificacion_visitante.goles_contra += self.goles_local

		# Actualizar las puntuaciones
		if (self.goles_local > self.goles_visitante):
			clasificacion_local.puntos += 3
		elif (self.goles_local < self.goles_visitante):
			clasificacion_visitante.puntos += 3
		else:
			clasificacion_local.puntos += 1
			clasificacion_visitante.puntos += 1

		if self.equipo_local.usuario:
			notificar(self.equipo_local.usuario, tipo = TipoNotificacion.PARTIDO_FINALIZADO, identificador = self.id, liga = self.equipo_local.liga)

		if self.equipo_visitante.usuario:
			notificar(self.equipo_visitante.usuario, tipo = TipoNotificacion.PARTIDO_FINALIZADO, identificador = self.id, liga = self.equipo_local.liga)

		# Guardar los cambios
		clasificacion_local.save()
		clasificacion_visitante.save()
		self.save()

	def __unicode__(self):
		''' Devuelve una cadena de texto que representa la clase '''
		return "Partido de %s contra %s en jornada %d de liga %d" % (self.equipo_local.nombre, self.equipo_visitante.nombre, self.jornada.numero, self.jornada.liga.id)

########################################################################

class Suceso(models.Model):
	''' Representa un suceso de un partido (gol, falta, etc) '''
	segundo_partido = models.PositiveIntegerField(null = True, blank = True)
	tipo = models.CharField(max_length = 50)

	equipo = models.ForeignKey(Equipo)
	partido = models.ForeignKey(Partido)

	def getMinuto(self):
		return self.segundo_partido / 60

	def getSegundo(self):
		return self.segundo_partido % 60

########################################################################
