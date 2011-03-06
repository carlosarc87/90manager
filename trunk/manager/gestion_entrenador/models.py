# -*- coding: utf-8 -*-
# Clases del sistema

from django.db import models
from django.contrib.auth.models import User, UserManager
from manager.gestion_entrenador.func import *

import random

########################################################################

# Usuario - hereda de la clase User de django
class Usuario(User):
	''' Representa a un usuario en el sistema '''
	objects = UserManager()

	def __unicode__(self):
		''' Devuelve una cadena de texto que representa la clase '''
		return self.username

	def save(self):
		''' Sobreescritura de la funcion save para arreglar un fallo con las contraseñas '''
		password = ""
		password = self.password
		self.set_password(self.password)
		if self.email == "":
			self.email = "none@none.net"
		User.save(self)

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

	def rellenarLiga(self):
		''' Rellena los huecos vacios de una liga con equipos controlados por bots '''
		# Generar los equipos
		for i in range(self.equipo_set.count(), self.num_equipos):
			equipo = Equipo(nombre="Equipo %d - %d" % (self.id, i), usuario = None, liga = self)
			equipo.save()
			# Generar jugadores
			for j in range(1, 20):
				# Establecer posición
				if (j == 1 or j == 20):
					posicion = "PORTERO"
				elif ((j >= 2 and j <= 5) or (j >= 12 and j <= 14)):
					posicion = "DEFENSA"
				elif ((j >= 6 and j <= 9) or (j >= 15 and j <= 17)):
					posicion = "CENTROCAMPISTA"
				else:
					posicion = "DELANTERO"

				# Establecer si es titular o suplente
				if (j <= 11):
					titular = True
					suplente = False
				else:
					titular = False
					suplente = True

				jugador = Jugador(equipo = equipo, nombre = nombreJugadorAleatorio(), titular = titular, suplente = suplente, transferible = False)
				jugador.setNumero(j)
				jugador.setPosicion(posicion)
				jugador.setHabilidadesAleatorias(posicion, 50)
				jugador.save()
				equipo.agregarJugador(jugador)

	def generarJornadas(self):
		''' Genera las jornadas de una liga '''
		jornadas = []
		num_jornadas_ida = self.num_equipos - 1
		num_emparejamientos_jornada = self.num_equipos / 2
		# Creamos una copia de los equipos
		id_equipos = list(self.equipo_set.all())
		random.shuffle(id_equipos)

		# Crear jornadas de ida
		j = 0
		while j < num_jornadas_ida:
			emparejamientos_jornada = []
			for emp in range(0, num_emparejamientos_jornada):
				emparejamiento = [id_equipos[emp], id_equipos[self.num_equipos - emp - 1]]
				emparejamientos_jornada.append(emparejamiento)
			# Annadir todos los emparejamientos a la jornada
			jornadas.append(emparejamientos_jornada)

			# Colocar segundo equipo al final del vector. El primer equipo siempre queda fijo
			equipo_pal_fondo = id_equipos.pop(1)
			id_equipos.append(equipo_pal_fondo)
			j += 1

		ultima_jornada = num_jornadas_ida * 2
		while (j < ultima_jornada):
			emparejamientos_jornada = []
			for emp in range(0, num_emparejamientos_jornada):
				emparejamiento = [jornadas[j - num_jornadas_ida][emp][1], jornadas[j - num_jornadas_ida][emp][0]]
				emparejamientos_jornada.append(emparejamiento)
			# Annadir todos los emparejamientos a la jornada
			jornadas.append(emparejamientos_jornada)
			j += 1

		for i in range(len(jornadas)):
			jornada = Jornada(liga = self, numero = i, jugada = False)
			jornada.save()
			for emparejamiento in jornadas[i]:
				partido = Partido(jornada = jornada, equipo_local = emparejamiento[0], equipo_visitante = emparejamiento[1], jugado = False)
				partido.save()

	def __unicode__(self):
		''' Devuelve una cadena de texto que representa la clase '''
		return self.nombre

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

# Equipo
class Equipo(models.Model):
	''' Representa un equipo en el sistema '''
	nombre = models.CharField(max_length=200)
	usuario = models.ForeignKey(Usuario, null = True)
	liga = models.ForeignKey(Liga)

	# Funciones
	def agregarJugador(self, jugador):
		''' Añade un jugador al equipo '''
		self.jugador_set.add(jugador)

	def __unicode__(self):
		return self.nombre

########################################################################

# Jugador
class Jugador(models.Model):
	''' Representa un jugador '''
	nombre = models.CharField(max_length = 200)
	equipo = models.ForeignKey(Equipo)

	numero = models.IntegerField(null = True, blank = True)
	posicion = models.CharField(max_length = 50)

	ataque = models.IntegerField(null = False, blank = False)
	defensa = models.IntegerField(null = False, blank = False)
	velocidad = models.IntegerField(null = False, blank = False)
	pases = models.IntegerField(null = False, blank = False)
	anotacion = models.IntegerField(null = False, blank = False)
	portero = models.IntegerField(null = False, blank = False)

	titular = models.BooleanField()
	suplente = models.BooleanField()
	transferible = models.BooleanField()

	def __unicode__(self):
		return self.nombre

	def setHabilidadesAleatorias(self, posicion, nivel):
		if(posicion == "DELANTERO"):
			self.ataque = aleatorio((int)(nivel * 0.8), nivel)
			self.defensa = aleatorio(0, (int)(nivel * 0.3))
			self.velocidad = aleatorio((int)(nivel * 0.5), nivel)
			self.pases = aleatorio((int)(nivel * 0.5), (int)(nivel * 0.8))
			self.anotacion = aleatorio((int)(nivel * 0.8), nivel)
			self.portero = aleatorio(0, (int)(nivel * 0.1))

		elif(posicion == "CENTROCAMPISTA"):
			self.ataque = aleatorio((int)(nivel * 0.5), (int)(nivel * 0.8))
			self.defensa = aleatorio((int)(nivel * 0.5), (int)(nivel * 0.8))
			self.velocidad = aleatorio((int)(nivel * 0.5), nivel)
			self.pases = aleatorio((int)(nivel * 0.7), nivel)
			self.anotacion = aleatorio((int)(nivel * 0.3), (int)(nivel * 0.8))
			self.portero = aleatorio(0, (int)(nivel * 0.1))

		elif(posicion == "DEFENSA"):
			self.ataque = aleatorio(0, (int)(nivel * 0.3))
			self.defensa = aleatorio((int)(nivel * 0.8), nivel)
			self.velocidad = aleatorio((int)(nivel * 0.5), nivel)
			self.pases = aleatorio((int)(nivel * 0.5), (int)(nivel * 0.8))
			self.anotacion = aleatorio(0, (int)(nivel * 0.5))
			self.portero = aleatorio(0, (int)(nivel * 0.3))

		elif(posicion == "PORTERO"):
			self.ataque = aleatorio(0, (int)(nivel * 0.3))
			self.defensa = aleatorio(0, (int)(nivel * 0.3))
			self.velocidad = aleatorio((int)(nivel * 0.5), nivel)
			self.pases = aleatorio((int)(nivel * 0.3), (int)(nivel * 0.7))
			self.anotacion = aleatorio(0, (int)(nivel * 0.1))
			self.portero = aleatorio((int)(nivel * 0.8), nivel)

		else:
			self.ataque = aleatorio(0, nivel)
			self.defensa = aleatorio(0, nivel)
			self.velocidad = aleatorio(0, nivel)
			self.pases = aleatorio(0, nivel)
			self.anotacion = aleatorio(0, nivel)
			self.portero = aleatorio(0, nivel)

		return self

	def mejorPosicion(self):
		# CENTROCAMPISTA o DELANTERO
		if(self.ataque > self.defensa):
			if(self.anotacion > self.pases):
				return "DELANTERO"
			else:
				return "CENTROCAMPISTA"
		# DEFENSA o CENTROCAMPISTA
		elif(self.defensa > self.portero):
			if(self.pases > self.defensa):
				return "CENTROCAMPISTA"
			else:
				return "DEFENSA"

		return "PORTERO"

	def setNumero(self, numero):
		self.numero = numero

	def setPosicion(self, posicion):
		self.posicion = posicion

	def valorMercado(self):
		if (self.posicion == "PORTERO"):
			media_hab_principales = self.portero
			media_hab_secundarias = self.pases
			media_hab_poco_importantes = (self.ataque + self.defensa + self.velocidad + self.anotacion) / 4

		elif (self.posicion == "DEFENSA"):
			media_hab_principales = self.defensa
			media_hab_secundarias = (self.velocidad + self.pases) / 2
			media_hab_poco_importantes = (self.ataque + self.anotacion + self.portero) / 3

		elif (self.posicion == "CENTROCAMPISTA"):
			media_hab_principales = (self.velocidad + self.pases) / 2
			media_hab_secundarias = (self.ataque + self.defensa + self.anotacion) / 3
			media_hab_poco_importantes = self.portero

		elif (self.posicion == "DELANTERO"):
			media_hab_principales = (self.ataque + self.anotacion) / 2
			media_hab_secundarias = (self.velocidad + self.pases) / 2
			media_hab_poco_importantes = (self.defensa + self.portero) / 2

		else:
			media_hab_principales = 0
			media_hab_secundarias = 0
			media_hab_poco_importantes = 0

		return (int)((1.15 ** media_hab_principales) + (1.1 ** media_hab_secundarias) + (1.05 ** media_hab_poco_importantes))

########################################################################

class AlineacionEquipo(models.Model):
	equipo = models.ForeignKey(Equipo)
	titulares = models.ManyToManyField(Jugador, related_name = "Jugadores_titulares")
	suplentes = models.ManyToManyField(Jugador, related_name = "Jugadores_suplentes")

	def getValorAtaque(self):
		valor = 0
		titulares = self.titulares.all()
		num_jugadores_campo = len(titulares)
		for i in range(0, num_jugadores_campo):
			posicion = titulares[i].posicion
			ataque = titulares[i].ataque

			if(posicion == "DEFENSA"):
				valor += (int)(ataque * 0.25)
			elif(posicion == "CENTROCAMPISTA"):
				valor += (int)(ataque * 0.75)
			elif(posicion == "DELANTERO"):
				valor += ataque

		return valor / (num_jugadores_campo - 1)

	def getValorDefensa(self):
		valor = 0
		titulares = self.titulares.all()
		num_jugadores_campo = len(titulares)
		for i in range(0, num_jugadores_campo):
			posicion = titulares[i].posicion
			defensa = titulares[i].defensa

			if(posicion == "DEFENSA"):
				valor += defensa
			elif(posicion == "CENTROCAMPISTA"):
				valor += (int)(defensa * 0.75)
			elif(posicion == "DELANTERO"):
				valor += (int)(defensa * 0.25)

		return valor / (num_jugadores_campo - 1)

	def getValorPases(self):
		valor = 0
		titulares = self.titulares.all()
		num_jugadores_campo = len(titulares)
		for i in range(0, num_jugadores_campo):
			posicion = titulares[i].posicion
			pases = titulares[i].pases
			if(posicion == "DEFENSA"):
				valor += (int)(pases * 0.75)
			elif(posicion == "CENTROCAMPISTA"):
				valor += pases
			elif(posicion == "DELANTERO"):
				valor += (int)(pases * 0.75)

		return valor / (num_jugadores_campo - 1)

	def getValorVelocidad(self):
		valor = 0
		titulares = self.titulares.all()
		num_jugadores_campo = len(titulares)
		for i in range(0, num_jugadores_campo):
			posicion = titulares[i].posicion
			velocidad = titulares[i].velocidad
			if(posicion == "DEFENSA"):
				valor += (int)(velocidad * 0.75)
			elif(posicion == "CENTROCAMPISTA"):
				valor += velocidad
			elif(posicion == "DELANTERO"):
				valor += (int)(velocidad * 0.75)

		return valor / (num_jugadores_campo - 1)

	def getValorAnotacion(self):
		valor = 0
		titulares = self.titulares.all()
		num_jugadores_campo = len(titulares)
		for i in range(0, num_jugadores_campo):
			posicion = titulares[i].posicion
			anotacion = titulares[i].anotacion
			if(posicion == "DEFENSA"):
				valor += (int)(anotacion * 0.5)
			elif(posicion == "CENTROCAMPISTA"):
				valor += (int)(anotacion * 0.75)
			elif(posicion == "DELANTERO"):
				valor += anotacion

		return valor / (num_jugadores_campo - 1)

	def getValorPortero(self):
		valor = 0
		i = 0
		titulares = self.titulares.all()
		num_jugadores_campo = len(titulares)
		while (i < num_jugadores_campo) and (valor == 0):
			posicion = titulares[i].posicion

			if(posicion == "PORTERO"):
				valor = titulares[i].portero

			i += 1

		return valor

########################################################################

# Partido
class Partido(models.Model):
	''' Representa un partido en el sistema '''
	#hora_inicio = models.TimeField("Hora de inicio")
	jornada = models.ForeignKey(Jornada)
	equipo_local = models.ForeignKey(Equipo, related_name = "Local")
	equipo_visitante = models.ForeignKey(Equipo, related_name = "Visitante")

	alineacion_local = models.ForeignKey(AlineacionEquipo, related_name = "AlineacionLocal", null = True)
	alineacion_visitante = models.ForeignKey(AlineacionEquipo, related_name = "AlineacionVisitante", null = True)

	goles_local = models.IntegerField(null = True, blank = True)
	goles_visitante = models.IntegerField(null = True, blank = True)

	jugado = models.BooleanField()

	def finalizado(self):
		''' Indica si un partido ya ha acabado '''
		return self.jugado

	def crearAlineacion(self, local, titulares, suplentes):
		if local:
			equipo = self.equipo_local
			if self.alineacion_local != None:
				del self.alineacion_local
		else:
			equipo = self.equipo_visitante
			if self.alineacion_visitante != None:
				del self.alineacion_visitante

		alineacion = AlineacionEquipo(equipo = equipo)
		alineacion.save()

		for jugador in titulares:
			alineacion.titulares.add(jugador)
		for jugador in suplentes:
			alineacion.suplentes.add(jugador)

		if local:
			self.alineacion_local = alineacion
		else:
			self.alineacion_visitante = alineacion

	def jugar(self):
		''' Juega el partido '''
		num_goles = [0, 0]

		# Obtener jugadores titulares y suplentes de los 2 equipos
		titulares_local = self.equipo_local.jugador_set.filter(titular = True)
		suplentes_local = self.equipo_local.jugador_set.filter(suplente = True)
		titulares_visitante = self.equipo_visitante.jugador_set.filter(titular = True)
		suplentes_visitante = self.equipo_visitante.jugador_set.filter(suplente = True)

		# Obtener alineaciones de los 2 equipos
		alineacion_local = self.alineacion_local
		alineacion_visitante = self.alineacion_visitante

		if not alineacion_local:
			self.crearAlineacion(True, self.equipo_local.jugador_set.all()[:11], self.equipo_local.jugador_set.all()[11:])
			alineacion_local = self.alineacion_local
		if not alineacion_visitante:
			self.crearAlineacion(False, self.equipo_visitante.jugador_set.all()[:11], self.equipo_visitante.jugador_set.all()[11:])
			alineacion_visitante = self.alineacion_visitante

		alineacion = [alineacion_local, alineacion_visitante]

		num_parte = 1 # Parte de partido que se está jugando

		# Inicializar variables para el partido
		# --------------------------------------
		ataque = [alineacion[0].getValorAtaque(), alineacion[1].getValorAtaque()]
		defensa = [alineacion[0].getValorDefensa(), alineacion[1].getValorDefensa()]
		pases = [alineacion[0].getValorPases(), alineacion[1].getValorPases()]
		velocidad = [alineacion[0].getValorVelocidad(), alineacion[1].getValorVelocidad()]
		anotacion = [alineacion[0].getValorAnotacion(), alineacion[1].getValorAnotacion()]
		portero = [alineacion[0].getValorPortero(), alineacion[1].getValorPortero()]
		# --------------------------------------

		los_gatos_nos_dominaran = True
		if not los_gatos_nos_dominaran:
			print "-------------------------------------------"
			#print alineacion[0].getNombre()
			print "Ataque: " + str(alineacion[0].getValorAtaque())
			print "Defensa: " + str(alineacion[0].getValorDefensa())
			print "Pases: " + str(alineacion[0].getValorPases())
			print "Velocidad: " + str(alineacion[0].getValorVelocidad())
			print "Anotacion: " + str(alineacion[0].getValorAnotacion())
			print "Portero: " + str(alineacion[0].getValorPortero())
			print "-------------------------------------------"
			#print alineacion[1].getNombre()
			print "Ataque: " + str(alineacion[1].getValorAtaque())
			print "Defensa: " + str(alineacion[1].getValorDefensa())
			print "Pases: " + str(alineacion[1].getValorPases())
			print "Velocidad: " + str(alineacion[1].getValorVelocidad())
			print "Anotacion: " + str(alineacion[1].getValorAnotacion())
			print "Portero: " + str(alineacion[1].getValorPortero())
			print "-------------------------------------------"

		# Continuar jugando mientras no se hayan acabado las 2 partes del partido
		while(num_parte <= 2):
			# Establecer equipo que comienza a jugar la parte
			if(num_parte == 1):
				# Sortear equipo que comienza
				equipo_comienza = aleatorio(0, 1)
				id_equipo_atacante = equipo_comienza
				segundos_jugados = 0
			else:
				if(equipo_comienza == 0): id_equipo_atacante = 1
				else: id_equipo_atacante = 0
				segundos_jugados = 45 * 60

			# Iniciar variables
			seg_restantes = 45 * 60
			tiempo_descuento = False

			# Continuar jugando mientras no se haya acabado todo el tiempo de la parte actual
			while(seg_restantes > 0):
				# Establecer id del defensor
				if(id_equipo_atacante == 0): id_equipo_defensor = 1
				else: id_equipo_defensor = 0

				# Crear jugada
				num_acciones = (aleatorio(2, 20) + aleatorio(2, 20) + aleatorio(2, 20)) / 3
				seg_accion = 2 + (int)((100.0 - velocidad[id_equipo_atacante]) / 10) + aleatorio(0, 2)

				#print "\t" + "num_acciones: " + str(num_acciones) + " (" + str(seg_accion) + " seg / accion)"
				formula = (1.0 * ataque[id_equipo_atacante]) / pases[id_equipo_atacante]
				prob_regate = probabilidadExito(formula)
				#print "Prob Pase/Regate (" + str(prob_regate) + "%) "
				accion = 1
				while (accion <= num_acciones) and (id_equipo_defensor != id_equipo_atacante):
					#print "\t" + str(accion) + ".- "

					# Realizar una de las acciones de la jugada completa
					if(accion != num_acciones):
						# Calcular probabilidad de que la acción sea un pase o un regate
						# Regate
						if(aleatorio(1, 100) <= prob_regate):
							formula = (1.0 * ataque[id_equipo_atacante] / defensa[id_equipo_defensor])
							prob_exito = probabilidadExito(formula)
							#print "Regate (" + str(prob_exito) + "%) "
							if(aleatorio(1, 100) > prob_exito):
								id_equipo_atacante = id_equipo_defensor
						# Pase
						else:
							formula = (pases[id_equipo_atacante] * 2.0) / (defensa[id_equipo_defensor] + velocidad[id_equipo_defensor])
							prob_exito = probabilidadExito(formula)
							#print "Pase (" + str(prob_exito) + "%) "
							if(aleatorio(1, 100) > prob_exito):
								id_equipo_atacante = id_equipo_defensor

					# Disparo a puerta
					else:
						# Calcular probabilidad de que el disparo vaya a portería (95% de la anotación)
						prob_exito = anotacion[id_equipo_atacante] * 0.95

						# Si el balón va a portería
						if(aleatorio(1, 100) <= prob_exito):
							formula = (1.0 * anotacion[id_equipo_atacante] / portero[id_equipo_defensor])
							prob_exito = probabilidadExito(formula)
							#print "Disparo a puerta (" + str(prob_exito) + "%) "
							if(aleatorio(1, 100) > prob_exito):
								texto = "Disparo parado"
								#print texto
								if id_equipo_atacante == 0:
									equipo_suceso = self.equipo_local
								else:
									equipo_suceso = self.equipo_visitante
								suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
								self.suceso_set.add(suceso)

								id_equipo_atacante = id_equipo_defensor
							# Marcar gol
							else:
								num_goles[id_equipo_atacante] += 1

								texto = "Gol"
								#print texto
								if id_equipo_atacante == 0:
									equipo_suceso = self.equipo_local
								else:
									equipo_suceso = self.equipo_visitante
								suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
								self.suceso_set.add(suceso)

								# Ahora sacará el equipo contrario
								id_equipo_atacante = id_equipo_defensor

								# Tiempo perdido en la celebración del gol
								seg_restantes -= 30
								segundos_jugados += 30
						# Fuera
						else:
							texto = "Disparo fuera"
							#print texto
							if id_equipo_atacante == 0:
								equipo_suceso = self.equipo_local
							else:
								equipo_suceso = self.equipo_visitante
							suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
							self.suceso_set.add(suceso)

					seg_restantes -= seg_accion
					segundos_jugados += seg_accion
					accion += 1

				# Minutos de descuento
				if(seg_restantes <= 0):
					if(tiempo_descuento == False):
						tiempo_descuento = True
						min_descuento = aleatorio(1, 5)
						seg_restantes += ((min_descuento * 60) + aleatorio(0, 30))

						texto = "TIEMPO DESCUENTO (" + str(min_descuento) + " minutos)"
						#print texto
						if id_equipo_atacante == 0:
							equipo_suceso = self.equipo_local
						else:
							equipo_suceso = self.equipo_visitante
						suceso = Suceso(segundo_partido = segundos_jugados - (segundos_jugados % 60), tipo = texto, equipo = equipo_suceso)
						self.suceso_set.add(suceso)
					else:
						texto = "FIN DE LA " + str(num_parte) + "ª PARTE"
						#print texto
						if id_equipo_atacante == 0:
							equipo_suceso = self.equipo_local
						else:
							equipo_suceso = self.equipo_visitante
						suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
						self.suceso_set.add(suceso)

			num_parte += 1

		self.goles_local = num_goles[0]
		self.goles_visitante = num_goles[1]
		self.jugado = True

	def __unicode__(self):
		''' Devuelve una cadena de texto que representa la clase '''
		return "Partido de %s contra %s en jornada %d de liga %d" % (self.equipo_local.nombre, self.equipo_visitante.nombre, self.jornada.numero, self.jornada.liga.id)

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

class Suceso(models.Model):
	segundo_partido = models.IntegerField(null = True, blank = True)
	tipo = models.CharField(max_length = 50)

	equipo = models.ForeignKey(Equipo)
	partido = models.ForeignKey(Partido)

	def getMinuto(self):
		return self.segundo_partido / 60

	def getSegundo(self):
		return self.segundo_partido % 60

########################################################################
