from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.db import transaction

import random

from manager.equipos.models import *
from manager.equipos.forms import *

@login_required
def index(request):
	# Obtenemos el usuario
	usuario = request.user
	
	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("base.html")
	c = Context({ "usuario" : usuario })
	return HttpResponse(t.render(c))
	
# Vista para registrar a un usuario
def registrar_usuario(request):
	return HttpResponse("Aun no implementado del todo...")
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
			return HttpResponse("Se ha registrado correctamente. <a href=\"/\">Volver</a>")
	else:
		form = UsuarioForm()
	
	return render_to_response("registration/registrar_usuario.html", {"form": form }, context_instance=RequestContext(request))
#	return HttpResponse("No intentes crear un usuario %s estando ya registrado, eh!" % request.user.username)

@login_required
def perfil_usuario(request):
	usuario = request.user
	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("cuentas/perfil.html")
	c = Context({ "usuario" : usuario })
	return HttpResponse(t.render(c))

@login_required
def ver_equipo(request, equipo_id):
	# Obtenemos el usuario
	usuario = request.user
	# Obtenemos el equipo
	equipo = Equipo.objects.get(id = equipo_id)
	# Obtenemos los jugadores
	jugadores = equipo.jugador_set.all()
	# Obtenemos la liga
	liga = equipo.liga

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("equipos/ver_equipo.html")
	c = Context({"liga" : liga,
				 "equipo" : equipo,
				 "jugadores" : jugadores,
				})
	return HttpResponse(t.render(c))
	
@login_required
def ver_jugador(request, jugador_id):
	# Obtenemos el usuario
	usuario = request.user
	# Obtenemos el jugador
	jugador = Jugador.objects.get(id = jugador_id)
	# Obtenemos el equipo
	equipo = jugador.equipo
	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("jugadores/ver_jugador.html")
	c = Context({"equipo" : equipo,
				 "jugador" : jugador,
				})
	return HttpResponse(t.render(c))

@login_required
def ver_liga(request, liga_id):
	# Obtenemos el usuario
	usuario = request.user
	# Obtenemos la liga
	liga = Liga.objects.get(id = liga_id)
	# Obtenemos los equipos que juegan en la liga
	equipos = liga.equipo_set.all()
	# Obtenemos las jornadas
	jornadas = liga.jornada_set.all()

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("ligas/ver_liga.html")
	c = Context({"liga" : liga,
				 "equipos" : equipos,
				 "jornadas" : jornadas,
				})
	return HttpResponse(t.render(c))


@login_required
def ver_jornada(request, jornada_id):
	# Obtenemos el usuario
	usuario = request.user
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
				})
	return HttpResponse(t.render(c))
	
@login_required
def ver_partido(request, partido_id):
	# Obtenemos el usuario
	usuario = request.user
	# Obtenemos el partido
	partido = Partido.objects.get(id = partido_id)
	# Obtenemos la liga y la jornada
	jornada = partido.jornada
	liga = jornada.liga
	# Obtenemos los equipos que juegan en el partido
	equipo_local = partido.equipo_local
	equipo_visitante = partido.equipo_visitante

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("partidos/ver_partido.html")
	c = Context({"jornada" : jornada,
				 "equipo_local" : equipo_local,
				 "equipo_visitante" : equipo_visitante,
				 "liga" : liga,
				 "partido" : partido,
				})
	return HttpResponse(t.render(c))

@login_required
def crear_equipo(request):
	return HttpResponse("Aun no implementado del todo...")
	if request.method == 'POST':
		form = EquipoForm(request.POST)
		if form.is_valid():
			# Solucion para los problemas de la password
			equipo = form.save(commit=False)
			equipo.usuario = request.user
			# Annadir 20 jugadores aleatorios
			equipo.save()
			return HttpResponse("Se ha creado correctamente. <a href=\"/\">Volver</a>")
	else:
		form = EquipoForm()
	
	return render_to_response("equipo/crear_equipo.html", {"form": form }, context_instance=RequestContext(request))
	
@login_required
@transaction.commit_on_success
def crear_liga(request):
	if request.method == 'POST':
		form = LigaForm(request.POST)
		if form.is_valid():
			# Solucion para los problemas de la password
			liga = form.save(commit=False)
			liga.creador = Usuario.objects.get(id=request.user.id)
			liga.save()
			
			# Generar los equipos
			for i in range(0, liga.num_equipos):
				equipo = Equipo(nombre="Equipo %d - %d" % (liga.id, i), usuario = Usuario.objects.get(username = "BOT"), liga=liga)
				equipo.save()
				# Generar jugadores
				for j in range(0, 20):
					jugador = Jugador(nombre="Jugador %d - %d - %d" % (liga.id, i, j), equipo=equipo)
					jugador.save()
					equipo.agregarJugador(jugador)

			# Generar jornadas
			jornadas = []
			num_jornadas_ida = liga.num_equipos - 1
			num_emparejamientos_jornada = liga.num_equipos / 2
			id_equipos = list(liga.equipo_set.all())
			random.shuffle(id_equipos)

			# Crear jornadas de ida
			j = 0
			while j < num_jornadas_ida:
				emparejamientos_jornada = []
				for emp in range(0, num_emparejamientos_jornada):
					emparejamiento = [id_equipos[emp], id_equipos[liga.num_equipos - emp - 1]]
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
				jornada = Jornada(liga=liga, numero=i)
				jornada.save()
				for emparejamiento in jornadas[i]:
					partido = Partido(jornada=jornada, equipo_local=emparejamiento[0], equipo_visitante=emparejamiento[1])
					partido.save()
				

			return HttpResponse("Se ha creado correctamente. <a href=\"/\">Volver</a>")
	else:
		form = LigaForm()
	
	return render_to_response("ligas/crear_liga.html", {"form": form })


	# Coger nombre
	
	# Generar equipos
	
	# Generar jugadores para los equipos
	
	# Generar jornadas
	
