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

from settings import RUTA

########################################################################

def listaNombres(nombre_fichero):
	""" Devuelve una lista con todos los nombres que hay en el fichero dado """
	# Crear lista
	lista_nombres = []

	# Obtener nombres
	fich = open(RUTA + "public/site_media/doc/" + nombre_fichero, "r")
	while(True):
		nombre = fich.readline()
		nombre = nombre[:-1] # Quitar '\n'
		if not nombre:
			break
		lista_nombres.append(nombre)

	fich.close()

	return lista_nombres

########################################################################

def quitar_acentos(cadena):
	cadena = cadena.replace('Á', 'A')
	cadena = cadena.replace('É', 'E')
	cadena = cadena.replace('Í', 'I')
	cadena = cadena.replace('Ó', 'O')
	cadena = cadena.replace('Ú', 'U')
	return cadena

########################################################################

def nombreEquipoAleatorio(lista_nombres_tipo_club, lista_parte1, lista_parte2):
	from random import randint
	
	# Establecer formato del nombre del equipo
	# 1.- [parte 1] + [parte 2]
	# 2.- [tipo_club] + [parte 1] + [parte 2]
	a = randint(1, 2)
	parte1 = lista_parte1[randint(0, len(lista_parte1) - 1)]
	parte2 = lista_parte2[randint(0, len(lista_parte2) - 1)]
	
	if a == 1:
		nombre_equipo = parte1 + ' ' + parte2
		parte1 = quitar_acentos(parte1)
		parte2 = quitar_acentos(parte2)
		siglas = parte1[0] + parte2[0]
	else:
		tipo_club = lista_nombres_tipo_club[randint(0, len(lista_nombres_tipo_club) - 1)]
		nombre_equipo = tipo_club + ' ' + parte1 + ' ' + parte2
		tipo_club = quitar_acentos(tipo_club)
		parte1 = quitar_acentos(parte1)
		parte2 = quitar_acentos(parte2)
		siglas = tipo_club[0] + parte1[0] + parte2[0]

	# Devolver nombre_completo y apodo
	return nombre_equipo, siglas

########################################################################
