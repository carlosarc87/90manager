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
from manager.gestion_entrenador import *

import random

########################################################################

def aleatorio(min, max):
	return random.randint(min, max)

########################################################################

def nombreJugadorAleatorio():
	# Crear listas
	lista_nombres = []
	lista_apellidos = []
	
	# Obtener nombres de jugadores
	fich = open("media/doc/nombres_hombres.txt", "r")
	while(True):
		nombre = fich.readline()
		if not nombre: break
		
		lista_nombres.append(nombre)
	
	fich.close()
	
	# Obtener apellidos de jugadores
	fich = open("media/doc/apellidos.txt", "r")
	while(True):
		apellido = fich.readline()
		if not apellido: break
		
		lista_apellidos.append(apellido)
	
	fich.close()
	
	# Poner 1 o 2 nombres
	num_nombres = aleatorio(1, 2)
	nombre_completo = lista_nombres[aleatorio(0, len(lista_nombres) - 1)]
	if(num_nombres == 2):
		nombre_completo += (" " + lista_nombres[aleatorio(0, len(lista_nombres) - 1)])
	
	# Poner 2 apellidos
	apellidos = lista_apellidos[aleatorio(0, len(lista_apellidos) - 1)] + " " + lista_apellidos[aleatorio(0, len(lista_apellidos) - 1)]
	
	# Devolver nombre/s y apellidos
	return nombre_completo + " " + apellidos