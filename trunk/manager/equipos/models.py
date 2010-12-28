from django.db import models
from django.contrib.auth.models import User, UserManager

import random

# Usuario - hereda de la clase User de django
class Usuario(User):
	objects = UserManager()
	
	def __unicode__(self):
		return self.username
		
	def save(self):
		password = ""
		password = self.password
		self.set_password(self.password)
		if self.email == "":
			self.email = "none@none.net"
		User.save(self)

# Liga
class Liga(models.Model):
	creador = models.ForeignKey(Usuario)
	nombre = models.CharField(max_length = 200)
	num_equipos = models.IntegerField()
	
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
		# Generar jornadas
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
				partido = Partido(jornada=jornada, equipo_local=emparejamiento[0], equipo_visitante=emparejamiento[1])
				partido.save()

# Jornada
class Jornada(models.Model):
	numero = models.IntegerField()
	#fecha = models.DateField("Fecha")
	liga = models.ForeignKey(Liga)
	jugada = models.BooleanField()
	
	def obtenerClasificacion(self):
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
	
# Equipo
class Equipo(models.Model):
	nombre = models.CharField(max_length=200)
	usuario = models.ForeignKey(Usuario, null = True)
	liga = models.ForeignKey(Liga)
	
	# Funciones
	def agregarJugador(self, jugador):
		self.jugador_set.add(jugador)
	
	def __unicode__(self):
		return self.nombre

# Jugador
class Jugador(models.Model):
	nombre = models.CharField(max_length=200)
	equipo = models.ForeignKey(Equipo)
	
	def __unicode__(self):
		return self.nombre
		
# Partido
class Partido(models.Model):
	#hora_inicio = models.TimeField("Hora de inicio")
	jornada = models.ForeignKey(Jornada)
	#jugadores = models.ManyToManyField(Jugador)
	equipo_local = models.ForeignKey(Equipo, related_name = "Local")
	equipo_visitante = models.ForeignKey(Equipo, related_name = "Visitante")
	
	goles_local = models.IntegerField(null = True, blank = True)
	goles_visitante = models.IntegerField(null = True, blank = True)
	
	titulares_local = models.ManyToManyField(Jugador, related_name = "Titulares_locales")
	titulares_visitante = models.ManyToManyField(Jugador, related_name = "Titulares_visitantes")
	
	def finalizado(self):
		''' Indica si un partido ya ha acabado '''
		return self.goles_local != None
	
	def jugar(self):
		''' Juega el partido y devuelve al ganador'''
		self.goles_local = random.randint(0, 10)
		self.goles_visitante = random.randint(0, 10)

class ClasificacionEquipoJornada(models.Model):
	jornada = models.ForeignKey(Jornada)
	equipo = models.ForeignKey(Equipo)
	#posicion = models.IntegerField()
	goles_favor = models.IntegerField()
	goles_contra = models.IntegerField()
	puntos = models.IntegerField()
	
