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

from gestion_base.func import devolver_mensaje, generar_pagina, redireccionar
from gestion_sistema.decorators import actualizar_liga, comprobar_sesion

from .models import Jornada


########################################################################

@login_required
def ver_jornada_id(request, jornada_id):
    """ Muestra los datos de una jornada """
    jornadas = Jornada.objects.filter(id=jornada_id)

    if jornadas.count() == 0:
        return devolver_mensaje(request, "Error, no existe una jornada con identificador %s" % jornada_id, 0)

    request.session['jornada_actual'] = jornadas[0]

    return redireccionar('/jornadas/ver/')


########################################################################

@login_required
@comprobar_sesion(['jornada_actual'])
@actualizar_liga
def ver_jornada(request):
    """ Muestra los datos de una jornada """
    # Obtenemos el usuario
    usuario = request.user

    # Obtenemos la jornada
    jornada_actual = request.session['jornada_actual']

    # Obtenemos la liga
    liga = jornada_actual.liga
    es_creador = liga.creador == usuario

    if jornada_actual.numero > 1:
        jornada_anterior = liga.jornada_set.get(numero=jornada_actual.numero - 1)
    else:
        jornada_anterior = None

    # Si la liga ha acabado
    if not liga.get_jornada_actual():
        liga_acabada = True
    else:
        liga_acabada = False

    # Obtenemos los encuentros que hay
    emparejamientos = jornada_actual.partido_set.all()

    # Obtenemos la clasificacion
    clasificacion_sin_ordenar = jornada_actual.clasificacionequipojornada_set.all()
    clasificacion = sorted(clasificacion_sin_ordenar,
                           key=lambda dato: (-dato.puntos, -(dato.goles_favor - dato.goles_contra), -dato.goles_favor))

    diccionario_equipos_clasificacion = dict()

    posicion = 1
    for c in clasificacion:
        diccionario_equipos_clasificacion[c.equipo] = c
        diccionario_equipos_clasificacion[c.equipo].posicion = posicion

        c.goles_diferencia = c.goles_favor - c.goles_contra

        if jornada_anterior is not None:
            incluida = True

            if not liga_acabada:
                jornada_a_comprobar = jornada_actual
            else:
                jornada_a_comprobar = jornada_anterior
                incluida = True

            c.partidos_ganados = len(c.equipo.get_partidos_ganados(jornada_a_comprobar, incluida))
            c.partidos_empatados = len(c.equipo.get_partidos_empatados(jornada_a_comprobar, incluida))
            c.partidos_perdidos = len(c.equipo.get_partidos_perdidos(jornada_a_comprobar, incluida))

        else:
            c.partidos_ganados = len(c.equipo.get_partidos_ganados(jornada_actual, True))
            c.partidos_empatados = len(c.equipo.get_partidos_empatados(jornada_actual, True))
            c.partidos_perdidos = len(c.equipo.get_partidos_perdidos(jornada_actual, True))

        c.partidos_jugados = c.partidos_ganados + c.partidos_empatados + c.partidos_perdidos

        posicion += 1

    if jornada_anterior is not None and jornada_anterior.jugada:
        clasificacion_anterior_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
        clasificacion_anterior = sorted(clasificacion_anterior_sin_ordenar, key=lambda dato: (
            -dato.puntos, -(dato.goles_favor - dato.goles_contra), -dato.goles_favor))

        posicion = 1
        for c in clasificacion_anterior:
            diccionario_equipos_clasificacion[c.equipo].diferencia_posicion_jornada_anterior = \
                posicion - diccionario_equipos_clasificacion[c.equipo].posicion

            posicion += 1

    # Obtener jornada siguiente
    jornada_siguiente = liga.jornada_set.get(numero=jornada_actual.numero + 1)

    # Obtener si es la jornada actual
    # Es la jornada actual si se no se ha jugado y se jugó la anterior
    if jornada_anterior is not None:
        es_jornada_actual = (jornada_anterior.jugada and not jornada_actual.jugada)
    elif jornada_anterior is None and not jornada_actual.jugada:  # 1º jornada
        es_jornada_actual = True
    else:
        es_jornada_actual = False

    d = {"jornada_actual": jornada_actual,
         "emparejamientos": emparejamientos,
         "liga": liga,
         "usuario": usuario,
         "jornada_anterior": jornada_anterior,
         "jornada_siguiente": jornada_siguiente,
         "clasificacion": clasificacion,
         "es_creador": es_creador,
         "es_jornada_actual": es_jornada_actual,
         "diccionario_equipos_clasificacion": diccionario_equipos_clasificacion
         }
    return generar_pagina(request, "juego/jornadas/ver_jornada.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['liga_actual'])
def ver_jornada_actual(request):
    """ Redirige a la jornada actual de la liga """
    # Obtenemos la liga
    liga = request.session['liga_actual']

    jornada = liga.get_jornada_actual()
    if jornada is None:
        return devolver_mensaje(request, "Error, la liga ya ha finalizado", 0)

    return redireccionar('/jornadas/ver/%s/' % jornada.id)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['liga_actual'])
def listar_jornadas(request):
    """ Muestra las jornadas de la liga """
    # Obtenemos la liga
    liga = request.session['liga_actual']
    jornadas = liga.get_jornadas()

    for jornada in jornadas:
        jornada.partidos_jornada = jornada.partido_set.all()

    d = {
        "liga": liga,
        "jornadas": jornadas
    }

    return generar_pagina(request, "juego/jornadas/listar_liga.html", d)

########################################################################
