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
from settings import MEDIA_URL

from .models import Jugador


########################################################################

@login_required
def ver_jugador_id(request, jugador_id):
    """ Muestra los datos de un jugador """

    jugadores = Jugador.objects.filter(id=jugador_id)

    if jugadores.count() == 0:
        return devolver_mensaje(request, "Error, no existe un jugador con identificador %s" % jugador_id, 0)

    # Obtenemos el jugador
    request.session['jugador_actual'] = jugadores[0]

    return redireccionar('/jugadores/ver/')


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['jugador_actual'])
def ver_jugador(request):
    """ Muestra los datos de un jugador """
    # Obtenemos el usuario
    usuario = request.user

    jugador = request.session['jugador_actual']

    # Rutas de imágenes de foto
    if jugador.sexo == 'F':
        ruta_imagenes = MEDIA_URL + 'img/jugadores/mujeres/'
        ruta_imagen_foto = ruta_imagenes + 'mujer.png'
    else:
        ruta_imagenes = MEDIA_URL + 'img/jugadores/hombres/'
        ruta_imagen_foto = ruta_imagenes + 'hombre.png'

    ruta_imagen_ojos = ruta_imagenes + 'ojos_' + jugador.color_ojos + '.png'
    ruta_imagen_pelo = ruta_imagenes + 'pelo_' + jugador.color_pelo + '.png'
    ruta_imagen_piel = ruta_imagenes + 'piel_' + jugador.color_piel + '.png'

    # Valor de mercado
    mejor_posicion = jugador.mejor_posicion()

    # Nivel
    nivel = jugador.get_nivel()

    # Valor de mercado
    valor_mercado = jugador.valor_mercado()

    # Obtener edad
    anios, dias = jugador.get_edad()

    # Obtenemos el equipo
    equipo = jugador.atributos.equipo

    # Obtenemos si está en subasta
    subasta = None
    if jugador.atributos.ofertado:
        subasta = jugador.atributos.subasta

    d = {
        "equipo": equipo,
        "usuario": usuario,
        "jugador": jugador,
        "subasta": subasta,
        "anios": anios,
        "dias": dias,
        "ruta_imagen_foto": ruta_imagen_foto,
        "ruta_imagen_ojos": ruta_imagen_ojos,
        "ruta_imagen_pelo": ruta_imagen_pelo,
        "ruta_imagen_piel": ruta_imagen_piel,
        "mejor_posicion": mejor_posicion,
        "nivel": nivel,
        "valor_mercado": valor_mercado,
    }

    return generar_pagina(request, "juego/jugadores/ver_jugador.html", d)

########################################################################
