from django.db import models
from django.contrib.auth.models import User, UserManager

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
	division = models.IntegerField()
	fecha_inicio = models.DateField("Fecha de inicio")
	
	def agregarEquipo(self, equipo):
		''' Agrega un equipo a la liga '''
		self.equipos_set.add(equipo)
	
	def generar(self):
		''' Genera las jornadas de la liga '''
		for i in range((self.equipos_set.all().size() - 1) * 2):
			print "a"

# Jornada
class Jornada(models.Model):
	numero = models.IntegerField()
	fecha = models.DateField("Fecha")
	liga = models.ForeignKey(Liga)
	
# Equipo
class Equipo(models.Model):
	nombre = models.CharField(max_length=200)
	usuario = models.OneToOneField(Usuario)
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
	hora_inicio = models.TimeField("Hora de inicio")
	jornada = models.ForeignKey(Jornada)
	jugadores = models.ManyToManyField(Jugador)
	equipo_local = models.ForeignKey(Equipo, related_name="Local")
	equipo_visitante = models.F