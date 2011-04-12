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
from django.template import RequestContext

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

import datetime

from forms import ContactoForm

from gestion_base.func import devolverMensaje

########################################################################

@login_required
def index(request):
	''' Devuelve la pagina principal '''
	return HttpResponseRedirect("/tablon")

########################################################################

def creditos(request):
	''' Ir a la pagina de creditos '''
	return render_to_response("web/creditos.html", {})

########################################################################

def contacto(request):
	''' Muestra la página para rellenar el formulario de "contacta con nosotros" '''
	if request.method == 'POST':
		form = ContactoForm(request.POST)
		if form.is_valid():
			from django.core.mail import mail_admins
			mensaje_puro = form.cleaned_data['mensaje']
			asunto = form.cleaned_data['asunto']
			emisor = form.cleaned_data['emisor']

			mensaje =  "-----------------------------------------------------------------\n"
			mensaje += " Mensaje de contacto enviado mediante el formulario de 90manager \n"
			mensaje += "  De: " + emisor + "\n"
			mensaje += "  Enviado a las: " + str(datetime.datetime.now()) + " \n"
			mensaje += "-----------------------------------------------------------------\n"
			mensaje += "\n"
			mensaje += mensaje_puro

			# Mandar correo
			mail_admins('[CONTACTO]: ' + asunto, mensaje)
			return devolverMensaje(request, "Se nos ha enviado el mensaje, ¡Gracias! (O no, si nos has insultado xD).", "/")
	else:
		form = ContactoForm()

	c = RequestContext(request, { "form" : form })

	return render_to_response("web/contacto.html", c)

########################################################################

def changelog(request):
	''' Muestra el historial de versiones de la web '''
	return render_to_response("web/changelog.html", {})

########################################################################

def siguenos(request):
	''' Muestra las páginas donde seguir el proyecto '''
	return render_to_response("web/siguenos.html", {})

########################################################################

def condiciones(request):
	''' Muestra las condiciones de uso '''
	return render_to_response("web/condiciones.html", {})

########################################################################

def bajoConstruccion(request):
	''' Mensaje para los enlaces que no estan construidos aun '''
	return HttpResponse("La página que deseas visitar aún no está acabada =(")

########################################################################
