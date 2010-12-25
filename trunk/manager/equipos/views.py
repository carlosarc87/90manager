from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.db import transaction

import datetime
import random

from manager.equipos.models import *
from manager.equipos.forms import *

###################### FUNCIONES AUXILIARES ############################

def obtenerUsuario(request):
	return Usuario.objects.get(id = request.user.id)

############################ VISTAS ####################################

@login_required
def index(request):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	
	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("base.html")
	c = Context({ "usuario" : usuario })
	return HttpResponse(t.render(c))
	
# Vista para registrar a un usuario
def registrar_usuario(request):
#	return HttpResponse("Aun no implementado del todo...")
#	if request.user == None:
	if request.method == 'POST':
		form = UsuarioForm(request.POST)
		if form.is_valid():
			# Solucion para los problemas de la password
			usuario = form.save(commit=False)
			usuario.is_staff = False
			usuario.is_active = True
			usuario.is_superuser = False
			usuario.date_joined = datetime.datetime.now()
			usuario.save()
			return HttpResponse("Se ha registrado correctamente. <a href=\"/cuentas/perfil\">Volver</a>")
	else:
		form = UsuarioForm()
	
	return render_to_response("registration/registrar_usuario.html", {"form": form })

@login_required
def perfil_usuario(request):
	usuario = obtenerUsuario(request)
	# Obtenemos las ligas creadas por el usuario
	ligas_creadas = Liga.objects.filter(creador = usuario)
	# Obtenemos los equipos
	equipos = usuario.equipo_set.all()
	
	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("cuentas/perfil.html")
	c = Context({"usuario" : usuario,
				 "ligas_creadas" : ligas_creadas,
				 "equipos" : equipos,
				})
	return HttpResponse(t.render(c))

@login_required
def ver_equipo(request, equipo_id):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	# Obtenemos el equipo
	equipo = Equipo.objects.get(id = equipo_id)
	# Obtenemos los jugadores
	jugadores = equipo.jugador_set.all()
	# Obtenemos la liga
	liga = equipo.liga

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("equipos/ver_equipo.html")
	c = Context({"usuario" : usuario,
				 "liga" : liga,
				 "equipo" : equipo,
				 "jugadores" : jugadores,
				})
	return HttpResponse(t.render(c))
	
@login_required
def ver_jugador(request, jugador_id):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	# Obtenemos el jugador
	jugador = Jugador.objects.get(id = jugador_id)
	# Obtenemos el equipo
	equipo = jugador.equipo
	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("jugadores/ver_jugador.html")
	c = Context({"equipo" : equipo,
				 "usuario" : usuario,
				 "jugador" : jugador,
				})
	return HttpResponse(t.render(c))

@login_required
def ver_liga(request, liga_id):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	# Obtenemos la liga
	liga = Liga.objects.get(id = liga_id)
	# Obtenemos los equipos que juegan en la liga
	equipos = liga.equipo_set.all()
	# Obtenemos las jornadas
	jornadas = liga.jornada_set.all()

	# Obtenemos las jornadas no jugadas
	jornadas_restantes = liga.jornada_set.filter(jugada = False)
	
	activada = liga.activada()

	jornada_actual = None

	# Comprobamos si el jugador tiene un equipo en esta liga
	equipo_propio = liga.equipo_set.filter(usuario = usuario)
	if len(equipo_propio) > 0:
		equipo_propio = equipo_propio[0]
	else:
		equipo_propio = None
	
	if activada:
		# Comprobamos si la liga ha acabado
		jornada_actual = None
		if len(jornadas_restantes) > 0:
			# No ha acabado aun
			jornada_actual = jornadas_restantes[0]
		else:
			# Ha acabado
			jornada_actual = None
		
	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("ligas/ver_liga.html")
	c = Context({"liga" : liga,
				 "equipos" : equipos,
				 "jornadas" : jornadas,
				 "usuario" : usuario,
				 "jornada_actual" : jornada_actual,
				 "jornadas_restantes" : jornadas_restantes,
				 "activada" : activada,
				 "equipo_propio" : equipo_propio
				})
	return HttpResponse(t.render(c))

@login_required
def avanzar_jornada_liga(request, liga_id):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	# Obtenemos la liga
	liga = Liga.objects.get(id = liga_id)
	# Obtenemos las jornadas no jugadas
	jornadas = liga.jornada_set.filter(jugada = False)
	# Sacar primera jornada no jugada
	jornada = jornadas[0]
	partidos = jornada.partido_set.all()
	for partido in partidos:
		partido.jugar()
		partido.save()
	jornada.jugada = True
	jornada.save()
	return ver_liga(request, liga_id) # Devolvemos a lo bruto a la vision de la liga
	

@login_required
def ver_jornada(request, jornada_id):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	# Obtenemos la jornada
	jornada = Jornada.objects.get(id = jornada_id)
	# Obtenemos la liga
	liga = jornada.liga
	# Obtenemos los encuentros que hay
	emparejamientos = jornada.partido_set.all()

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("jornadas/ver_jornada.html")
	c = Context({"jornada" : jornada,
				 "emparejamientos" : emparejamientos,
				 "liga" : liga,
				 "usuario" : usuario,
				 "jornada_anterior" : jornada.id - 1,
				 "jornada_siguiente" : jornada.id + 1,
				})
	return HttpResponse(t.render(c))
	
@login_required
def ver_partido(request, partido_id):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	# Obtenemos el partido
	partido = Partido.objects.get(id = partido_id)
	# Obtenemos la liga y la jornada
	jornada = partido.jornada
	liga = jornada.liga
	# Obtenemos los equipos que juegan en el partido
	equipo_local = partido.equipo_local
	equipo_visitante = partido.equipo_visitante

	# Comprobamos si el partido ha acabado
	finalizado = partido.finalizado()
	# Calculamos el resultado
	resultado = 0
	if finalizado:
		if partido.goles_local > partido.goles_visitante:
			resultado = "Ganador local"
		elif partido.goles_local < partido.goles_visitante:
			resultado = "Ganador visitante"
		else:
			resultado = "Empate"

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("partidos/ver_partido.html")
	c = Context({"jornada" : jornada,
				 "equipo_local" : equipo_local,
				 "equipo_visitante" : equipo_visitante,
				 "liga" : liga,
				 "partido" : partido,
				 "usuario" : usuario,
				 "finalizado" : finalizado,
				 "resultado" : resultado,
				})
	return HttpResponse(t.render(c))

@login_required
def crear_equipo(request, liga_id):
#	return HttpResponse("Aun no implementado del todo...")
	liga = Liga.objects.get(id = liga_id)
	usuario = obtenerUsuario(request)
	if request.method == 'POST':
		form = EquipoForm(request.POST)
		if form.is_valid():
			# Solucion para los problemas de la password
			equipo = form.save(commit=False)
			equipo.usuario = usuario
			equipo.liga = liga
			equipo.save()
			# Annadir 20 jugadores aleatorios
			for j in range(0, 20):
				jugador = Jugador(nombre="Jugador %d - %s - %d" % (liga.id, equipo.nombre, j), equipo = equipo)
				jugador.save()
				equipo.agregarJugador(jugador)
			#equipo.save()
			return HttpResponse("Se ha creado correctamente. <a href=\"/equipos/%d\">Volver</a>" % equipo.id)
	else:
		form = EquipoForm()
	
	return render_to_response("equipos/crear_equipo.html", {"form": form, "usuario" : usuario, "liga" : liga })
	
@login_required
def crear_liga(request):
	usuario = obtenerUsuario(request)
	if request.method == 'POST':
		form = LigaForm(request.POST)
		if form.is_valid():
			# Solucion para los problemas de la password
			liga = form.save(commit=False)
			liga.creador = Usuario.objects.get(id=request.user.id)
			liga.save()

			return HttpResponse("Se ha creado correctamente. <a href=\"/ligas/%d\">Volver</a>" % liga.id)
	else:
		form = LigaForm()
	
	return render_to_response("ligas/crear_liga.html", {"form" : form, "usuario" : usuario })	

@login_required
@transaction.commit_on_success
def activar_liga(request, liga_id):
	usuario = obtenerUsuario(request)
	# Obtenemos la liga
	liga = Liga.objects.get(id = liga_id)
	liga.rellenarLiga()
	liga.generarJornadas()

	return HttpResponse("Se ha generado la liga correctamente. <a href=\"/ligas/%d\">Volver</a>" % liga.id)
	
