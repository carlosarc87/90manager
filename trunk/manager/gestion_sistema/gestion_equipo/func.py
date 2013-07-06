# -*- coding: utf-8 -*-
"""
Copyright 2013 by
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
	# Listas de nombres
	lista_nombres_masc = []
	lista_nombres_fem = []
	
	femeninos = False
	fich = open(RUTA + "public/site_media/doc/" + nombre_fichero, "r")
	while(True):
		linea = fich.readline()
		
		if linea:
			linea = linea[:-1] # Quitar '\n' del final
			
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

def quitar_caracteres_raros(cadena):
	cadena = cadena.replace('á', 'a')
	cadena = cadena.replace('é', 'e')
	cadena = cadena.replace('í', 'i')
	cadena = cadena.replace('ó', 'o')
	cadena = cadena.replace('ú', 'u')
	cadena = cadena.replace('ñ', 'n')
	cadena = cadena.replace('Á', 'A')
	cadena = cadena.replace('É', 'E')
	cadena = cadena.replace('Í', 'I')
	cadena = cadena.replace('Ó', 'O')
	cadena = cadena.replace('Ú', 'U')
	cadena = cadena.replace('Ñ', 'N')
	return cadena

########################################################################

def nombreEquipoAleatorio(lista_nombres_tipo_club, lista_parte1, lista_parte2):
	from random import randint
	
	# Establecer formato del nombre del equipo
	# 1.- [parte 1] + [parte 2]
	# 2.- [tipo_club] + [parte 1] + [parte 2]
	a = randint(1, 2)
	
	# Elegir genero al azar
	g = randint(1, 2)
	
	# Obtener nombres dependiendo del genero
	if g == 1: # Masculino
		parte1 = lista_parte1[0][randint(0, len(lista_parte1[0]) - 1)]
		parte2 = lista_parte2[0][randint(0, len(lista_parte2[0]) - 1)]
	else: # Femenino
		parte1 = lista_parte1[1][randint(0, len(lista_parte1[1]) - 1)]
		parte2 = lista_parte2[1][randint(0, len(lista_parte2[1]) - 1)]
	
	if a == 1:
		nombre_equipo = parte1 + ' ' + parte2
	else:
		tipo_club = lista_nombres_tipo_club[0][randint(0, len(lista_nombres_tipo_club) - 1)]
		nombre_equipo = tipo_club + ' ' + parte1 + ' ' + parte2

	# Devolver nombre_completo
	return nombre_equipo

########################################################################

def generarSiglasNombre(nombre_equipo):
	""" Devuelve unas siglas para el nombre dado """
	# Separar el nombre del equipo en partes a partir de los espacios
	nombre_equipo = quitar_caracteres_raros(nombre_equipo)
	nombre_equipo = nombre_equipo.upper()
	partes = nombre_equipo.split(" ")
	num_partes = len(partes)
	
	if num_partes >= 3:
		return partes[0][0] + partes[num_partes - 2][0] + partes[num_partes - 1][0]
	
	return partes[0][0] + partes[1][0] + partes[1][1]

########################################################################

def ObtenerNombreYSiglasAleatorio(liga):
	# Generar nombre de equipo aleatorio
	# -------------------------------------------------
	# Obtener listas de nombres
	# -------------------------------------------------
	# Tipo club
	lista_nombres_tipo_club = listaNombres('nombres_equipos/tipo_club.txt') # Tipos de club
	lon_lista_nombres_tipo_club = len(lista_nombres_tipo_club)

	# Parte 1
	lista_parte1 = [[], []]

	# Animales
	lista_nombres_animales = listaNombres('nombres_equipos/animales.txt')
	lista_parte1[0] += lista_nombres_animales[0]
	lista_parte1[1] += lista_nombres_animales[1]

	# Comidas
	lista_nombres_comidas = listaNombres('nombres_equipos/comidas.txt')
	lista_parte1[0] += lista_nombres_comidas[0]
	lista_parte1[1] += lista_nombres_comidas[1]

	# Profesiones
	lista_nombres_profesiones = listaNombres('nombres_equipos/profesiones.txt')
	lista_parte1[0] += lista_nombres_profesiones[0]
	lista_parte1[1] += lista_nombres_profesiones[1]

	# Razas
	lista_nombres_razas = listaNombres('nombres_equipos/razas.txt')
	lista_parte1[0] += lista_nombres_razas[0]
	lista_parte1[1] += lista_nombres_razas[1]

	# Objetos
	lista_nombres_objetos = listaNombres('nombres_equipos/objetos.txt')
	lista_parte1[0] += lista_nombres_objetos[0]
	lista_parte1[1] += lista_nombres_objetos[1]

	# Parte 2
	lista_parte2 = [[], []]

	# Colores
	lista_nombres_colores = listaNombres('nombres_equipos/colores.txt')
	lista_parte2[0] += lista_nombres_colores[0]
	lista_parte2[1] += lista_nombres_colores[1]

	# Formas
	lista_nombres_formas = listaNombres('nombres_equipos/formas.txt')
	lista_parte2[0] += lista_nombres_formas[0]
	lista_parte2[1] += lista_nombres_formas[1]
	# -------------------------------------------------

	nombre_aleatorio = ''
	siglas = ''
	for i in range(liga.equipo_set.count(), liga.num_equipos):
		nombre_eq = nombreEquipoAleatorio(lista_nombres_tipo_club, lista_parte1, lista_parte2)
		siglas_eq = generarSiglasNombre(nombre_eq)

		# Comprobar que las siglas no se repitan
		c = 1
		while liga.equipo_set.filter(siglas = siglas_eq).count() > 0:
			siglas_eq = siglas_eq[:-1] + str(c)
			c += 1

		nombre_aleatorio = nombre_eq
		siglas = siglas_eq

	return nombre_aleatorio, siglas

########################################################################
