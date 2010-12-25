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
			equipo = Equipo(nombre="Equipo %d - %d" % (self.id, i), usuario = Usuario.objects.get(username = "BOT"), liga = self)
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
	
# Equipo
class Equipo(models.Model):
	nombre = models.CharField(max_length=200)
	usuario = models.ForeignKey(Usuario)
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
	equipo_local = models.ForeignKey(Equipo, related_name="Local")
	equipo_visitante = models.ForeignKey(Equipo, related_name="Visitante")
	
	goles_local = models.IntegerField(null=True, blank=True)
	goles_visitante = models.IntegerField(null=True, blank=True)
	
	titulares_local = models.ManyToManyField(Jugador, related_name="Titulares_locales")
	titulares_visitante = models.ManyToManyField(Jugador, related_name="Titulares_visitantes")
	
	def finalizado(self):
		''' Indica si un partido ya ha acabado '''
		return self.goles_local != None
	
	def jugar(self):
		''' Juega el partido y devuelve al ganador'''
		self.goles_local = random.randint(0, 10)
		self.goles_visitante = random.randint(0, 10)

