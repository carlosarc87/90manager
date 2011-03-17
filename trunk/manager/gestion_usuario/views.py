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
from django.db import transaction
from django.contrib.auth import authenticate, login

import datetime

from models import Usuario
from forms import UsuarioForm, ContactoForm

from gestion_base.func import devolverMensaje
from gestion_usuario.func import obtenerUsuario

from gestion_sistema.gestion_liga.models import Liga

########################################################################

# Vista para registrar a un usuario
def registrar_usuario(request):
	''' Vista para registrar a un usuario '''
#	if obtenerUsuario(request) != None:
#		return devolverMensaje(request, "No puede registrar usuarios estando logueado.", "/")
	if request.method == 'POST':
		form = UsuarioForm(request.POST)
		if form.is_valid():
			# Solucion para los problemas de la password
			usuario = form.save(commit = False)
			password = form.cleaned_data['password']
			usuario.is_staff = False
			usuario.is_active = True
			usuario.is_superuser = False
			usuario.date_joined = datetime.datetime.now()
			usuario.save()
			# Loguear al usuario
			usuario_reg = authenticate(username = usuario.username, password = password)
			if usuario_reg is not None:
				login(request, usuario_reg)
				return devolverMensaje(request, "Se ha registrado correctamente.", "/cuentas/perfil/")
			else:
				return devolverMensaje(request, "ERROR.", "/cuentas/perfil/")

	else:
		form = UsuarioForm()

	return render_to_response("web/usuarios/registrar_usuario.html", {"form_reg": form})

########################################################################

@login_required
def perfil_usuario(request):
	''' Muestra el perfil del usuario logueado '''
	usuario = obtenerUsuario(request)
	if usuario is None:
		return devolverMensaje(request, "SHEEEEEEEEEE vuelve al redil.", "/admin/")
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
