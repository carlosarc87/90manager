# -*- coding: utf-8 -*-
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.db import transaction

import datetime
import random

from manager.gestion_entrenador.models import *
from manager.gestion_entrenador.forms import *

###################### FUNCIONES AUXILIARES ############################

def obtenerUsuario(request):
	if Usuario.objects.filter(id = request.user.id).count() > 0:
		usuario = Usuario.objects.get(id = request.user.id)
	else:
		usuario = None
	return usuario

############################ VISTAS ####################################

@login_required
def index(request):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")
	
	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("base.html")
	c = Context({ "usuario" : usuario })
	return HttpResponse(t.render(c))
	
# Vista para registrar a un usuario
def registrar_usuario(request):
	
	if obtenerUsuario(request) != None:
		return HttpResponse("No puede registrar usuarios estando logueado.")
	if request.method == 'POST':
		form = UsuarioForm(request.POST)
		if form.is_valid():
			# Solucion para los problemas de la password
			usuario = form.save(commit = False)
			usuario.is_staff = False
			usuario.is_active = True
			usuario.is_superuser = False
			usuario.date_joined = datetime.datetime.now()
			usuario.save()
			return HttpResponse("Se ha registrado correctamente. <a href=\"/cuentas/perfil\">Volver</a>")
	else:
		form = UsuarioForm()
	
	return render_to_response("registration/registrar_usuario.html", {"form_reg": form})

@login_required
def perfil_usuario(request):
	usuario = obtenerUsuario(request)
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")
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
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")

	if Equipo.objects.filter(id = equipo_id).count() == 0:
		return HttpResponse("Error, no existe un equipo con identificador %s" % equipo_id)

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
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")

	if Jugador.objects.filter(id = jugador_id).count() == 0:
		return HttpResponse("Error, no existe un jugador con identificador %s" % jugador_id)
		
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
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")

	if Liga.objects.filter(id = liga_id).count() == 0:
		return HttpResponse("Error, no existe una liga con identificador %s" % liga_id)

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

	clasificacion = None

	liga_acabada = False

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
			liga_acabada = True
			
		if jornada_actual:
			if jornada_actual.numero > 0:
				jornada_anterior = liga.jornada_set.get(numero = jornada_actual.numero - 1)
				clasificacion_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
				clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: dato.puntos, reverse = True)
		if liga_acabada:
			jornada_anterior = liga.jornada_set.all()[len(liga.jornada_set.all()) - 1]
			clasificacion_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
			clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: dato.puntos, reverse = True)
			
	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("ligas/ver_liga.html")
	c = Context({"liga" : liga,
				 "equipos" : equipos,
				 "jornadas" : jornadas,
				 "usuario" : usuario,
				 "jornada_actual" : jornada_actual,
				 "jornadas_restantes" : jornadas_restantes,
				 "activada" : activada,
				 "equipo_propio" : equipo_propio,
				 "clasificacion" : clasificacion,
				 "liga_acabada" : liga_acabada
				})
	return HttpResponse(t.render(c))

@login_required
def avanzar_jornada_liga(request, liga_id):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")

	if Liga.objects.filter(id = liga_id).count() == 0:
		return HttpResponse("Error, no existe una liga con identificador %s" % liga_id)

	# Obtenemos la liga
	liga = Liga.objects.get(id = liga_id)
		
	# Obtenemos las jornadas no jugadas
	jornadas = liga.jornada_set.filter(jugada = False)
	
	if jornadas.count() == 0:
		return HttpResponse("Esta liga ya esta acabada")	
	
	# Sacar primera jornada no jugada
	jornada = jornadas[0]
	partidos = jornada.partido_set.all()
	for partido in partidos:
		if partido.equipo_local.usuario != None or partido.equipo_visitante.usuario != None:
			if not partido.finalizado():
				return HttpResponse("EH! que aun quedan partidos de los usuarios por jugar")
		else:
			if not partido.finalizado():
				# Generar alineacion aleatoria
				partido.titulares_local = partido.equipo_local.jugador_set.all()[:11]
				partido.titulares_visitante = partido.equipo_visitante.jugador_set.all()[:11]
				partido.jugar()
				partido.save()
	jornada.jugada = True
	jornada.save()
	jornada.obtenerClasificacion()
	return ver_liga(request, liga_id) # Devolvemos a lo bruto a la vision de la liga
	
@login_required
def jugar_partido(request, partido_id):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")
	
	if Partido.objects.filter(id = partido_id).count() == 0:
		return HttpResponse("Error, no existe un partido con identificador %s" % partido_id)

	partido = Partido.objects.get(id = partido_id)
	if partido.finalizado():
		return HttpResponse("Este partido ya se jugo")
	if partido.equipo_local.usuario != None:
		if partido.titulares_local.count() != 11:
			return HttpResponse("Eh, que tienes que preparar el equipo antes del partido")			
	else:
		partido.titulares_local = partido.equipo_local.jugador_set.all()[:11]

	if partido.equipo_visitante.usuario != None:
		if partido.titulares_visitante.count() != 11:
			return HttpResponse("Eh, que tienes que preparar el equipo antes del partido")			
	else:
		partido.titulares_visitante = partido.equipo_visitante.jugador_set.all()[:11]
	partido.jugar()
	partido.save()
	
	return ver_partido(request, partido_id)

@login_required
def ver_jornada(request, jornada_id):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")

	if Jornada.objects.filter(id = jornada_id).count() == 0:
		return HttpResponse("Error, no existe una jornada con identificador %s" % jornada_id)

	# Obtenemos la jornada
	jornada = Jornada.objects.get(id = jornada_id)
	# Obtenemos la liga
	liga = jornada.liga
	# Obtenemos los encuentros que hay
	emparejamientos = jornada.partido_set.all()
	# Obtenemos la clasificacion

	clasificacion = None
	clasificacion_anterior = None
	if jornada.jugada:
		clasificacion_sin_ordenar = jornada.clasificacionequipojornada_set.all()
		# Funcion sorted devuelve una COPIA de la lista ordenada
		clasificacion = sorted(clasificacion_sin_ordenar, key = lambda dato: dato.puntos, reverse = True)

	if jornada.numero >= 1:
		jornada_anterior = liga.jornada_set.get(numero = jornada.numero - 1)
		if jornada_anterior.jugada:
			clasificacion_anterior_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
			clasificacion_anterior = sorted(clasificacion_anterior_sin_ordenar, key = lambda dato: dato.puntos, reverse = True)

	jornada_anterior = liga.jornada_set.filter(numero = jornada.numero - 1)
	if jornada_anterior.count() > 0:
		jornada_anterior = jornada_anterior[0].id
	else:
		jornada_anterior = None

	jornada_siguiente = liga.jornada_set.filter(numero = jornada.numero + 1)
	if jornada_siguiente.count() > 0:
		jornada_siguiente = jornada_siguiente[0].id
	else:
		jornada_siguiente = None


	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("jornadas/ver_jornada.html")
	c = Context({"jornada" : jornada,
				 "emparejamientos" : emparejamientos,
				 "liga" : liga,
				 "usuario" : usuario,
				 "jornada_anterior" : jornada_anterior,
				 "jornada_siguiente" : jornada_siguiente,
				 "clasificacion" : clasificacion,
				 "clasificacion_anterior" : clasificacion_anterior,
				})
	return HttpResponse(t.render(c))
	
@login_required
def ver_partido(request, partido_id):
	# Obtenemos el usuario
	usuario = obtenerUsuario(request)
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")

	if Partido.objects.filter(id = partido_id).count() == 0:
		return HttpResponse("Error, no existe un partido con identificador %s" % partido_id)

	# Obtenemos el partido
	partido = Partido.objects.get(id = partido_id)
	# Obtenemos la liga y la jornada
	jornada = partido.jornada
	liga = jornada.liga
	# Obtenemos los equipos que juegan en el partido
	equipo_local = partido.equipo_local
	equipo_visitante = partido.equipo_visitante

	titulares_local = partido.titulares_local.all()
	titulares_visitante = partido.titulares_visitante.all()

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
				 "titulares_local" : titulares_local,
				 "titulares_visitante" : titulares_visitante
				})
	return HttpResponse(t.render(c))


@login_required
def preparar_partido(request, partido_id):
	partido = Partido.objects.get(id = partido_id)
	usuario = obtenerUsuario(request)
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")

	if Partido.objects.filter(id = partido_id).count() == 0:
		return HttpResponse("Error, no existe un partido con identificador %s" % partido_id)

	# Comprobar que el partido no se haya jugado ya
	if partido.finalizado():
		return HttpResponse("El partido ya acabo. <a href=\"/partidos/ver/%d\">Volver</a>" % partido.id)

	# Comprobar si el usuario juega en el partido
	if (partido.equipo_local.usuario == usuario): # Juega como local
		equipo = partido.equipo_local
		if request.method == 'POST':
			form = PrepararEquipoLocalForm(request.POST, instance = partido)
			if form.is_valid():
				form.save()
				return HttpResponse("Se ha creado correctamente la alineacion. <a href=\"/partidos/ver/%d\">Volver</a>" % partido.id)
		else:
			form = PrepararEquipoLocalForm(instance = partido)

	elif (partido.equipo_visitante.usuario == usuario): # Juega como visitante
		equipo = partido.equipo_visitante
		if request.method == 'POST':
			form = PrepararEquipoVisitanteForm(request.POST, instance = partido)
			if form.is_valid():
				form.save()
				return HttpResponse("Se ha creado correctamente la alineacion. <a href=\"/partidos/ver/%d\">Volver</a>" % partido.id)
		else:
			form = PrepararEquipoVisitanteForm(instance = partido)
	
	else: # No juega como naaaaaaaaaaaaaaa
		return HttpResponse("No tienes vela en este entierro, o mejor dicho, no tienes equipo en este partido <a href=\"/partidos/ver/%d\">Volver</a>" % partido.id)

	return render_to_response("partidos/preparar_partido.html", {"form": form, "usuario" : usuario, "partido" : partido, "equipo" : equipo })	

@login_required
def crear_equipo(request, liga_id):
	usuario = obtenerUsuario(request)
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")

	if Liga.objects.filter(id = liga_id).count() == 0:
		return HttpResponse("Error, no existe una liga con identificador %s" % liga_id)

	liga = Liga.objects.get(id = liga_id)

	if liga.activada():
		return HttpResponse("Esta liga ya no acepta mas equipos")

	if request.method == 'POST':
		form = EquipoForm(request.POST)
		if form.is_valid():
			equipo = form.save(commit = False)
			equipo.usuario = usuario
			equipo.liga = liga
			equipo.save()
			# Annadir 20 jugadores aleatorios
			for j in range(0, 20):
				jugador = Jugador(nombre="Jugador %d - %s - %d" % (liga.id, equipo.nombre, j), equipo = equipo)
				jugador.save()
				equipo.agregarJugador(jugador)
			return HttpResponse("Se ha creado correctamente. <a href=\"/equipos/ver/%d\">Volver</a>" % equipo.id)
	else:
		form = EquipoForm()
	
	return render_to_response("equipos/crear_equipo.html", {"form": form, "usuario" : usuario, "liga" : liga })
	
@login_required
def crear_liga(request):
	usuario = obtenerUsuario(request)
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")
		
	if request.method == 'POST':
		form = LigaForm(request.POST)
		if form.is_valid():
			# Solucion para los problemas de la password
			liga = form.save(commit = False)
			liga.creador = Usuario.objects.get(id = request.user.id)
			liga.save()

			return HttpResponse("Se ha creado correctamente. <a href=\"/ligas/ver/%d\">Volver</a>" % liga.id)
	else:
		form = LigaForm()
	
	return render_to_response("ligas/crear_liga.html", {"form" : form, "usuario" : usuario })	

@login_required
@transaction.commit_on_success
def activar_liga(request, liga_id):
	usuario = obtenerUsuario(request)
	if usuario == None:
		return HttpResponse("¡Eh eh! No te <a href=\"/admin/\"/>escapes</a>")

	if Liga.objects.filter(id = liga_id).count() == 0:
		return HttpResponse("Error, no existe una liga con identificador %s" % liga_id)
		
	# Obtenemos la liga
	liga = Liga.objects.get(id = liga_id)
	
	if liga.activada():
		return HttpResponse("Ya esta activada esta liga. <a href=\"/ligas/ver/%d\">Ir</a> su pagina." % liga.id)
	
	liga.rellenarLiga()
	liga.generarJornadas()

	return HttpResponse("Se ha generado la liga correctamente. <a href=\"/ligas/ver/%d\">Volver</a>" % liga.id)
