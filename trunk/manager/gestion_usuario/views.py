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

import datetime
import hashlib
import random

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render

from gestion_base.func import devolver_mensaje, generar_pagina, redireccionar
from gestion_sistema.gestion_liga.models import Liga
from settings import URL_PROPIA, vper

from .forms import UsuarioForm
from .models import ClaveRegistroUsuario, Usuario


########################################################################

def principal(request):
    """ Página principal del sistema """
    # Si el usuario está logeado
    if request.user.is_authenticated():
        return redireccionar("/tablon/")

    # Obtener número de usuarios registrados
    usuarios_registrados = Usuario.objects.count()

    # Formulario de registro
    form_reg = ""
    login_error = None
    if request.method == 'POST':
        # Formulario de acceso
        if "login" in request.POST:
            username = request.POST['login_username']
            password = request.POST['login_password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redireccionar("/tablon/")
                else:
                    login_error = "El usuario no ha sido activado aun"
            else:
                login_error = "Usuario o contraseña incorrectos"

        # Formulario de registro
        else:
            form_reg = UsuarioForm(request.POST)
            if form_reg.is_valid():
                # Solucion para los problemas de la password
                usuario = form_reg.save(commit=False)
                password = form_reg.cleaned_data['password']
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
                    salt = hashlib.sha1.new(str(random.random())).hexdigest()[:5]
                    clave = hashlib.sha1.new(salt + usuario.username).hexdigest()

                    # Dos días para activar la cuenta
                    fin_clave = datetime.datetime.today() + datetime.timedelta(2)

                    # Crear y guardar el perfil de la clave
                    perfil_clave = ClaveRegistroUsuario(usuario=usuario, clave=clave, expira=fin_clave)
                    perfil_clave.save()

                    asunto = 'Activación de la cuenta'
                    mensaje = 'Hola %s, gracias por registrarte en 90manager.\n' % usuario.username
                    mensaje += 'Para activar la cuenta, haz click en el siguiente link: '
                    mensaje += URL_PROPIA + 'cuentas/confirmar/' + clave + '/' + '\n'
                    mensaje += 'La clave expirará en 48 horas.\n'

                    send_mail(asunto, mensaje, 'noreply@90manager.com', [usuario.email])

                return devolver_mensaje(request, "Se ha enviado un mensaje de confirmación a tu correo", "/")
    else:
        form_reg = UsuarioForm()

    return render(request, "web/principal.html", {
        "form_reg": form_reg,
        "usuarios_registrados": usuarios_registrados,
        "login_error": login_error
    })


########################################################################

@login_required
def tablon(request):
    """ Muestra el tablon del usuario logueado """
    if 'liga_actual' in request.session:
        del request.session['liga_actual']

    usuario = request.user

    # Obtenemos las ligas creadas por el usuario
    ligas_creadas = Liga.objects.filter(creador=usuario)

    # Obtenemos los equipos del usuario
    equipos = usuario.equipo_set.all()

    # Creamos lista de ligas a las que tiene acceso el usuario
    ligas_usuario = list(ligas_creadas)

    for equipo in equipos:
        if ligas_usuario.count(equipo.liga) == 0:
            ligas_usuario.append(equipo.liga)

        index_liga = ligas_usuario.index(equipo.liga)
        ligas_usuario[index_liga].equipo_usuario = equipo

    # Cargamos la plantilla con los parametros y la devolvemos
    d = {
        "usuario": usuario,
        "ligas_usuario": ligas_usuario
    }

    return generar_pagina(request, "juego/tablon.html", d)


########################################################################

def activar_usuario(request, clave):
    if request.user.is_authenticated():
        return devolver_mensaje(request, "Ya estás activado en el sistema", "/")

    if ClaveRegistroUsuario.objects.filter(clave=clave).count() == 0:
        return devolver_mensaje(request, "Error: no existe la clave de activación dada", "/")

    cru = ClaveRegistroUsuario.objects.get(clave=clave)
    usuario = cru.usuario

    if cru.expira < datetime.datetime.today():
        usuario.delete()
        cru.delete()
        return devolver_mensaje(request, "Error: la clave ya caducó, regístrate de nuevo", "/cuentas/registrar/")

    # Activamos al usuario
    usuario.is_active = True
    usuario.save()

    # Eliminamos la clave
    cru.delete()

    return devolver_mensaje(request, "Se activó al usuario correctamente", "/")

########################################################################
