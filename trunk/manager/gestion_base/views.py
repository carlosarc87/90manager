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

from forms import ContactoForm

from gestion_base.func import devolverMensaje
from gestion_usuario.func import obtenerUsuario

########################################################################

def index(request):
	''' Devuelve la pagina principal '''
	t = loader.get_template("index.html")
	return render_to_response("index.html", {})

########################################################################

def contacto(request):
	''' Muestra la página para rellenar el formulario de "contacta con nosotros" '''
	if request.method == 'POST':
		form = ContactoForm(request.POST)
		if form.is_valid():
			return devolverMensaje(request, "Se ha rellenado correctamente el formulario de contacto.", "/")
	else:
		form = ContactoForm()

	return render_to_response("registration/contacto.html", {"form" : form})

########################################################################

def changelog(request):
	return HttpResponse("Aun no implementado.")

########################################################################
