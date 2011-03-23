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
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.mail import send_mail

import datetime, random, sha

from settings import URL_PROPIA, vper

from models import Usuario, ClaveRegistroUsuario
from forms import UsuarioForm

from gestion_base.func import devolverMensaje

from gestion_sistema.gestion_liga.models import Liga

########################################################################

# Vista para registrar a un usuario
def registrar_usuario(request):
	''' Vista para registrar a un usuario '''
	if request.user.is_authenticated():
		return devolverMensaje(request, "Ya estas registrado en el sistema", "/")
	if request.method == 'POST':
		form = UsuarioForm(request.POST)
		if form.is_valid():
			# Solucion para los problemas de la password
			usuario = form.save(commit = False)
			password = form.cleaned_data['password']
			if vper:
				usuario.is_active = False
			else:
				usuario.is_active = True

			usuario.is_staff = False
			usuario.is_superuser = False
			usuario.date_joined = datetime.datetime.now()
			usuario.set_password(password)
			usuario.save()

			if vper:
				# Generamos la clave de activacion
				salt = sha.new(str(random.random())).hexdigest()[:5]
				clave = sha.new(salt + usuario.username).hexdigest()

				# Dos días para activar la cuenta
				fin_clave = datetime.datetime.today() + datetime.timedelta(2)

				# Crear y guardar el perfil de la clave
				perfil_clave = ClaveRegistroUsuario(usuario = usuario, clave = clave, expira = fin_clave)
				perfil_clave.save()

				asunto = 'Activación de la cuenta'
				mensaje =  'Hola %s, gracias por registrarte en 90manager.\n' % (usuario.username)
				mensaje += 'Para activar la cuenta, pulse el siguiente link:\n'
				mensaje += URL_PROPIA + 'cuentas/confirmar/' + clave + '/' +'\n'
				mensaje += 'La clave expirara en 48 horas\n'
				mensaje += 'Muchas gracias de huevo, digo nuevo.\n'

				send_mail(asunto, mensaje, 'noreply@90manager.com', [usuario.email])

			# Loguear al usuario
			#usuario.is_active = True
			#usuario_reg = authenticate(username = usuario.username, password = password)
			#if usuario_reg is not None:
			#	login(request, usuario_reg)
			#	return devolverMensaje(request, "Se ha registrado correctamente.", "/cuentas/perfil/")
			#else:
			#	return devolverMensaje(request, "ERROR.", "/cuentas/perfil/")
			return devolverMensaje(request, "Se ha enviado un mensaje de confirmacion a tu correo", "/")
	else:
		form = UsuarioForm()

	return render_to_response("web/usuarios/registrar_usuario.html", { "form_reg": form })

########################################################################

@login_required
def perfil_usuario(request):
	''' Muestra el perfil del usuario logueado '''
	usuario = request.user
	# Obtenemos las ligas creadas por el usuario
	ligas_creadas = Liga.objects.filter(creador = usuario)

	# Obtenemos los equipos
	equipos = usuario.equipo_set.all()

	# Cargamos la plantilla con los parametros y la devolvemos
	t = loader.get_template("juego/cuentas/perfil.html")
	c = Context({"usuario" : usuario,
				 "ligas_creadas" : ligas_creadas,
				 "equipos" : equipos,
				})
	return HttpResponse(t.render(c))

########################################################################

def activar_usuario(request, clave):
	if request.user.is_authenticated():
		return devolverMensaje(request, "Ya estas activado en el sistema ya que estás registrado", "/")
	if ClaveRegistroUsuario.objects.filter(clave = clave).count() == 0:
		return devolverMensaje(request, "Error, no existe tal clave de activación", "/")
	cru = ClaveRegistroUsuario.objects.get(clave = clave)
	usuario = cru.usuario

	if cru.expira < datetime.datetime.today():
		usuario.delete()
		cru.delete()
		return devolverMensaje(request, "Error, la clave ya caducó, regístrese de nuevo", "/cuentas/registrar/")

	# Activamos al usuario
	usuario.is_active = True
	usuario.save()

	# Eliminamos la clave
	#cru.delete()
	return devolverMensaje(request, "Se activó al usuario correctamente", "/")

########################################################################













