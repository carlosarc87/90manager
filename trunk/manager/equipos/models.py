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
	division = models.IntegerField()
	fecha_inicio = models.DateField("Fecha de inicio")

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
	equipo_visitante = models.ForeignKey(Equipo, related_name="Visitante")	

