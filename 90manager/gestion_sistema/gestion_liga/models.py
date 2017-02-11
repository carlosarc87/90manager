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

import random
from datetime import datetime, timedelta
from math import ceil

from django.core.validators import MaxValueValidator
from django.db import models, transaction

from gestion_usuario.models import Usuario


########################################################################

# Liga
class Liga(models.Model):
    """ Representa una liga """
    creador = models.ForeignKey(Usuario)
    nombre = models.CharField(max_length=50)
    num_equipos = models.PositiveIntegerField(null=True, default=0)
    publica = models.BooleanField(default=True)  # Visibilidad de la liga

    # Fecha en la que se activa la liga
    fecha_real_inicio = models.DateTimeField(null=True)

    # Fecha (ficticia) en la que comienza la liga
    fecha_ficticia_inicio = models.DateTimeField(null=True)

    # Factor de tiempo de las ligas
    factor_tiempo = models.PositiveIntegerField(default=1)

    # Reglas liga
    sexo_permitido = models.PositiveIntegerField(
        default=0)  # Sexo permitido (0 = Solo hombres, 1 = Solo mujeres, 2 = Mixto)
    permitir_bots = models.BooleanField(default=True)  # Indica si se permiten (1) o no (0) bots en las ligas
    inteligencia_bots = models.PositiveIntegerField(default=3,
                                                    null=True)  # Nivel de inteligencia de los bots (1 - 5(muy alto))
    tipo_avance_jornadas = models.PositiveIntegerField(
        default=0)  # Tipo de avance de las jornadas (0 = Manual, 1 = Auto, 2 = Esperar hora)

    # Reglas equipos
    dinero_inicial = models.IntegerField(default=20000, validators=[MaxValueValidator(999999999999)])
    num_jugadores_inicial = models.PositiveIntegerField(default=20, validators=[MaxValueValidator(100)])
    nivel_max_jugadores_inicio = models.PositiveIntegerField(default=50, validators=[
        MaxValueValidator(100)])  # Nivel máximo inicial de los jugadores al comienzo de la liga (10 - 100)

    def set_fecha(self, nueva_fecha):
        """ Establece una fecha de la liga """
        dif_f = self.get_fecha() - nueva_fecha
        dif_r = dif_f / self.factor_tiempo
        self.fecha_real_inicio += dif_r
        self.save()

    def get_fecha(self):
        """ Devuelve la fecha ficticia de la liga """
        ahora_real = datetime.now()
        fecha_real_inicio = self.fecha_real_inicio
        factor = self.factor_tiempo
        t_real_transcurrida = ahora_real - fecha_real_inicio.replace(tzinfo=None)
        t_ficticio_transcurrida = t_real_transcurrida * int(factor)

        ahora_ficticia = self.fecha_ficticia_inicio + t_ficticio_transcurrida

        return ahora_ficticia

    def get_jornadas(self):
        """ Devuelve todas las jornadas de la liga """
        return self.jornada_set.all()

    def activada(self):
        """ Devuelve si una liga ya ha empezado a jugarse """
        return self.fecha_real_inicio is not None

    def get_jornada_actual(self):
        """ Devuelve la jornada actual de la liga o None en caso de haber acabado """
        # Obtenemos las jornadas no jugadas
        jornadas_restantes = self.get_jornadas().filter(jugada=False)
        jornada_actual = None

        if len(jornadas_restantes) > 0:
            # No ha acabado aun
            jornada_actual = jornadas_restantes[0]

        return jornada_actual

    @transaction.atomic
    def rellenar_liga(self):
        """ Rellena los huecos vacios de una liga con equipos controlados por bots """
        from gestion_sistema.gestion_equipo.func import obtener_nombre_y_siglas_aleatorio
        from gestion_sistema.gestion_equipo.models import Equipo

        for i in range(self.equipo_set.count(), int(self.num_equipos)):
            nombre_equipo, siglas_equipo = obtener_nombre_y_siglas_aleatorio(self)

            equipo = Equipo(nombre=nombre_equipo, siglas=siglas_equipo, usuario=None, liga=self,
                            dinero=self.dinero_inicial)
            equipo.save()
            equipo.generar_jugadores_aleatorios(self.sexo_permitido, self.num_jugadores_inicial,
                                                self.nivel_max_jugadores_inicio)

    @transaction.atomic
    def generar_jornadas(self):
        """ Genera las jornadas de una liga """
        from gestion_sistema.gestion_jornada.models import Jornada
        from gestion_sistema.gestion_partido.models import Partido
        import math

        jornadas = []
        num_jornadas_ida = int(self.num_equipos) - 1
        num_emparejamientos_jornada = math.ceil(int(self.num_equipos) / 2)

        # Creamos una copia de los equipos
        id_equipos = list(self.equipo_set.all())
        random.shuffle(id_equipos)

        # Crear jornadas de la ida
        j = 0
        while j < num_jornadas_ida:
            emparejamientos_jornada = []

            for emp in range(0, num_emparejamientos_jornada):
                # Alternar local y visitante
                if (j % 2) == 0:
                    emparejamiento = [id_equipos[self.num_equipos - emp - 1], id_equipos[emp]]
                else:
                    emparejamiento = [id_equipos[emp], id_equipos[self.num_equipos - emp - 1]]

                # Annadir emparejamiento a la lista de emparejamientos de la jornada
                emparejamientos_jornada.append(emparejamiento)

            # Añadir todos los emparejamientos a la jornada
            jornadas.append(emparejamientos_jornada)

            # Colocar segundo equipo al final del vector. El primer equipo siempre queda fijo
            equipo_pal_fondo = id_equipos.pop(1)
            id_equipos.append(equipo_pal_fondo)
            j += 1

        # Jornadas de la vuelta
        ultima_jornada = num_jornadas_ida * 2
        while j < ultima_jornada:
            emparejamientos_jornada = []
            for emp in range(0, num_emparejamientos_jornada):
                emparejamiento = [jornadas[j - num_jornadas_ida][emp][1], jornadas[j - num_jornadas_ida][emp][0]]
                emparejamientos_jornada.append(emparejamiento)

            # Annadir todos los emparejamientos a la jornada
            jornadas.append(emparejamientos_jornada)
            j += 1

        # Generar las fechas para una jornada
        # Datos base
        l_dias = [0, 0, 0, 0, 0, 1, 1]
        primera_hora = 18 * 4
        ultima_hora = 22 * 4
        partidos = list(range(num_emparejamientos_jornada))

        # Generamos los ordenes de una jornada
        dias_jugables = l_dias.count(1)
        partidos_por_dia = int(ceil(len(partidos) * 1.0 / dias_jugables))
        huecos = (ultima_hora - primera_hora)
        if partidos_por_dia > 1:
            espacio_entre_partidos = huecos / (partidos_por_dia - 1)
        else:
            espacio_entre_partidos = 0

        orden_jornada = []
        indice_partido = 0
        dia_inicio = self.fecha_ficticia_inicio.weekday()
        for dia in range(len(l_dias)):
            dia_actual = dia + dia_inicio
            if l_dias[dia_actual % len(l_dias)]:
                lista_partidos = []
                for partido in range(partidos_por_dia):
                    hora = (partido % huecos) * espacio_entre_partidos
                    lista_partidos.append([hora, (indice_partido * partidos_por_dia) + partido])
                indice_partido += 1
                orden_jornada.append([dia_actual, lista_partidos])

        # Guardar jornadas y partidos
        for i in range(len(jornadas)):
            jornada = Jornada(liga=self, numero=i + 1, jugada=False)
            jornada.fecha_inicio = self.fecha_ficticia_inicio + timedelta(days=i * 7)
            jornada.fecha_fin = jornada.fecha_inicio + timedelta(days=7)
            jornada.save()

            for siguiente_dia, orden_dia in orden_jornada:
                fecha = jornada.fecha_inicio + timedelta(days=siguiente_dia - dia_inicio)
                for enfrentamiento in orden_dia:
                    if enfrentamiento[1] < len(jornadas[i]):
                        emparejamiento = jornadas[i][enfrentamiento[1]]
                        partido = Partido(liga=self, jornada=jornada, equipo_local=emparejamiento[0],
                                          equipo_visitante=emparejamiento[1], jugado=False)
                        hora = fecha + timedelta(hours=18 + (enfrentamiento[0] / 4),
                                                 minutes=15 * (enfrentamiento[0] % 4))
                        partido.fecha_inicio = hora
                        partido.fecha_fin = partido.fecha_inicio + timedelta(hours=2)
                        partido.save()

    def agregar_equipo(self, equipo):
        """ Agrega un equipo a la liga """
        self.equipos_set.add(equipo)

    @transaction.atomic
    def avanzar_jornada(self):
        """ Avanza una jornada en la liga """
        # Sacar primera jornada no jugada
        jornada = self.get_jornada_actual()
        if not jornada:
            return False

        print("Jugando partidos restantes")
        jornada.jugar_partidos_restantes()

        """
        # Actualizar subastas
        #		print "Actualizando subastas"
        #		for subasta in self.subasta_set.all():
        #			subasta.expira -= 1
        #			if subasta.expira == 0:
        #				# Completar el traslado
        #				subasta.finalizar()
        #				subasta.delete()
        #			else:
        #				subasta.save()
        """

        # Generar los datos de clasificacion de la siguiente jornada
        print("Generando clasificaciones")
        siguiente_jornada = self.get_jornada_actual()
        if siguiente_jornada:
            siguiente_jornada.generar_clasificacion()
            siguiente_jornada.mantener_alineaciones(jornada)
        print("Fin")
        return True

    def get_num_jornadas(self):
        """ Devuelve el número de jornadas que tiene la liga """
        return self.get_jornadas().count()

    def __str__(self):
        """ Devuelve una cadena de texto que representa la clase """
        return self.nombre

########################################################################
