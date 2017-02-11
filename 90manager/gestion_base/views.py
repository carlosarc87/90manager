# -*- coding: utf-8 -*-
"""
Copyright 2017 by
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

from datetime import datetime

from django.contrib.auth.decorators import login_required

from gestion_base.func import devolver_mensaje, generar_pagina, redireccionar

from .forms import ContactoForm


########################################################################

@login_required
def index():
    """ Devuelve la pagina principal """
    return redireccionar("/tablon/")


########################################################################

def creditos(request):
    """ Ir a la pagina de creditos """
    return generar_pagina(request, "web/creditos.html")


########################################################################

def contacto(request):
    """ Muestra la página para rellenar el formulario de "contacta con nosotros" """
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            from django.core.mail import mail_admins
            mensaje_puro = form.cleaned_data['mensaje']
            asunto = form.cleaned_data['asunto']
            emisor = form.cleaned_data['emisor']

            mensaje = "-----------------------------------------------------------------\n"
            mensaje += " Mensaje de contacto enviado mediante el formulario de 90manager \n"
            mensaje += "  De: " + emisor + "\n"
            mensaje += "  Enviado a las: " + str(datetime.now()) + " \n"
            mensaje += "-----------------------------------------------------------------\n"
            mensaje += "\n"
            mensaje += mensaje_puro

            # Mandar correo
            mail_admins('[CONTACTO]: ' + asunto, mensaje)

            return devolver_mensaje(request, "El mensaje ha sido enviado", 1, "/")
    else:
        form = ContactoForm()

    c = {
        "form": form
    }

    return generar_pagina(request, "web/contacto.html", c)


########################################################################

def changelog(request):
    """ Muestra el historial de versiones de la web """
    return generar_pagina(request, "web/changelog.html")


########################################################################

def siguenos(request):
    """ Muestra las páginas donde seguir el proyecto """
    return generar_pagina(request, "web/siguenos.html")


########################################################################

def condiciones(request):
    """ Muestra las condiciones de uso """
    return generar_pagina(request, "web/condiciones.html")


########################################################################

def bajo_construccion(request):
    """ Mensaje para los enlaces que no estan construidos aun """
    return generar_pagina(request, "La página que deseas visitar aún no está acabada =(")

########################################################################
