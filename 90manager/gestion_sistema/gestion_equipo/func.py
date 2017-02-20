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

from settings import MEDIA_ROOT


########################################################################

def jugadores_posicion(jugadores_partido, posicion):
    """ Devuelve a todos los jugadores de una lista según su posición """

    lista_aux = []

    for jugador_partido in jugadores_partido:
        if jugador_partido.atributos.jugador.mejor_posicion() == posicion:
            lista_aux.append(jugador_partido)

    return lista_aux


########################################################################

def lista_nombres(nombre_fichero):
    """ Devuelve una lista con todos los nombres que hay en el fichero dado """
    # Listas de nombres
    lista_nombres_masc = []
    lista_nombres_fem = []

    femeninos = False

    with open(MEDIA_ROOT + "/doc/" + nombre_fichero, "r", encoding="utf-8") as fich:
        while True:
            linea = fich.readline()

            if linea:
                linea = linea[:-1]  # Quitar '\n' del final

                if linea == "# Femeninos":
                    femeninos = True

                if not linea[0] == '#':
                    if femeninos:
                        lista_nombres_fem.append(linea)
                    else:
                        lista_nombres_masc.append(linea)
            else:
                break

        fich.close()

    return lista_nombres_masc, lista_nombres_fem


########################################################################

def transformar_caracteres_para_siglas(cadena):
    cadena = cadena.upper()

    cadena = cadena.replace('Á', 'A')
    cadena = cadena.replace('É', 'E')
    cadena = cadena.replace('Í', 'I')
    cadena = cadena.replace('Ó', 'O')
    cadena = cadena.replace('Ú', 'U')
    cadena = cadena.replace('Ñ', 'N')

    return cadena


########################################################################

def nombre_equipo_aleatorio(liga, lista_nombres_tipo_club, lista_parte1, lista_parte2, sexo_permitido):
    from random import randint

    # Establecer genero
    if sexo_permitido == 2:  # Equipo mixto
        genero_nombre_equipo = randint(1, 2)
    else:  # Equipo de un solo genero
        genero_nombre_equipo = sexo_permitido + 1

    # Obtener nombres dependiendo del genero
    if genero_nombre_equipo == 1:  # Masculino
        parte1 = lista_parte1[0][randint(0, len(lista_parte1[0]) - 1)]
        parte2 = lista_parte2[0][randint(0, len(lista_parte2[0]) - 1)]
    else:  # Femenino
        parte1 = lista_parte1[1][randint(0, len(lista_parte1[1]) - 1)]
        parte2 = lista_parte2[1][randint(0, len(lista_parte2[1]) - 1)]

    # Establecer formato del nombre del equipo
    # 1.- [parte 1] + [parte 2]
    # 2.- [tipo_club] + [parte 1] + [parte 2]
    formato_nombre_equipo = randint(1, 2)

    if formato_nombre_equipo == 1:
        nombre_equipo = parte1 + ' ' + parte2
    else:
        tipo_club = lista_nombres_tipo_club[0][randint(0, len(lista_nombres_tipo_club) - 1)]
        nombre_equipo = tipo_club + ' ' + parte1 + ' ' + parte2

    # Comprobar que el nombre no se repita
    while liga.equipo_set.filter(nombre=nombre_equipo).count() > 0:
        nombre_equipo = nombre_equipo_aleatorio(liga, lista_nombres_tipo_club, lista_parte1, lista_parte2,
                                                sexo_permitido)

    # Devolver nombre_completo
    return nombre_equipo


########################################################################

def generar_siglas_nombre(liga, nombre_equipo):
    """ Devuelve unas siglas para el nombre dado """
    # Separar el nombre del equipo en partes a partir de los espacios
    nombre_equipo = transformar_caracteres_para_siglas(nombre_equipo)
    partes = nombre_equipo.split(" ")
    num_partes = len(partes)

    if num_partes >= 3:
        siglas_equipo = partes[0][0] + partes[num_partes - 2][0] + partes[num_partes - 1][0]
    else:
        siglas_equipo = partes[0][0] + partes[1][0] + partes[1][1]

    # Comprobar que las siglas no se repitan
    c = 1
    while liga.equipo_set.filter(siglas=siglas_equipo).count() > 0:
        siglas_equipo = siglas_equipo[:-1] + str(c)
        c += 1

    return siglas_equipo


########################################################################

def obtener_nombre_y_siglas_aleatorio(liga):
    # Generar nombre de equipo aleatorio
    # -------------------------------------------------
    # Obtener listas de nombres
    # -------------------------------------------------
    # Tipo club
    lista_nombres_tipo_club = lista_nombres('nombres_equipos/tipo_club.txt')  # Tipos de club

    # Parte 1
    lista_parte1 = [[], []]

    # Animales
    lista_nombres_equipos = lista_nombres('nombres_equipos/animales.txt')
    lista_parte1[0] += lista_nombres_equipos[0]
    lista_parte1[1] += lista_nombres_equipos[1]

    # Comidas
    lista_nombres_equipos = lista_nombres('nombres_equipos/comidas.txt')
    lista_parte1[0] += lista_nombres_equipos[0]
    lista_parte1[1] += lista_nombres_equipos[1]

    # Profesiones
    lista_nombres_equipos = lista_nombres('nombres_equipos/profesiones.txt')
    lista_parte1[0] += lista_nombres_equipos[0]
    lista_parte1[1] += lista_nombres_equipos[1]

    # Razas
    lista_nombres_equipos = lista_nombres('nombres_equipos/razas.txt')
    lista_parte1[0] += lista_nombres_equipos[0]
    lista_parte1[1] += lista_nombres_equipos[1]

    # Objetos
    lista_nombres_equipos = lista_nombres('nombres_equipos/objetos.txt')
    lista_parte1[0] += lista_nombres_equipos[0]
    lista_parte1[1] += lista_nombres_equipos[1]

    # Parte 2
    lista_parte2 = [[], []]

    # Apariencias
    lista_nombres_equipos = lista_nombres('nombres_equipos/apariencias.txt')
    lista_parte2[0] += lista_nombres_equipos[0]
    lista_parte2[1] += lista_nombres_equipos[1]

    # Atributos
    lista_nombres_equipos = lista_nombres('nombres_equipos/atributos.txt')
    lista_parte2[0] += lista_nombres_equipos[0]
    lista_parte2[1] += lista_nombres_equipos[1]

    # Caracteres
    lista_nombres_equipos = lista_nombres('nombres_equipos/caracteres.txt')
    lista_parte2[0] += lista_nombres_equipos[0]
    lista_parte2[1] += lista_nombres_equipos[1]

    # Colores
    lista_nombres_equipos = lista_nombres('nombres_equipos/colores.txt')
    lista_parte2[0] += lista_nombres_equipos[0]
    lista_parte2[1] += lista_nombres_equipos[1]

    # Estados
    lista_nombres_equipos = lista_nombres('nombres_equipos/estados.txt')
    lista_parte2[0] += lista_nombres_equipos[0]
    lista_parte2[1] += lista_nombres_equipos[1]

    # Formas
    lista_nombres_equipos = lista_nombres('nombres_equipos/formas.txt')
    lista_parte2[0] += lista_nombres_equipos[0]
    lista_parte2[1] += lista_nombres_equipos[1]
    # -------------------------------------------------

    nombre_aleatorio = ''
    siglas = ''
    for i in range(liga.equipo_set.count(), liga.num_equipos):
        nombre_eq = nombre_equipo_aleatorio(liga, lista_nombres_tipo_club, lista_parte1, lista_parte2,
                                            liga.sexo_permitido)
        siglas_eq = generar_siglas_nombre(liga, nombre_eq)

        nombre_aleatorio = nombre_eq
        siglas = siglas_eq

    return nombre_aleatorio, siglas

########################################################################
