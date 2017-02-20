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
from random import randint

from django.db import models, transaction

from gestion_base.func import clamp
from gestion_sistema.gestion_calendario.models import Evento
from gestion_sistema.gestion_equipo.func import jugadores_posicion
from gestion_sistema.gestion_equipo.models import Equipo
from gestion_sistema.gestion_jornada.models import Jornada
from gestion_sistema.gestion_jugador.models import AtributosVariablesJugador, Jugador
from gestion_usuario.gestion_notificacion.func import Notificacion, notificar

from .func import probabilidad_exito_jugada


########################################################################

class JugadorPartido(models.Model):
    """ Represente la posicion de un jugador en un partido """
    BANQUILLO = 'BA'
    PORTERO = 'PO'
    DEFENSA = 'DF'
    CENTROCAMPISTA = 'CC'
    DELANTERO = 'DL'

    POSICIONES = (
        (BANQUILLO, 'BANQUILLO'),
        (PORTERO, 'PORTERO'),
        (DEFENSA, 'DEFENSA'),
        (CENTROCAMPISTA, 'CENTROCAMPISTA'),
        (DELANTERO, 'DELANTERO'),
    )

    ''' Representa los atributos de un jugador en un partido '''
    # Atributos del jugador
    atributos = models.ForeignKey(AtributosVariablesJugador)

    # Posición del jugador en un partido
    posicion = models.CharField(max_length=2, choices=POSICIONES)

    # Atributos del jugador en un partido
    atributos_partido = None

    @staticmethod
    def aplicar_estabilidad_habilidad(estabilidad, valor_habilidad):
        max_porcentaje_perdida = 20
        max_perdida_estabilidad = (valor_habilidad / 100) * max_porcentaje_perdida  # 0 - max_porcentaje_perdida
        valor_final = clamp(valor_habilidad - (max_perdida_estabilidad * ((100 - estabilidad) / 100)), 0, 100)

        return valor_final

    @staticmethod
    def aplicar_moral_habilidad(moral, valor_habilidad):
        max_porcentaje_diferencia = 10
        max_diferencia_moral = (valor_habilidad / 100) * max_porcentaje_diferencia  # 0 - max_porcentaje_diferencia
        valor_final = clamp(valor_habilidad + (max_diferencia_moral * ((moral / 100) - 0.5)), 0, 100)

        return valor_final

    def aplicar_cambios_habilidad_campo(self, valor_habilidad):
        valor_habilidad = self.aplicar_estabilidad_habilidad(self.atributos.estabilidad, valor_habilidad)
        valor_habilidad = self.aplicar_moral_habilidad(self.atributos.moral, valor_habilidad)

        return valor_habilidad

    def aplicar_cambios_atributos_partido_inicio_partido(self):
        # Habilidades de campo
        self.atributos_partido.ataque = self.aplicar_cambios_habilidad_campo(self.atributos.ataque)
        self.atributos_partido.defensa = self.aplicar_cambios_habilidad_campo(self.atributos.defensa)
        self.atributos_partido.velocidad = self.aplicar_cambios_habilidad_campo(self.atributos.velocidad)
        self.atributos_partido.pases = self.aplicar_cambios_habilidad_campo(self.atributos.pases)
        self.atributos_partido.anotacion = self.aplicar_cambios_habilidad_campo(self.atributos.anotacion)
        self.atributos_partido.portero = self.aplicar_cambios_habilidad_campo(self.atributos.portero)

    def aplicar_cambios_atributos_partido_inicio_parte(self):
        # Estados
        self.atributos_partido.cansancio = clamp(self.atributos_partido.cansancio - 20, 0, 100)

    def generar_atributos_partido(self):
        self.atributos_partido = type('', (), {})()

        # Habilidades de campo
        self.atributos_partido.ataque = self.atributos.ataque
        self.atributos_partido.defensa = self.atributos.defensa
        self.atributos_partido.velocidad = self.atributos.velocidad
        self.atributos_partido.pases = self.atributos.pases
        self.atributos_partido.anotacion = self.atributos.anotacion
        self.atributos_partido.portero = self.atributos.portero

        # Habilidades físicas
        self.atributos_partido.resistencia = self.atributos.resistencia

        # Habilidades mentales
        self.atributos_partido.agresividad = self.atributos.agresividad
        self.atributos_partido.concentracion = self.atributos.concentracion
        self.atributos_partido.moral = self.atributos.moral

        # Estados
        # TODO self.atributos_partido.cansancio = 0

    def __str__(self):
        """ Devuelve una cadena representativa del objeto """
        return "[" + str(self.posicion) + "] " + self.atributos.jugador.nombre


########################################################################

class AlineacionEquipo(models.Model):
    """ Representa la alineación de un equipo en un partido """
    equipo = models.ForeignKey(Equipo)
    jugadores = models.ManyToManyField(JugadorPartido, blank=True)

    def get_centrocampistas(self):
        """ Devuelve los centrocampistas del equipo """
        lista = self.jugadores.filter(posicion=JugadorPartido.CENTROCAMPISTA)
        if len(lista) > 0:
            return lista
        return None

    def get_defensas(self):
        """ Devuelve los defensas del equipo """
        lista = self.jugadores.filter(posicion=JugadorPartido.DEFENSA)
        if len(lista) > 0:
            return lista
        return None

    def get_delanteros(self):
        """ Devuelve los delanteros del equipo """
        lista = self.jugadores.filter(posicion=JugadorPartido.DELANTERO)
        if len(lista) > 0:
            return lista
        return None

    def get_portero(self):
        """ Devuelve al portero del equipo """
        lista = self.jugadores.filter(posicion=JugadorPartido.PORTERO)
        if len(lista) > 0:
            return lista[0]
        return None

    def get_jugadores(self):
        """ Devuelve a todos los jugadores del equipo """
        return self.jugadores.all()

    def get_suplentes(self):
        """ Devuelve los jugadores suplentes """
        datos = self.get_datos_suplentes()
        lista = []
        for dato in datos:
            jugador = dato.atributos.jugador
            lista.append(jugador)
        return lista

    def get_titulares(self):
        """ Devuelve los jugadores titulares """
        datos = self.get_datos_titulares()
        lista = []
        for dato in datos:
            jugador = dato.atributos.jugador
            lista.append(jugador)
        return lista

    def get_datos_suplentes(self):
        """ Devuelve los datos de los suplentes """
        return self.jugadores.filter(posicion=JugadorPartido.BANQUILLO)

    def get_datos_titulares(self):
        """ Devuelve los datos de los titulares """
        return self.jugadores.all().exclude(posicion=JugadorPartido.BANQUILLO)

    """ Por si se reutiliza en un futuro
    def get_valor_ataque(self):
        valor = 0
        titulares = self.get_datos_titulares()
        for t in titulares:
            posicion = t.posicion
            ataque = t.atributos.ataque

            if posicion == "DF":
                valor += (ataque * 0.25)
            elif posicion == "CC":
                valor += (ataque * 0.5)
            elif posicion == "DL":
                valor += ataque

        if len(titulares) == 0:
            return 0

        return int(valor / len(titulares))

    def get_valor_defensa(self):
        valor = 0
        titulares = self.get_datos_titulares()
        for t in titulares:
            posicion = t.posicion
            defensa = t.atributos.defensa

            if posicion == "DF":
                valor += defensa
            elif posicion == "CC":
                valor += (defensa * 0.5)
            elif posicion == "DL":
                valor += (defensa * 0.25)

        if len(titulares) == 0:
            return 0

        return int(valor / len(titulares))

    def get_valor_pases(self):
        valor = 0
        titulares = self.get_datos_titulares()
        for t in titulares:
            posicion = t.posicion
            pases = t.atributos.pases
            if posicion == "DF":
                valor += (pases * 0.5)
            elif posicion == "CC":
                valor += pases
            elif posicion == "DL":
                valor += (pases * 0.5)

        if len(titulares) == 0:
            return 0

        return int(valor / len(titulares))

    def get_valor_velocidad(self):
        valor = 0
        titulares = self.get_datos_titulares()
        for t in titulares:
            posicion = t.posicion
            velocidad = t.atributos.velocidad

            if posicion == "DF":
                valor += (velocidad * 0.5)
            elif posicion == "CC":
                valor += (velocidad * 0.5)
            elif posicion == "DL":
                valor += (velocidad * 0.5)

        if len(titulares) == 0:
            return 0

        return int(valor / len(titulares))
    """

    @transaction.atomic
    def borrar_alineacion(self):
        """ Elimina la alineacion actual """
        for jugador in self.jugadores.all():
            jugador.delete()

    @transaction.atomic
    def copiar_alineacion(self, alineacion):
        """ Copia la alineacion desde otra alineacion """
        self.borrar_alineacion()

        for jugador in alineacion.jugadores.all():
            j = JugadorPartido(atributos=jugador.atributos, posicion=jugador.posicion)
            j.save()
            self.jugadores.add(j)

    @transaction.atomic
    def set_alineacion(self, portero, defensas, centrocampistas, delanteros, suplentes):
        """ Establece una alineacion de jugadores a partir de los ids """
        self.borrar_alineacion()

        atributos = self.equipo.atributosvariablesjugador_set.get(jugador__id=portero)
        p = JugadorPartido(atributos=atributos, posicion=JugadorPartido.PORTERO)
        p.save()
        self.jugadores.add(p)

        for id_jugador in defensas:
            atributos = self.equipo.atributosvariablesjugador_set.get(jugador__id=id_jugador)
            p = JugadorPartido(atributos=atributos, posicion=JugadorPartido.DEFENSA)
            p.save()
            self.jugadores.add(p)

        for id_jugador in centrocampistas:
            atributos = self.equipo.atributosvariablesjugador_set.get(jugador__id=id_jugador)
            p = JugadorPartido(atributos=atributos, posicion=JugadorPartido.CENTROCAMPISTA)
            p.save()
            self.jugadores.add(p)

        for id_jugador in delanteros:
            atributos = self.equipo.atributosvariablesjugador_set.get(jugador__id=id_jugador)
            p = JugadorPartido(atributos=atributos, posicion=JugadorPartido.DELANTERO)
            p.save()
            self.jugadores.add(p)

        for id_jugador in suplentes:
            atributos = self.equipo.atributosvariablesjugador_set.get(jugador__id=id_jugador)
            p = JugadorPartido(atributos=atributos, posicion=JugadorPartido.BANQUILLO)
            p.save()
            self.jugadores.add(p)

    @staticmethod
    def calcular_mejor_formacion(lista_df, lista_cc, lista_dl):
        """ Devuelve la mejor formación numérica para el equipo dados los jugadores """
        lista_formaciones = [
            [3, 4, 3],
            [3, 5, 2],
            [4, 3, 3],
            [4, 4, 2],
            [4, 5, 1],
            [5, 3, 2],
            [5, 4, 1]
        ]

        # Algoritmo a seguir:
        # 1. Obtener datos de la siguiente formación de la lista.
        # 2. Calcular valores de la formación con los mejores jugadores.
        # 3. Si el valor total de la formación es mejor al de la mejor ya encontrada, sustituirla.

        mejor_formacion = lista_formaciones[0]
        nivel_mejor_formacion = 0

        # Calcular mejor formación a partir de los niveles de los jugadores en cada una.
        for formacion in lista_formaciones:
            nivel_formacion = 0

            for i in range(0, formacion[0]):
                nivel_formacion += lista_df[i].get_nivel("DEFENSA")

            for i in range(0, formacion[1]):
                nivel_formacion += lista_cc[i].get_nivel("CENTROCAMPISTA")

            for i in range(0, formacion[2]):
                nivel_formacion += lista_dl[i].get_nivel("DELANTERO")

            if nivel_formacion > nivel_mejor_formacion:
                mejor_formacion = formacion
                nivel_mejor_formacion = nivel_formacion

        return mejor_formacion

    @transaction.atomic
    def set_aleatoria(self):
        """ Establece una formación aleatoria para el equipo.
            Trata de generar la mejor formación por nivel de jugadores """

        # Borrar alineación
        self.borrar_alineacion()

        # Obtener jugadores del equipo
        jugadores_equipo = self.equipo.atributosvariablesjugador_set.all()

        """
        # Listas para guardar jugadores por posición y poder obtener luego los mejores Cabe la posibilidad de que no
        # haya suficientes jugadores con el mejor nivel en alguna posición (sobre todo en niveles bajos), por lo que
        # es mejor añadir la posibilidad de que los jugadores también jueguen en posiciones que no sean la mejor
        """
        lista_po = sorted(jugadores_equipo,
                          key=lambda atributosvariablesjugador: atributosvariablesjugador.get_nivel('PORTERO'),
                          reverse=True)

        lista_df = sorted(jugadores_equipo,
                          key=lambda atributosvariablesjugador: atributosvariablesjugador.get_nivel('DEFENSA'),
                          reverse=True)

        lista_cc = sorted(jugadores_equipo,
                          key=lambda atributosvariablesjugador: atributosvariablesjugador.get_nivel('CENTROCAMPISTA'),
                          reverse=True)

        lista_dl = sorted(jugadores_equipo,
                          key=lambda atributosvariablesjugador: atributosvariablesjugador.get_nivel('DELANTERO'),
                          reverse=True)

        # Obtener mejor formación
        mejor_formacion = self.calcular_mejor_formacion(lista_df, lista_cc, lista_dl)

        # --------------------------------------------------------------
        # Establecer formación
        # --------------------------------------------------------------

        # Añadir portero
        if len(lista_po) > 0:
            atributos_jugador = lista_po.pop(0)
            lista_po, lista_df, lista_cc, lista_dl = self.eliminar_jugador_listas_posiciones(atributos_jugador,
                                                                                             lista_po,
                                                                                             lista_df, lista_cc,
                                                                                             lista_dl)

            jugador = JugadorPartido(atributos=atributos_jugador, posicion=JugadorPartido.PORTERO)
            jugador.save()
            self.jugadores.add(jugador)

        # Añadir defensas
        for i in range(0, mejor_formacion[0]):
            if len(lista_df) > 0:
                atributos_jugador = lista_df.pop(0)
                lista_po, lista_df, lista_cc, lista_dl = self.eliminar_jugador_listas_posiciones(atributos_jugador,
                                                                                                 lista_po, lista_df,
                                                                                                 lista_cc, lista_dl)

                jugador = JugadorPartido(atributos=atributos_jugador, posicion=JugadorPartido.DEFENSA)
                jugador.save()
                self.jugadores.add(jugador)

        # Añadir centrocampistas
        for i in range(0, mejor_formacion[1]):
            if len(lista_cc) > 0:
                atributos_jugador = lista_cc.pop(0)
                lista_po, lista_df, lista_cc, lista_dl = self.eliminar_jugador_listas_posiciones(atributos_jugador,
                                                                                                 lista_po, lista_df,
                                                                                                 lista_cc, lista_dl)

                jugador = JugadorPartido(atributos=atributos_jugador, posicion=JugadorPartido.CENTROCAMPISTA)
                jugador.save()
                self.jugadores.add(jugador)

        # Añadir delanteros
        for i in range(0, mejor_formacion[2]):
            if len(lista_dl) > 0:
                atributos_jugador = lista_dl.pop(0)
                lista_po, lista_df, lista_cc, lista_dl = self.eliminar_jugador_listas_posiciones(atributos_jugador,
                                                                                                 lista_po, lista_df,
                                                                                                 lista_cc, lista_dl)

                jugador = JugadorPartido(atributos=atributos_jugador, posicion=JugadorPartido.DELANTERO)
                jugador.save()
                self.jugadores.add(jugador)

    # FIN setAleatoria

    @staticmethod
    def eliminar_jugador_listas_posiciones(jugador, lista_po, lista_df, lista_cc, lista_dl):
        if lista_po.count(jugador) != 0:
            lista_po.remove(jugador)

        if lista_df.count(jugador) != 0:
            lista_df.remove(jugador)

        if lista_cc.count(jugador) != 0:
            lista_cc.remove(jugador)

        if lista_dl.count(jugador) != 0:
            lista_dl.remove(jugador)

        return lista_po, lista_df, lista_cc, lista_dl

    def esta_preparada(self):
        return len(self.jugadores.all()) > 0


########################################################################

# Partido
class Partido(Evento):
    """ Representa un partido en el sistema """
    jornada = models.ForeignKey(Jornada)
    equipo_local = models.ForeignKey(Equipo, related_name="Local")
    equipo_visitante = models.ForeignKey(Equipo, related_name="Visitante")

    alineacion_local = models.ForeignKey(AlineacionEquipo, related_name="AlineacionLocal")
    alineacion_visitante = models.ForeignKey(AlineacionEquipo, related_name="AlineacionVisitante")

    goles_local = models.PositiveIntegerField(null=True, blank=True)
    goles_visitante = models.PositiveIntegerField(null=True, blank=True)

    jugado = models.BooleanField(default=False)

    def finalizado(self):
        """ Indica si un partido ya ha acabado """
        return self.jugado

    @staticmethod
    # Precondiciones: La alineación tiene al menos 1 portero, 1 defensa, 1 centrocampista y 1 delantero
    def generar_jugador_jugada(jugadores_partido, jugador_jugada_anterior, posicion_balon):
        # Obtener probabilidades para cada posición de jugador según la posición del balón
        probabilidad_posiciones = {
            "PORTERO":
                clamp((0.35 - posicion_balon), 0, 0.35) / 20,
            "DEFENSA":
                (1 - abs(posicion_balon - 0.2)) / len(jugadores_posicion(jugadores_partido, "DEFENSA")),
            "CENTROCAMPISTA":
                (1 - abs(posicion_balon - 0.6)) / len(jugadores_posicion(jugadores_partido, "CENTROCAMPISTA")),
            "DELANTERO":
                (1 - abs(posicion_balon - 1)) / len(jugadores_posicion(jugadores_partido, "DELANTERO")),
        }

        suma_probabilidades_posiciones = 0
        for dato in probabilidad_posiciones:
            suma_probabilidades_posiciones += probabilidad_posiciones[dato]

        for dato in probabilidad_posiciones:
            probabilidad_posiciones[dato] /= suma_probabilidades_posiciones

        # Obtener posición del jugador que realiza la jugada
        posicion_jugador_jugada = "DELANTERO"
        r = random.uniform(0, 1)

        probabilidad_acumulada = 0
        for dato in probabilidad_posiciones:
            probabilidad_acumulada += probabilidad_posiciones[dato]

            if r < probabilidad_acumulada:
                posicion_jugador_jugada = dato
                break

        # Obtener lista de jugadores posibles según la posición obtenida del jugador de la jugada
        jugadores_posibles = jugadores_posicion(jugadores_partido, posicion_jugador_jugada)

        # Obtener aleatoriamente el id de lista del jugador de la jugada
        id_jugador_aleatorio = 0
        if len(jugadores_posibles) > 1:
            id_jugador_aleatorio = randint(0, len(jugadores_posibles) - 1)

        # Evitar que el nuevo jugador de la jugada coincida con el jugador de la jugada anterior
        if jugador_jugada_anterior is not None and \
                (jugadores_posibles[id_jugador_aleatorio] == jugador_jugada_anterior):
            id_jugador_aleatorio += 1

            if id_jugador_aleatorio >= len(jugadores_posibles):
                id_jugador_aleatorio = 0

        jugador_jugada = jugadores_posibles[id_jugador_aleatorio]

        return jugador_jugada

    @staticmethod
    def generar_num_acciones_jugada(posicion_balon):
        """
        Devuelve el número total de acciones que tendrá una jugada.
        Las jugadas tendrán un número total de acciones dependiendo de la distancia del balón a la portería rival.
        """
        min_acciones = int((randint(1, 4) + randint(1, 4)) / 2)
        max_acciones = int(clamp(30 * (1 - posicion_balon), min_acciones + 4, 30))

        # Generar el número de acciones aleatoriamente intentando que sea un valor central entre min y max.
        num_acciones = int((randint(min_acciones, max_acciones) +
                            randint(min_acciones, max_acciones) +
                            randint(min_acciones, max_acciones)) / 3)

        return num_acciones

    @transaction.atomic
    def jugar(self):
        """ Juega el partido """

        inc_moral_local = 10

        self.goles_local = 0
        self.goles_visitante = 0

        lista_sucesos = []

        # Generar alineaciones aleatorias si no están preparadas
        if not self.alineacion_local.esta_preparada():
            self.alineacion_local.set_aleatoria()

        if not self.alineacion_visitante.esta_preparada():
            self.alineacion_visitante.set_aleatoria()

        # Obtener jugadores titulares de los 2 equipos
        titulares = [
            self.alineacion_local.get_titulares(),
            self.alineacion_visitante.get_titulares()
        ]

        jugadores_partido = [[], []]

        # Calcular atributos de partido para los jugadores
        c = 0
        for titulares_equipo in titulares:
            for jugador_titular in titulares_equipo:
                jugador_partido = JugadorPartido(
                    atributos=jugador_titular.atributos, posicion=jugador_titular.mejor_posicion())

                jugador_partido.generar_atributos_partido()

                # Se incrementa la moral de los locales
                jugador_partido.atributos_partido.moral = \
                    clamp(jugador_partido.atributos_partido.moral + inc_moral_local, 0, 100)

                jugador_partido.aplicar_cambios_atributos_partido_inicio_partido()

                jugadores_partido[c].append(jugador_partido)

            c += 1

        num_parte = 1  # Parte de partido que se está jugando
        equipo_comienza = randint(0, 1)  # Sortear equipo que comienza

        # Continuar jugando mientras no se hayan acabado las 2 partes del partido
        while num_parte <= 2:
            lista_sucesos_parte_partido = self.jugar_parte_partido(num_parte, equipo_comienza, jugadores_partido)
            lista_sucesos += lista_sucesos_parte_partido
            num_parte += 1

        self.jugado = True

        # Crear notificación
        if self.equipo_local.usuario:
            notificar(self.equipo_local.usuario, tipo=Notificacion.PARTIDO_FINALIZADO, identificador=self.id,
                      liga=self.equipo_local.liga)

        if self.equipo_visitante.usuario:
            notificar(self.equipo_visitante.usuario, tipo=Notificacion.PARTIDO_FINALIZADO, identificador=self.id,
                      liga=self.equipo_local.liga)

        # Guardar los cambios
        self.save()

        return lista_sucesos
    
    def jugar_parte_partido(self, num_parte, equipo_comienza, jugadores_partido):
        """ Jugar una parte dada de un partido """
        lista_sucesos = []
        
        # Iniciar variables de la parte del partido
        seg_descuento = 0
        seg_jugados = 0
        seg_restantes = 2700  # 45min * 60seg/min
        tiempo_descuento = False
        posicion_balon = 0.5
    
        # Establecer equipo que comienza a jugar la parte
        if num_parte == 1:
            id_equipo_atacante = equipo_comienza
        else:
            id_equipo_atacante = 1 if (equipo_comienza == 0) else 0
            seg_jugados = 2700  # 45min * 60seg/min
    
        equipo_suceso = self.equipo_local if (id_equipo_atacante == 0) else self.equipo_visitante
    
        # Suceso de comienzo de parte
        lista_sucesos.append(
            Suceso(partido=self, segundo_partido=seg_jugados, tipo=Suceso.COMENZAR, equipo=equipo_suceso))
    
        # Establecer jugador que saca
        jugador_jugada = jugadores_posicion(jugadores_partido[id_equipo_atacante], "DELANTERO")[0]
    
        siguiente_accion = Suceso.PASE
    
        # Continuar jugando mientras no se haya acabado el tiempo de la parte actual
        while seg_restantes > 0:
            id_equipo_atacante = 1 if (id_equipo_atacante == 0) else 0
            posicion_balon = 1 - posicion_balon

            num_acciones = self.generar_num_acciones_jugada(posicion_balon)

            seg_jugada, seg_descuento_jugada = self.jugar_jugada_partido(
                jugadores_partido, lista_sucesos, id_equipo_atacante,
                num_acciones, posicion_balon, seg_jugados, siguiente_accion, jugador_jugada)

            seg_descuento += seg_descuento_jugada
            seg_jugados += seg_jugada
            seg_restantes -= seg_jugada

            # Minutos de descuento
            if seg_restantes <= 0:
                if not tiempo_descuento:
                    tiempo_descuento = True
                    min_descuento = int(seg_descuento / 60)
                    seg_restantes += ((min_descuento * 60) + randint(0, 30))

                    lista_sucesos.append(
                        Suceso(partido=self, segundo_partido=seg_jugados - (seg_jugados % 60),
                               tipo=Suceso.TIEMPO_DESCUENTO, valor=min_descuento))
                else:
                    lista_sucesos.append(
                        Suceso(partido=self, segundo_partido=seg_jugados, tipo=Suceso.FIN_PARTE,
                               valor=num_parte))

        return lista_sucesos

    def jugar_jugada_partido(self, jugadores_partido, lista_sucesos, id_equipo_atacante,
                             num_acciones, posicion_balon, seg_jugados, siguiente_accion, jugador_jugada):
        mostrar_datos = True

        id_equipo_defensor = 1 if (id_equipo_atacante == 0) else 0
        equipo_suceso = self.equipo_local if (id_equipo_atacante == 0) else self.equipo_visitante

        seg_jugada = 0
        seg_descuento_jugada = 0

        accion = 1

        while (accion <= num_acciones) and (id_equipo_defensor != id_equipo_atacante):
            # Obtener valor de movimiento del balón según el número de acción (0 - 1)
            valor_accion = (accion - 1) / (num_acciones - 1) if num_acciones > 1 else 0

            # Obtener valor de movimiento del balón según los atributos de partido del jugador que lo realiza (0 - 1)
            # Saque de puerta
            if jugador_jugada == jugadores_posicion(jugadores_partido[id_equipo_atacante], "PORTERO")[0]:
                valor_movimiento_jugador_jugada = (random.uniform(0.2, 0.8) + random.uniform(0.2, 0.8)) / 2
            else:
                valor_movimiento_jugador_jugada = random.uniform(
                    -jugador_jugada.atributos_partido.defensa,
                    jugador_jugada.atributos_partido.ataque
                ) / 100

            dif_posicion_accion = (1 - posicion_balon) * \
                                  ((valor_accion + valor_movimiento_jugador_jugada) / 2)

            posicion_balon = clamp(posicion_balon + dif_posicion_accion, 0, 1)

            max_seg_accion = 6 + int((100.0 - jugador_jugada.atributos_partido.velocidad) / 20)
            seg_accion = randint(2, max_seg_accion)

            if mostrar_datos:
                print("\t" + str(accion) + "/" + str(num_acciones) + " | " + str("%.2f" % posicion_balon))

            # Realizar una de las acciones de la jugada completa
            # Acciones posibles:
            # - Regate (0 - X; X <= 100)
            # - Pase (X - 100; X <= 100)
            # - Movimiento con balón (101 - 120)
            # - Balón fuera (121 - 130)
            if accion != num_acciones:
                # Calcular probabilidad de que la acción sea moverse con el balón, un pase o un regate
                p = randint(1, 130)

                formula = jugador_jugada.atributos_partido.ataque / (10.0 * jugador_jugada.atributos_partido.pases)
                prob_regate = probabilidad_exito_jugada(formula, posicion_balon)

                # Regate
                if (siguiente_accion == Suceso.REGATE) or (siguiente_accion is None and p <= prob_regate):
                    jugador_rival_jugada = self.generar_jugador_jugada(
                        jugadores_partido[id_equipo_defensor], None, 1 - posicion_balon)

                    formula = (jugador_jugada.atributos_partido.ataque + jugador_jugada.atributos_partido.velocidad) / \
                              (jugador_rival_jugada.atributos_partido.defensa
                               + jugador_rival_jugada.atributos_partido.velocidad)

                    prob_exito = probabilidad_exito_jugada(formula, posicion_balon)

                    # Regate fallado
                    if randint(1, 100) > prob_exito:
                        lista_sucesos.append(
                            Suceso(partido=self, segundo_partido=seg_jugados, tipo=Suceso.REGATE, valor=0,
                                   equipo=equipo_suceso, jugador=jugador_jugada.atributos.jugador))

                        if mostrar_datos:
                            print("\t" + str(jugador_jugada) + ". "
                                  + "Regate fallado (" + str("%.2f" % prob_exito) + "%) contra "
                                  + str(jugador_rival_jugada))

                        # El equipo contrario se hace con el balón
                        id_equipo_atacante = id_equipo_defensor

                        jugador_jugada = jugador_rival_jugada

                    # Regate realizado
                    else:
                        lista_sucesos.append(
                            Suceso(partido=self, segundo_partido=seg_jugados, tipo=Suceso.REGATE, valor=1,
                                   equipo=equipo_suceso, jugador=jugador_jugada.atributos.jugador))

                        if mostrar_datos:
                            print("\t" + str(jugador_jugada) + ". "
                                  + "Regate realizado (" + str("%.2f" % prob_exito) + "%) contra "
                                  + str(jugador_rival_jugada))

                    siguiente_accion = None

                # Pase
                elif (siguiente_accion == Suceso.PASE) or (siguiente_accion is None and p <= 100):
                    jugador_rival_jugada = self.generar_jugador_jugada(
                        jugadores_partido[id_equipo_defensor], None, 1 - posicion_balon)

                    formula = (jugador_jugada.atributos_partido.pases * 2.0) / \
                              (jugador_rival_jugada.atributos_partido.defensa +
                               jugador_rival_jugada.atributos_partido.velocidad)
                    prob_exito = probabilidad_exito_jugada(formula, posicion_balon)

                    valor_aleatorio = randint(1, 100 + int((1.1 - posicion_balon) * 40))

                    # Pase realizado
                    if valor_aleatorio <= prob_exito or valor_aleatorio > 100:
                        lista_sucesos.append(
                            Suceso(partido=self, segundo_partido=seg_jugados, tipo=Suceso.PASE, valor=1,
                                   equipo=equipo_suceso, jugador=jugador_jugada.atributos.jugador))

                        if mostrar_datos:
                            # Pase realizado contra rival
                            if valor_aleatorio > 100:
                                print("\t" + str(jugador_jugada) + ". "
                                      + "Pase realizado (" + str("%.2f" % prob_exito) + "%) contra "
                                      + str(jugador_rival_jugada))
                            # Pase realizado sin rival
                            else:
                                print("\t" + str(jugador_jugada) + ". "
                                      + "Pase realizado sin rival")

                        # Calcular jugador que recibe el pase
                        jugador_jugada = self.generar_jugador_jugada(
                            jugadores_partido[id_equipo_atacante], jugador_jugada, posicion_balon)

                    # Pase fallado
                    else:
                        lista_sucesos.append(
                            Suceso(partido=self, segundo_partido=seg_jugados, tipo=Suceso.PASE, valor=0,
                                   equipo=equipo_suceso, jugador=jugador_jugada.atributos.jugador))

                        if mostrar_datos:
                            print("\t" + str(jugador_jugada) + ". "
                                  + "Pase fallado (" + str("%.2f" % prob_exito) + "%) contra "
                                  + str(jugador_rival_jugada))

                        # El equipo contrario se hace con el balón
                        id_equipo_atacante = id_equipo_defensor

                        jugador_jugada = jugador_rival_jugada

                    siguiente_accion = None

                # Moverse con el balón
                elif p <= 120:
                    # Movimiento realizado
                    lista_sucesos.append(
                        Suceso(partido=self, segundo_partido=seg_jugados, tipo=Suceso.MOVIMIENTO_BALON,
                               equipo=equipo_suceso, jugador=jugador_jugada.atributos.jugador))

                    if mostrar_datos:
                        print("\t" + str(jugador_jugada) + ". "
                              + "Movimiento realizado")

                    siguiente_accion = None

                # Balón fuera del campo
                else:
                    jugador_jugada = self.generar_jugador_jugada(
                        jugadores_partido[id_equipo_defensor], None, clamp(posicion_balon - 0.5, 0, 1))

                    if mostrar_datos:
                        print("\t" + str(jugador_jugada) + ". "
                              + "Balón fuera")

                    # El equipo contrario se hace con el balón
                    id_equipo_atacante = id_equipo_defensor

                    siguiente_accion = Suceso.PASE

                    seg_accion += 5

            # Disparo a puerta
            else:
                portero_rival = jugadores_posicion(jugadores_partido[id_equipo_defensor], "PORTERO")[0]

                # Calcular probabilidad de que el disparo vaya a portería.
                # Esto dependerá de la anotación (95% de la anotación) y la distancia del disparo a la portería.
                prob_exito = clamp(posicion_balon + 0.1, 0.2, 1) * jugador_jugada.atributos_partido.anotacion * 0.95

                # Si el balón va a portería
                if randint(1, 100) <= prob_exito:
                    formula = (jugador_jugada.atributos_partido.anotacion / portero_rival.atributos_partido.portero)
                    prob_exito = probabilidad_exito_jugada(formula, posicion_balon)

                    if randint(1, 100) > prob_exito:
                        posicion_balon = 1

                        # Disparo parado
                        lista_sucesos.append(
                            Suceso(partido=self, segundo_partido=seg_jugados, tipo=Suceso.DISPARO, valor=1,
                                   equipo=equipo_suceso, jugador=jugador_jugada.atributos.jugador))

                        if mostrar_datos:
                            print("\t" + str(jugador_jugada) + ". "
                                  + "Disparo parado (" + str("%.2f" % prob_exito) + "%) por "
                                  + str(portero_rival))

                        jugador_jugada = portero_rival

                    # Marcar gol
                    else:
                        if id_equipo_atacante == 0:
                            self.goles_local += 1
                        else:
                            self.goles_visitante += 1

                        posicion_balon = 0.5

                        # Gol
                        lista_sucesos.append(
                            Suceso(partido=self, segundo_partido=seg_jugados, tipo=Suceso.GOL,
                                   equipo=equipo_suceso, jugador=jugador_jugada.atributos.jugador))

                        # Tiempo perdido en la celebración del gol
                        seg_accion += 30
                        seg_descuento_jugada += 30

                        if mostrar_datos:
                            print("\t" + str(jugador_jugada) + ". "
                                  + "GOL (" + str("%.2f" % prob_exito) + "%) a "
                                  + str(portero_rival))

                        # Establecer jugador que saca
                        jugador_jugada = jugadores_posicion(jugadores_partido[id_equipo_defensor], "DELANTERO")[0]

                # Fuera
                else:
                    posicion_balon = 1

                    # Disparo fuera
                    lista_sucesos.append(
                        Suceso(partido=self, segundo_partido=seg_jugados, tipo=Suceso.DISPARO, valor=0,
                               equipo=equipo_suceso, jugador=jugador_jugada.atributos.jugador))

                    seg_accion += 10

                    if mostrar_datos:
                        print("\t" + str(jugador_jugada) + ". "
                              + "Disparo fuera (" + str("%.2f" % prob_exito) + "%)")

                    jugador_jugada = portero_rival

                # El equipo contrario se hace con el balón
                id_equipo_atacante = id_equipo_defensor

                siguiente_accion = Suceso.PASE

            seg_jugada += seg_accion
            seg_jugados += seg_accion
            accion += 1

        return seg_jugada, seg_descuento_jugada

    @transaction.atomic
    def __init__(self, *args, **kwargs):
        super(Partido, self).__init__(*args, **kwargs)

        if not self.alineacion_local_id:
            self.alineacion_local = AlineacionEquipo(equipo=self.equipo_local)
            self.alineacion_visitante = AlineacionEquipo(equipo=self.equipo_visitante)
            self.alineacion_local.save()
            self.alineacion_visitante.save()
            self.alineacion_local_id = self.alineacion_local.id
            self.alineacion_visitante_id = self.alineacion_visitante.id

    def __str__(self):
        """ Devuelve una cadena de texto que representa la clase """
        return "Partido de %s contra %s en jornada %d de liga %d" % (
            self.equipo_local.nombre, self.equipo_visitante.nombre, self.jornada.numero, self.jornada.liga.id)


########################################################################

class Suceso(models.Model):
    """ Representa un suceso de un partido (gol, falta, etc) """
    COMENZAR = 100
    FIN_PARTE = 101
    TIEMPO_DESCUENTO = 102
    MOVIMIENTO_BALON = 200
    REGATE = 300
    PASE = 301
    DISPARO = 400
    GOL = 666

    TIPO_SUCESOS = (
        (COMENZAR, 'Comienza equipo'),
        (FIN_PARTE, 'Fin de la parte'),
        (TIEMPO_DESCUENTO, 'Tiempo de descuento'),
        (MOVIMIENTO_BALON, 'Movimiento del balon'),
        (REGATE, 'Regate'),
        (PASE, 'Pase'),
        (DISPARO, 'Disparo'),
        (GOL, 'Gol'),
    )
    segundo_partido = models.PositiveIntegerField(null=True, blank=True)
    tipo = models.PositiveIntegerField(choices=TIPO_SUCESOS)

    # Valor adicional del suceso (minutos de descuento, que parte ha acabado)
    valor = models.PositiveIntegerField(default=None, null=True, blank=True)

    equipo = models.ForeignKey(Equipo, null=True)
    jugador = models.ForeignKey(Jugador, null=True)
    partido = models.ForeignKey(Partido)

    def get_minuto(self):
        """ Devuelve los minutos del suceso """
        return int(self.segundo_partido) / 60

    def get_segundo(self):
        """ Devuelve los segundos del suceso """
        return int(self.segundo_partido) % 60

    def get_texto(self):
        """ Convierte el suceso en una cadena de caracteres """
        cadena = self.get_tipo_display()

        if self.tipo == Suceso.COMENZAR:
            cadena += "\"" + self.equipo.nombre + "\""

        elif self.tipo == Suceso.FIN_PARTE:
            if self.valor == 1:
                cadena = "Fin de la primera parte"
            else:
                cadena = "Fin del partido"

        elif self.tipo == Suceso.TIEMPO_DESCUENTO:
            cadena += ": " + str(self.valor) + " minutos"

        elif self.tipo == Suceso.REGATE:
            if self.valor == 0:
                cadena += " fallado por " + self.jugador.apodo
            elif self.valor == 1:
                cadena += " realizado por " + self.jugador.apodo

        elif self.tipo == Suceso.PASE:
            if self.valor == 0:
                cadena += " fallado por " + self.jugador.apodo
            elif self.valor == 1:
                cadena += " realizado por " + self.jugador.apodo

        elif self.tipo == Suceso.DISPARO:
            if self.valor == 0:
                cadena += " de " + self.jugador.apodo + " fuera"
            elif self.valor == 1:
                cadena += " de " + self.jugador.apodo + " parado"

        elif self.tipo == Suceso.GOL:
            cadena += " de " + self.jugador.apodo

        else:
            cadena += " " + str(self.valor)

        return cadena

    def get_tiempo(self):
        """ Devuelve el tiempo como una cadena formateada """
        return "%02d:%02d" % (self.get_minuto(), self.get_segundo())

    def __str__(self):
        """ Devuelve una cadena de texto representando al Suceso """
        return self.get_tiempo() + " - " + self.get_texto()

########################################################################
