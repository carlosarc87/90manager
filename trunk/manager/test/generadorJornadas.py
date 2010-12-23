# -*- coding: utf-8 -*-
# Prueba para generar jornadas

import random

num_equipos = 6;

jornadas = []

num_jornadas_ida = num_equipos - 1

num_emparejamientos_jornada = num_equipos / 2

id_equipos = range(1, num_equipos + 1)

random.seed(0)

random.shuffle(id_equipos)

# Crear jornadas de ida
j = 0
while j < num_jornadas_ida:
	emparejamientos_jornada = []
	for emp in range(0, num_emparejamientos_jornada):
		emparejamiento = [id_equipos[emp], id_equipos[num_equipos - emp - 1]]
		emparejamientos_jornada.append(emparejamiento)
	# Annadir todos los emparejamientos a la jornada
	jornadas.append(emparejamientos_jornada)
	
	# Colocar segundo equipo al final del vector. El primer equipo siempre queda fijo
	equipo_pal_fondo = id_equipos.pop(1)
	id_equipos.append(equipo_pal_fondo)
	
	j += 1
	

ultima_jornada = num_jornadas_ida * 2
while (j < ultima_jornada):
	emparejamientos_jornada = []
	for emp in range(0, num_emparejamientos_jornada):
		emparejamiento = [jornadas[j - num_jornadas_ida][emp][1], jornadas[j - num_jornadas_ida][emp][0]]
		emparejamientos_jornada.append(emparejamiento)
	# Annadir todos los emparejamientos a la jornada
	jornadas.append(emparejamientos_jornada)
	j += 1

for i in range(0, len(jornadas)):
	print "Jornada numero: %d" % i
	for emparejamiento in jornadas[i]:
		print emparejamiento
  