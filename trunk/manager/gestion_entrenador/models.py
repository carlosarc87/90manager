# -*- coding: utf-8 -*-
# Clases del sistema

from django.db import models
from django.contrib.auth.models import User, UserManager

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
			for j in range(0, 20):
				jugador = Jugador(nombre="Jugador %d - %d - %d" % (self.id, i, j), equipo = equipo)
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
					print clasificacion_local.puntos
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
	
	def __init__(self, nombre, ataque, defensa, velocidad, pases, anotacion, portero):
		self.nombre = nombre

		self.ataque = ataque
		self.defensa = defensa
		self.velocidad = velocidad
		self.pases = pases
		self.anotacion = anotacion
		self.portero = portero
		
		self.posicion = self.mejorPosicion()
		
		self.titular = False
		self.suplente = False
		self.transferible = False

	def JugadorAleatorio(self, posicion, nivel):
		lista_nombres = []
		lista_apellidos = []
		
		# Obtener nombres de jugadores
		fich = open("nombres_hombres.txt", "r")
		while(True):
			nombre = fich.readline()
			if not nombre: break
			
			lista_nombres.append(nombre)
		
		fich.close()
		
		# Obtener apellidos de jugadores
		fich = open("apellidos.txt", "r")
		while(True):
			apellido = fich.readline()
			if not apellido: break
			
			lista_apellidos.append(apellido)
		
		fich.close()
		
		num_nombres = aleatorio(1, 2)
		nombre_completo = lista_nombres[aleatorio(0, len(lista_nombres) - 1)]
		if(num_nombres == 2):
			nombre_completo += (" " + lista_nombres[aleatorio(0, len(lista_nombres) - 1)])
		
		apellidos = lista_apellidos[aleatorio(0, len(lista_apellidos) - 1)] + " " + lista_apellidos[aleatorio(0, len(lista_apellidos) - 1)]
						
		nombre_completo = nombre_completo + " " + apellidos
		
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
		
		jug.setPosicion(posicion)
		return self

	def mejorPosicion():
		# CENTROCAMPISTA o DELANTERO
		if(self.ataque > self.defensa):
			if(self.anotacion > self.pases): return "DELANTERO"
			else: return "CENTROCAMPISTA"
		# DEFENSA o CENTROCAMPISTA
		elif(self.defensa > self.portero):
			if(self.pases > self.defensa): return "CENTROCAMPISTA"
			else: return "DEFENSA"
		
		return "PORTERO"

	def setNumero(self, numero):
		self.numero = numero;

	def setPosicion(self, posicion):
		self.posicion = posicion;

########################################################################

class AlineacionEquipo(models.Model):
	nombre = models.CharField(max_length = 200)
	titulares = models.ManyToManyField(Jugador, related_name = "Jugadores_titulares")
	suplentes = models.ManyToManyField(Jugador, related_name = "Jugadores_suplentes")
	
	def init(self, nombre, titulares, suplentes):
		self.nombre = nombre
		
		for jugador in titulares:
			self.titulares.append(titulares[i])
		
		for jugador in suplentes:
			self.suplentes.append(suplentes[i])
	
	def getValorAtaque(self):
		valor = 0
		num_jugadores_campo = len(self.titulares)
		for i in range(0, num_jugadores_campo):
			posicion = self.titulares[i].posicion
			ataque = self.titulares[i].ataque
			
			if(posicion == "DEFENSA"):
				valor += (int)(ataque * 0.25)
			else:
				if(posicion == "CENTROCAMPISTA"):
					valor += (int)(ataque * 0.75)
				else:
					if(posicion == "DELANTERO"):
						valor += ataque
		
		return valor / (num_jugadores_campo - 1)
	
	def getValorDefensa(self):
		valor = 0
		num_jugadores_campo = len(self.titulares)
		for i in range(0, num_jugadores_campo):
			posicion = self.titulares[i].posicion
			defensa = self.titulares[i].defensa
			
			if(posicion == "DEFENSA"):
				valor += defensa
			else:
				if(posicion == "CENTROCAMPISTA"):
					valor += (int)(defensa * 0.75)
				else:
					if(posicion == "DELANTERO"):
						valor += (int)(defensa * 0.25)
		
		return valor / (num_jugadores_campo - 1)
	
	def getValorPases(self):
		valor = 0
		num_jugadores_campo = len(self.titulares)
		for i in range(0, num_jugadores_campo):
			posicion = self.titulares[i].posicion
			pases = self.titulares[i].pases
			if(posicion == "DEFENSA"):
				valor += (int)(pases * 0.75)
			else:
				if(posicion == "CENTROCAMPISTA"):
					valor += pases
				else:
					if(posicion == "DELANTERO"):
						valor += (int)(pases * 0.75)
		
		return valor / (num_jugadores_campo - 1)
	
	def getValorVelocidad(self):
		valor = 0
		num_jugadores_campo = len(self.titulares)
		for i in range(0, num_jugadores_campo):
			posicion = self.titulares[i].posicion
			velocidad = self.titulares[i].velocidad
			if(posicion == "DEFENSA"):
				valor += (int)(velocidad * 0.75)
			else:
				if(posicion == "CENTROCAMPISTA"):
					valor += velocidad
				else:
					if(posicion == "DELANTERO"):
						valor += (int)(velocidad * 0.75)
		
		return valor / (num_jugadores_campo - 1)
	
	def getValorAnotacion(self):
		valor = 0
		num_jugadores_campo = len(self.titulares)
		for i in range(0, num_jugadores_campo):
			posicion = self.titulares[i].posicion
			anotacion = self.titulares[i].anotacion
			if(posicion == "DEFENSA"):
				valor += (int)(anotacion * 0.5)
			else:
				if(posicion == "CENTROCAMPISTA"):
					valor += (int)(anotacion * 0.75)
				else:
					if(posicion == "DELANTERO"):
						valor += anotacion
		
		return valor / (num_jugadores_campo - 1)
	
	def getValorPortero(self):
		valor = 0
		i = 0
		num_jugadores_campo = len(self.titulares)
		while (i < num_jugadores_campo) and (valor == 0):
			posicion = self.titulares[i].posicion
			
			if(posicion == "PORTERO"):
				valor = self.titulares[i].portero
				
			i += 1
		
		return valor

########################################################################

class Suceso(models.Model):
	segundo_partido = models.IntegerField(null = True, blank = True)
	tipo_suceso = models.CharField(max_length = 50)
	nombre_equipo = models.ForeignKey(Equipo)
	
	def __init__(self, segundo_partido, tipo_suceso, nombre_equipo):
		self.segundo_partido = segundo_partido
		self.tipo_suceso = tipo_suceso
		self.nombre_equipo = nombre_equipo
	
	def getMinuto(self):
		return self.segundo_partido / 60
	
	def getSegundo(self):
		return self.segundo_partido % 60

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

	goles_local = models.IntegerField(null = True, blank = True)
	goles_visitante = models.IntegerField(null = True, blank = True)

	jugado = models.BooleanField()

	titulares_local = models.ManyToManyField(Jugador, related_name = "Titulares_locales")
	titulares_visitante = models.ManyToManyField(Jugador, related_name = "Titulares_visitantes")
	
	sucesos_partido = models.ForeignKey(Suceso)

	def finalizado(self):
		''' Indica si un partido ya ha acabado '''
		return self.jugado

	def jugar(self):
		''' Juega el partido '''
		num_goles = []
		sucesos_partido = []
		alineacion_local = AlineacionEquipo(equipo_local, equipo_local.jugadores_set.all())
		alineacion_visitante = AlineacionEquipo(equipo_visitante, equipo_visitante.jugadores_set.all())
		alineacion = []
		alineacion[0] = alineacion_local
		alineacion[1] = alineacion_visitante
		
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
		
		print "-------------------------------------------"
		print alineacion[0].getNombre()
		print "Ataque: " + str(alineacion[0].getValorAtaque())
		print "Defensa: " + str(alineacion[0].getValorDefensa())
		print "Pases: " + str(alineacion[0].getValorPases())
		print "Velocidad: " + str(alineacion[0].getValorVelocidad())
		print "Anotacion: " + str(alineacion[0].getValorAnotacion())
		print "Portero: " + str(alineacion[0].getValorPortero())
		print "-------------------------------------------"
		print alineacion[1].getNombre()
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
				seg_accion = 2 + ((100 - velocidad[id_equipo_atacante]) / 10)
				
				#print "\t" + "num_acciones: " + str(num_acciones) + " (" + str(seg_accion) + " seg / accion)"
				formula = (1.0 * ataque[id_equipo_atacante]) / pases[id_equipo_atacante]
				prob_regate = 100 - (100 / (formula + 1))
				accion = 1
				while (accion <= num_acciones) and (id_equipo_defensor != id_equipo_atacante):
					#print "\t" + str(accion) + ".- "
					
					# Realizar una de las acciones de la jugada completa
					if(accion != num_acciones):
						# Calcular probabilidad de que la acción sea un pase o un regate
						# Regate
						if(aleatorio(1, 100) <= prob_regate):
							formula = (1.0 * ataque[id_equipo_atacante] / defensa[id_equipo_defensor])
							prob_exito = (100 - (100 / (formula + 1)))
							print "Regate (" + str(prob_exito) + "%) "
							if(aleatorio(1, 100) > prob_exito):
								id_equipo_atacante = id_equipo_defensor
						# Pase
						else:
							formula = (pases[id_equipo_atacante] * 2.0) / (defensa[id_equipo_defensor] + velocidad[id_equipo_defensor])
							prob_exito = (100 - (100 / (formula + 1)))
							print "Pase (" + str(prob_exito) + "%) "
							if(aleatorio(1, 100) > prob_exito):
								id_equipo_atacante = id_equipo_defensor
							
					# Disparo a puerta
					else:
						# Calcular probabilidad de que el disparo vaya a portería (95% de la anotación)
						prob_exito = anotacion[id_equipo_atacante] * 0.95
						
						# Si el balón va a portería
						if(aleatorio(1, 100) <= prob_exito):
							formula = (1.0 * anotacion[id_equipo_atacante] / portero[id_equipo_defensor])
							prob_exito = (100 - (100 / (formula + 1)))
							print "Disparo a puerta (" + str(prob_exito) + "%) "
							if(aleatorio(1, 100) > prob_exito):
								texto = "Disparo parado"
								suceso = Suceso(segundos_jugados, texto, alineacion[id_equipo_atacante].getNombre())
								sucesos_partido.append(suceso)
								print "fallado."
								
								id_equipo_atacante = id_equipo_defensor
							# Marcar gol
							else:
								num_goles[id_equipo_atacante] += 1
								
								texto = "Gol"
								suceso = Suceso(segundos_jugados, texto, alineacion[id_equipo_atacante].getNombre())
								sucesos_partido.append(suceso)
								print "¡GOL!"
								
								# Ahora sacará el equipo contrario
								id_equipo_atacante = id_equipo_defensor
								
								# Tiempo perdido en la celebración del gol
								seg_restantes -= 30
								segundos_jugados += 30
						# Fuera
						else:
							texto = "Disparo fuera"
							suceso = Suceso(segundos_jugados, texto, alineacion[id_equipo_atacante].getNombre())
							sucesos_partido.append(suceso)
					
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
						suceso = Suceso(segundos_jugados - (segundos_jugados % 60), texto)
						sucesos_partido.append(suceso)
						print "Tiempo añadido: " + str(min_descuento) + " minutos"
					else:
						texto = "FIN DE LA " + str(num_parte) + "ª PARTE"
						suceso = Suceso(segundos_jugados, texto)
						sucesos_partido.append(suceso)
					
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
