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

from gestion_base.func import quitar_acentos
from settings import MEDIA_ROOT


########################################################################

def lista_nombres(nombre_fichero):
    """ Devuelve una lista con todos los nombres que hay en el fichero dado """
    # Crear lista
    lista_nombres_jugadores = []

    # Obtener nombres
    with open(MEDIA_ROOT + "/doc/" + nombre_fichero, "r", encoding="utf-8") as fich:
        while True:
            nombre = fich.readline()
            nombre = nombre[:-1]  # Quitar '\n'

            if not nombre:
                break

            lista_nombres_jugadores.append(nombre)

        fich.close()

    return lista_nombres_jugadores


########################################################################

def nombre_jugador_aleatorio(lista_nombres_jugadores, lista_apellidos_jugadores):
    from random import randint

    # Poner 1 o 2 nombres
    num_nombres = randint(1, 2)
    nombre1 = lista_nombres_jugadores[randint(0, len(lista_nombres_jugadores) - 1)]
    nombre_completo = nombre1
    aux = quitar_acentos(nombre1)
    apodo = aux[0] + '. '

    # Si se pone un segundo nombre
    if num_nombres == 2 and randint(0, 3) == 0:
        nombre2 = lista_nombres_jugadores[randint(0, len(lista_nombres_jugadores) - 1)]
        nombre_completo = nombre_completo + ' ' + nombre2
        aux = quitar_acentos(nombre2)
        apodo = apodo + aux[0] + '. '

    # Poner 2 apellidos
    apellido1 = lista_apellidos_jugadores[randint(0, len(lista_apellidos_jugadores) - 1)]
    apellido2 = lista_apellidos_jugadores[randint(0, len(lista_apellidos_jugadores) - 1)]
    apellidos = apellido1 + ' ' + apellido2
    apodo = apodo + apellido1

    # Devolver nombre_completo y apodo
    return nombre_completo + ' ' + apellidos, apodo

########################################################################
