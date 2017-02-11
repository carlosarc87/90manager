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

# Vistas del sistema
from django.contrib.auth.decorators import login_required

from gestion_base.func import (agregar_separadores_miles, devolver_mensaje,
                               generar_pagina, quitar_acentos, redireccionar)
from gestion_sistema.decorators import actualizar_liga, comprobar_sesion

from .forms import EquipoForm
from .models import Equipo


########################################################################

@login_required
def ver_equipo_id(request, equipo_id):
    """ Muestra los datos de un equipo """
    # Obtenemos el usuario
    equipos = Equipo.objects.filter(id=equipo_id)

    if equipos.count() == 0:
        return devolver_mensaje(request, "Error, no existe un equipo con identificador %s" % equipo_id, 0)

    # Obtenemos el equipo
    request.session['equipo_actual'] = equipos[0]

    return redireccionar("/equipos/ver")


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['equipo_actual'])
def ver_equipo(request):
    """ Muestra los datos de un equipo """
    # Obtenemos el usuario
    usuario = request.user

    equipo = request.session['equipo_actual']

    if 'liga_actual' not in request.session:
        request.session['liga_actual'] = equipo.liga

    # Obtenemos los jugadores
    jugadores = equipo.get_jugadores()

    # Obtener datos de los jugadores
    suma_edad = 0
    suma_nivel = 0
    valor_equipo = 0
    for jugador in jugadores:
        # Valor total del equipo
        valor_equipo += jugador.valor_mercado()

        # Edad del equipo
        jugador.anios, jugador.dias = jugador.get_edad()
        jugador.nivel = jugador.get_nivel()
        suma_nivel += jugador.nivel
        suma_edad += jugador.anios + (jugador.dias / 365.0)

    if len(jugadores) > 0:
        edad_media_equipo = "%.2f" % ((suma_edad * 1.0) / len(jugadores))
        nivel_medio_equipo = "%.2f" % ((suma_nivel * 1.0) / len(jugadores))
    else:
        edad_media_equipo = 0
        nivel_medio_equipo = 0

    # Obtenemos la liga
    liga = equipo.liga

    dinero_equipo = agregar_separadores_miles(equipo.dinero)
    valor_equipo = agregar_separadores_miles(valor_equipo)

    d = {
        "usuario": usuario,
        "liga": liga,
        "equipo": equipo,
        "jugadores": jugadores,
        "dinero_equipo": dinero_equipo,
        "valor_equipo": valor_equipo,
        "edad_media_equipo": edad_media_equipo,
        "nivel_medio_equipo": nivel_medio_equipo
    }
    return generar_pagina(request, "juego/equipos/ver_equipo.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['equipo_propio'])
def ver_equipo_propio(request):
    """ Muestra los datos de un equipo """
    # Obtenemos el usuario
    usuario = request.user

    equipo = request.session['equipo_propio']

    # Obtenemos los jugadores
    jugadores = equipo.get_jugadores()

    # Obtener datos de los jugadores
    suma_edad = 0
    suma_nivel = 0
    valor_equipo = 0
    for jugador in jugadores:
        # Valor total del equipo
        valor_equipo += jugador.valor_mercado()

        # Edad del equipo
        jugador.anios, jugador.dias = jugador.get_edad()
        jugador.nivel = jugador.get_nivel()
        suma_nivel += jugador.nivel
        suma_edad += jugador.anios + (jugador.dias / 365.0)

    if len(jugadores) > 0:
        edad_media_equipo = "%.2f" % ((suma_edad * 1.0) / len(jugadores))
        nivel_medio_equipo = "%.2f" % ((suma_nivel * 1.0) / len(jugadores))
    else:
        edad_media_equipo = 0
        nivel_medio_equipo = 0

    # Obtenemos la liga
    liga = equipo.liga

    d = {"usuario": usuario,
         "liga": liga,
         "equipo": equipo,
         "jugadores": jugadores,
         "valor_equipo": valor_equipo,
         "edad_media_equipo": edad_media_equipo,
         "nivel_medio_equipo": nivel_medio_equipo
         }
    return generar_pagina(request, "juego/equipos/ver_equipo.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['liga_actual'])
def crear_equipo(request):
    from gestion_sistema.gestion_equipo.func import obtener_nombre_y_siglas_aleatorio

    ''' Muestra la pagina para crear un equipo '''
    usuario = request.user

    liga = request.session['liga_actual']

    if liga.activada():
        return devolver_mensaje(request, "Esta liga ya no acepta mas equipos", 0, "/ligas/ver/%d/" % liga.id)

    if liga.equipo_set.count() > liga.num_equipos:
        return devolver_mensaje(request, "Esta liga ya está llena", 0, "/ligas/ver/%d/" % liga.id)

    if liga.equipo_set.filter(usuario=usuario).count() > 0:
        return devolver_mensaje(request, "Ya tienes un equipo en esta liga", 0, "/ligas/ver/%d/" % liga.id)

    if request.method == 'POST':
        form = EquipoForm(liga, request.POST)
        if form.is_valid():
            equipo = form.save(commit=False)
            equipo.usuario = usuario
            equipo.liga = liga
            equipo.dinero = liga.dinero_inicial
            equipo.save()
            equipo.generar_jugadores_aleatorios(liga.sexo_permitido, liga.num_jugadores_inicial,
                                                liga.nivel_max_jugadores_inicio)
            return devolver_mensaje(request, "Se ha creado correctamente", 1, "/equipos/ver/%d/" % equipo.id)
    else:
        form = EquipoForm(liga)

    nombre_aleatorio, siglas = obtener_nombre_y_siglas_aleatorio(liga)

    d = {"form": form, "usuario": usuario, "liga": liga, "nombre_aleatorio": nombre_aleatorio, "siglas": siglas}
    return generar_pagina(request, "juego/equipos/crear_equipo.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['liga_actual', 'equipo_propio'])
def listar_equipos_liga(request):
    """ Muestra los equipos de una liga """

    liga = request.session['liga_actual']
    equipo_propio = request.session['equipo_propio']

    # Obtenemos los equipos que juegan en la liga
    equipos = liga.equipo_set.all()
    equipos = sorted(equipos, key=lambda dato: quitar_acentos(dato.nombre.lower()))

    activada = liga.activada()

    # Cargamos la plantilla con los parametros y la devolvemos
    d = {
        "liga": liga,
        "equipos": equipos,
        "activada": activada,
        "equipo_propio": equipo_propio,
    }
    return generar_pagina(request, "juego/equipos/listar_liga.html", d)

########################################################################
