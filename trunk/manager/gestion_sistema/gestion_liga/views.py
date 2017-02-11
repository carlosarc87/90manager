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
from django.db import transaction
from django.shortcuts import render

from gestion_base.func import (devolver_mensaje, generar_pagina, quitar_acentos,
                               redireccionar)
from gestion_sistema.decorators import actualizar_liga, comprobar_sesion
from gestion_usuario.gestion_notificacion.func import Notificacion, notificar
from gestion_usuario.models import Usuario

from .forms import CambiarFechaForm, LigaForm
from .models import Liga


########################################################################

@login_required
def ver_ligas_publicas(request):
    """ Muestra las ligas publicas que haya en el sistema """
    # Obtenemos las ligas
    ligas = Liga.objects.filter(publica=True, jornada=None)

    for liga in ligas:
        liga.inscritos = liga.equipo_set.all().count()

    d = {"ligas": ligas}
    return render(request, "juego/ligas/ver_ligas_publicas.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['liga_actual'])
@transaction.atomic
def ver_liga(request):
    """ Muestra los datos de una liga determinada """
    # Obtenemos el usuario
    usuario = request.user

    liga = request.session['liga_actual']

    # Obtenemos los equipos que juegan en la liga
    equipos = liga.equipo_set.all()
    equipos = sorted(equipos, key=lambda dato: dato.siglas)

    activada = liga.activada()
    jornada_actual = None
    jornada_anterior = None

    clasificacion = None
    partidos_jornada_actual = None

    liga_acabada = False

    es_creador = (liga.creador == usuario)

    form_fecha = None

    if es_creador:
        if request.method == 'POST':
            form_fecha = CambiarFechaForm(request.POST)

            if form_fecha.is_valid():
                fecha_nueva = form_fecha.cleaned_data['fecha_nueva']
                liga.set_fecha(fecha_nueva)
                return redireccionar('/ligas/ver/%d/' % liga.id)
        else:
            form_fecha = CambiarFechaForm()

    # Comprobamos si el jugador tiene un equipo en esta liga
    equipo_propio = liga.equipo_set.filter(usuario=usuario)
    if len(equipo_propio) > 0:
        equipo_propio = equipo_propio[0]
    else:
        equipo_propio = None

    request.session['equipo_propio'] = equipo_propio

    # Si la liga está activada
    if activada:
        # Comprobamos si la liga ha acabado
        jornada_actual = liga.get_jornada_actual()

        # Si la liga ha acabado
        if jornada_actual is None:
            liga_acabada = True
        else:
            if jornada_actual.numero >= 2:
                jornada_anterior = liga.get_jornadas().get(numero=jornada_actual.numero)
                clasificacion_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
                clasificacion = sorted(clasificacion_sin_ordenar, key=lambda dato: (
                    -dato.puntos, -(dato.goles_favor - dato.goles_contra), -dato.goles_favor))
            elif jornada_actual.numero == 1:  # Generar clasificacion vacía
                clasificacion = jornada_actual.clasificacionequipojornada_set.all()

        if liga_acabada:
            jornada_anterior = liga.get_jornadas()[liga.get_num_jornadas() - 1]
            clasificacion_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
            clasificacion = sorted(clasificacion_sin_ordenar, key=lambda dato: (
                -dato.puntos, -(dato.goles_favor - dato.goles_contra), -dato.goles_favor))
            partidos_jornada_actual = jornada_anterior.partido_set.all()
        else:
            partidos_jornada_actual = jornada_actual.partido_set.all()

        if clasificacion is not None:
            # Calcular variables extra para la clasificación
            posicion = 1

            ultima_posicion_ascenso = 1
            primera_posicion_descenso = len(clasificacion)

            for c in clasificacion:
                c.posicion = posicion

                # Comprobar si es posición de ascenso
                if c.posicion <= ultima_posicion_ascenso:
                    c.posicion_ascenso = True
                else:
                    c.posicion_ascenso = False

                # Comprobar si es posición de descenso
                if c.posicion >= primera_posicion_descenso:
                    c.posicion_descenso = True
                else:
                    c.posicion_descenso = False

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
        else:
            equipos_clasificacion = sorted(equipos, key=lambda dato: quitar_acentos(dato.nombre.lower()))

            clasificacion = []
            posicion = 1

            ultima_posicion_ascenso = 1
            primera_posicion_descenso = len(equipos_clasificacion)

            for equipo_clasificacion in equipos_clasificacion:
                c = type('', (), {})()
                c.posicion = posicion

                c.equipo = equipo_clasificacion

                # Comprobar si es posición de ascenso
                if c.posicion <= ultima_posicion_ascenso:
                    c.posicion_ascenso = True
                else:
                    c.posicion_ascenso = False

                # Comprobar si es posición de descenso
                if c.posicion >= primera_posicion_descenso:
                    c.posicion_descenso = True
                else:
                    c.posicion_descenso = False

                c.goles_diferencia = 0
                c.goles_favor = 0
                c.goles_contra = 0

                c.partidos_jugados = 0
                c.partidos_ganados = 0
                c.partidos_empatados = 0
                c.partidos_perdidos = 0

                c.puntos = 0

                clasificacion.append(c)

                posicion += 1

    # Cargamos la plantilla con los parametros y la devolvemos
    d = {
        "liga": liga,
        "equipos": equipos,
        "jornada_actual": jornada_actual,
        "jornada_anterior": jornada_anterior,
        "partidos_jornada_actual": partidos_jornada_actual,
        "activada": activada,
        "equipo_propio": equipo_propio,
        "clasificacion": clasificacion,
        "liga_acabada": liga_acabada,
        "es_creador": es_creador,
        "form_fecha": form_fecha,
    }
    return generar_pagina(request, "juego/ligas/ver_liga.html", d)


########################################################################

@login_required
def ver_liga_id(request, liga_id):
    if Liga.objects.filter(id=liga_id).count() == 0:
        return devolver_mensaje(request, "Error, no existe una liga con identificador %s" % liga_id, 0)

    # Obtenemos la liga
    liga = Liga.objects.get(id=liga_id)
    request.session['liga_actual'] = liga

    return redireccionar("/ligas/ver/")


########################################################################

@login_required
def crear_liga(request):
    """ Muestra y gestiona el formulario para crear una liga """
    usuario = request.user

    if request.method == 'POST':
        form = LigaForm(request.POST)

        if form.is_valid():
            liga = form.save(commit=False)
            liga.creador = Usuario.objects.get(id=usuario.id)
            liga.factor_tiempo = 24 / liga.factor_tiempo
            liga.save()

            return devolver_mensaje(request, "Se ha creado correctamente", 1, "/ligas/ver/%d/" % liga.id)
    else:
        form = LigaForm()

    d = {"form": form}

    return generar_pagina(request, "juego/ligas/crear_liga.html", d, False)


########################################################################

@login_required
@comprobar_sesion(['liga_actual'])
@transaction.atomic
def activar_liga(request):
    """ Formulario para activar una liga """
    usuario = request.user

    # Obtenemos la liga
    liga = request.session['liga_actual']

    if liga.creador != usuario:
        return devolver_mensaje(request, "Error, solo el creador de la liga puede activarla", 0)

    if liga.activada():
        return devolver_mensaje(request, "Ya esta activada esta liga", 0, "/ligas/ver/%d/" % liga.id)

    equipos = liga.equipo_set.all()

    if request.method == 'POST':
        liga.fecha_real_inicio = datetime.now()
        liga.save()
        liga.rellenar_liga()
        liga.generar_jornadas()

        # Generar primera clasificacion de la liga
        jornada = liga.get_jornada_actual()
        jornada.generar_clasificacion()

        for equipo in liga.equipo_set.exclude(usuario=None):
            notificar(equipo.usuario, tipo=Notificacion.LIGA_ACTIVADA, identificador=liga.id)

        liga.save()

        return devolver_mensaje(request, "Se ha generado la liga correctamente", 1, "/ligas/ver/%d/" % liga.id)

    d = {
        "liga": liga,
        "equipos": equipos
    }

    return generar_pagina(request, "juego/ligas/activar_liga.html", d)

########################################################################
