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

from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.db.models import F, Q

from gestion_sistema.gestion_liga.models import Liga
from gestion_usuario.models import Usuario


########################################################################

# Equipo
class Equipo(models.Model):
    """ Representa un equipo en el sistema """
    nombre = models.CharField(max_length=50)
    siglas = models.CharField(max_length=3)

    usuario = models.ForeignKey(Usuario, null=True)
    liga = models.ForeignKey(Liga)

    dinero = models.IntegerField(default=0, validators=[MaxValueValidator(999999999999)])

    # Funciones
    def get_jugadores(self):
        """ Devuelve los jugadores del equipo """
        atributos = self.atributosvariablesjugador_set.all()
        jugadores = []

        for atrib in atributos:
            jugadores.append(atrib.jugador)

        return jugadores

    def get_partidos(self, liga):
        """ Devuelve los partidos de una liga en los que juega """
        from gestion_sistema.gestion_partido.models import Partido

        q = Partido.objects.filter(Q(equipo_local=self) | Q(equipo_visitante=self))
        jornadas = list(liga.jornada_set.all())
        lista = q.filter(jornada__in=jornadas)

        return lista

    def get_partidos_hasta_jornada(self, jornada, incluida=False):
        """ Devuelve los partidos jugados hasta la jornada """
        # Obtenemos la liga
        liga = jornada.liga
        # Obtenemos los partidos en los que juega
        partidos = self.get_partidos(liga)

        if not incluida:
            return partidos.filter(jornada__lt=jornada)
        else:
            return partidos.filter(jornada__lte=jornada)

    def get_partidos_empatados(self, jornada, incluida=False):
        """ Devuelve los partidos empatados hasta la jornada """

        partidos = self.get_partidos_hasta_jornada(jornada, incluida)
        partidos_jugados = partidos.filter(jugado=True)
        partidos_empatados = partidos_jugados.filter(goles_local=F('goles_visitante'))

        return partidos_empatados

    def get_partidos_ganados(self, jornada, incluida=False):
        """ Devuelve los partidos ganados hasta la jornada """

        partidos = self.get_partidos_hasta_jornada(jornada, incluida)
        partidos_jugados = partidos.filter(jugado=True)
        partidos_ganados = partidos_jugados.filter(
            Q(Q(equipo_local=self) & Q(goles_local__gt=F('goles_visitante'))) |
            Q(Q(equipo_visitante=self) & Q(goles_local__lt=F('goles_visitante'))))

        return partidos_ganados

    def get_partidos_perdidos(self, jornada, incluida=False):
        """ Devuelve los partidos perdidos hasta la jornada """

        partidos = self.get_partidos_hasta_jornada(jornada, incluida)
        partidos_jugados = partidos.filter(jugado=True)
        partidos_perdidos = partidos_jugados.filter(
            Q(Q(equipo_local=self) & Q(goles_local__lt=F('goles_visitante'))) |
            Q(Q(equipo_visitante=self) & Q(goles_local__gt=F('goles_visitante'))))

        return partidos_perdidos

    def agregar_jugador(self, jugador):
        """ Añade un jugador al equipo """
        self.atributosvariablesjugador_set.add(jugador.atributos)

    def cobrar(self, cantidad):
        """ Cobra una cantidad al equipo """
        self.dinero -= cantidad
        self.save()

    def pagar(self, cantidad):
        """ Paga una cantidad al equipo """
        self.dinero += cantidad
        self.save()

    @transaction.atomic
    def generar_jugadores_aleatorios(self, sexo_permitido=0, num_jugadores_inicial=25, max_nivel=50):
        """ Genera un conjunto de jugadores aleatorios para el equipo """
        from gestion_sistema.gestion_jugador.models import Jugador
        from gestion_sistema.gestion_jugador.func import nombre_jugador_aleatorio, lista_nombres
        from datetime import timedelta
        from random import randint

        edad_min = 18
        edad_max = 35

        hombres_participan = sexo_permitido != 1
        mujeres_participan = sexo_permitido > 0

        # Cargar lista de nombres de jugadores según el sexo
        lista_nombres_hombres = None
        lista_nombres_mujeres = None

        if hombres_participan:
            lista_nombres_hombres = lista_nombres("nombres_hombres.txt")

        if mujeres_participan:
            lista_nombres_mujeres = lista_nombres("nombres_mujeres.txt")

        # Cargar lista de apellidos de jugadores
        lista_apellidos = lista_nombres("apellidos.txt")

        # Generar jugadores
        for j in range(1, num_jugadores_inicial + 1):
            # Establecer posición
            if j % 10 == 1:
                posicion = "PORTERO"
            elif (j % 10 >= 2) and (j % 10 <= 4):
                posicion = "DEFENSA"
            elif (j % 10 >= 5) and (j % 10 <= 7):
                posicion = "CENTROCAMPISTA"
            else:
                posicion = "DELANTERO"

            # Establecer dorsal
            dorsal = j

            # Obtener aleatoriamente datos de hombre o mujer según si participan o no
            if mujeres_participan is False or (hombres_participan and randint(0, 1) == 0):
                lista_nombres = lista_nombres_hombres
                sexo = 'M'
            else:
                lista_nombres = lista_nombres_mujeres
                sexo = 'F'

            # ---------------------------------------------
            # Establecer variables del jugador
            # ---------------------------------------------
            nombre_aleatorio, apodo_aux = nombre_jugador_aleatorio(lista_nombres, lista_apellidos)

            # Calcular datos de la edad del jugador
            fecha_ficticia_inicio = self.liga.fecha_ficticia_inicio.date()
            fecha_nacimiento = \
                fecha_ficticia_inicio - \
                timedelta(randint(edad_min, edad_max) * 365) + \
                timedelta(randint(0, 364))

            edad = fecha_ficticia_inicio - fecha_nacimiento
            anios = int(edad.days / 365.25)

            # Cada 2 años de diferencia con 28 se resta un punto al nivel máximo
            max_nivel_jug = max_nivel - int(abs(28 - anios) / 2)
            # ---------------------------------------------

            # ---------------------------------------------
            # Asignar variables al jugador
            # ---------------------------------------------
            jugador = Jugador(nombre=nombre_aleatorio, apodo=apodo_aux, fecha_nacimiento=fecha_nacimiento, sexo=sexo)
            jugador.save()

            atributos = jugador.generar_atributos(self, dorsal, posicion, max_nivel_jug)
            atributos.save()

            jugador.set_apariencia_aleatoria()

            # Guardar jugador
            jugador.atributos.save()
            jugador.save()

            # Añadir jugador al equipo
            self.agregar_jugador(jugador)
            # ---------------------------------------------

    def __str__(self):
        return self.nombre

########################################################################
