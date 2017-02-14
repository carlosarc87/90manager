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

from random import randint

from django.db import models, transaction

from gestion_sistema.gestion_calendario.models import Evento
from gestion_sistema.gestion_equipo.models import Equipo
from gestion_sistema.gestion_jornada.models import Jornada
from gestion_sistema.gestion_jugador.models import AtributosVariablesJugador
from gestion_usuario.gestion_notificacion.func import Notificacion, notificar

from .func import probabilidad_exito


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
    # Datos principales
    atributos = models.ForeignKey(AtributosVariablesJugador)
    posicion = models.CharField(max_length=2, choices=POSICIONES)

    def __str__(self):
        """ Devuelve una cadena representativa del objeto """
        return self.posicion + " - " + self.jugador.nombre


########################################################################

class AlineacionEquipo(models.Model):
    """ Representa la alineación de un equipo en un partido """
    equipo = models.ForeignKey(Equipo)
    jugadores = models.ManyToManyField(JugadorPartido, blank=True)

    @transaction.atomic
    def borrar_alineacion(self):
        """ Elimina la alineacion actual """
        for jugador in self.jugadores.all():
            jugador.delete()

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

    @transaction.atomic
    def copiar_alineacion(self, alineacion):
        """ Copia la alineacion desde otra alineacion """
        self.borrar_alineacion()

        for jugador in alineacion.jugadores.all():
            j = JugadorPartido(atributos=jugador.atributos, posicion=jugador.posicion)
            j.save()
            self.jugadores.add(j)

    def get_titulares(self):
        """ Devuelve los jugadores titulares """
        datos = self.get_datos_titulares()
        lista = []
        for dato in datos:
            jugador = dato.atributos.jugador
            lista.append(jugador)
        return lista

    def get_suplentes(self):
        """ Devuelve los jugadores suplentes """
        datos = self.get_datos_suplentes()
        lista = []
        for dato in datos:
            jugador = dato.atributos.jugador
            lista.append(jugador)
        return lista

    def get_delanteros(self):
        """ Devuelve los delanteros del equipo """
        lista = self.jugadores.filter(posicion=JugadorPartido.DELANTERO)
        if len(lista) > 0:
            return lista
        return None

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

    def get_portero(self):
        """ Devuelve al portero del equipo """
        lista = self.jugadores.filter(posicion=JugadorPartido.PORTERO)
        if len(lista) > 0:
            return lista[0]
        return None

    def get_jugadores(self):
        """ Devuelve a todos los jugadores """
        return self.jugadores.all()

    def get_datos_titulares(self):
        """ Devuelve los datos de los titulares """
        return self.jugadores.all().exclude(posicion=JugadorPartido.BANQUILLO)

    def get_datos_suplentes(self):
        """ Devuelve los datos de los suplentes """
        return self.jugadores.filter(posicion=JugadorPartido.BANQUILLO)

    @transaction.atomic
    def set_aleatoria(self):
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

        # --------------------------------------------------------------
        # Comprobar qué formación es con la que el equipo tiene mejor valor
        # --------------------------------------------------------------
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

    def get_valor_anotacion(self):
        valor = 0
        titulares = self.get_datos_titulares()
        for t in titulares:
            posicion = t.posicion
            anotacion = t.atributos.anotacion
            if posicion == "DF":
                valor += (anotacion * 0.25)
            elif posicion == "CC":
                valor += (anotacion * 0.5)
            elif posicion == "DL":
                valor += (anotacion * 0.5)

        if len(titulares) == 0:
            return 0

        return int(valor / len(titulares))

    def get_valor_portero(self):
        titulares = self.get_datos_titulares()
        for t in titulares:
            posicion = t.posicion

            if posicion == "PO":
                return t.atributos.portero

        return 0

    def get_valor_moral(self):
        valor = 0
        titulares = self.get_datos_titulares()
        for t in titulares:
            valor += t.atributos.moral

        if len(titulares) == 0:
            return 0

        return int(valor / len(titulares))


########################################################################

# Partido
class Partido(Evento):
    """ Representa un partido en el sistema """
    # hora_inicio = models.TimeField("Hora de inicio")
    jornada = models.ForeignKey(Jornada)
    equipo_local = models.ForeignKey(Equipo, related_name="Local")
    equipo_visitante = models.ForeignKey(Equipo, related_name="Visitante")

    alineacion_local = models.ForeignKey(AlineacionEquipo, related_name="AlineacionLocal")
    alineacion_visitante = models.ForeignKey(AlineacionEquipo, related_name="AlineacionVisitante")

    goles_local = models.PositiveIntegerField(null=True, blank=True)
    goles_visitante = models.PositiveIntegerField(null=True, blank=True)

    jugado = models.BooleanField(default=False)

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

    def finalizado(self):
        """ Indica si un partido ya ha acabado """
        return self.jugado

    @transaction.atomic
    def jugar(self):
        import time

        ini = time.time()
        ' Juega el partido '
        num_goles = [0, 0]
        lista_sucesos = []

        if not self.alineacion_local.esta_preparada():
            self.alineacion_local.set_aleatoria()

        if not self.alineacion_visitante.esta_preparada():
            self.alineacion_visitante.set_aleatoria()

        # Obtener jugadores titulares y suplentes de los 2 equipos
        # titulares_local = self.alineacion_local.get_datos_titulares()
        # suplentes_local = self.alineacion_local.get_datos_suplentes()
        # titulares_visitante = self.alineacion_visitante.get_datos_titulares()
        # suplentes_visitante = self.alineacion_visitante.get_datos_suplentes()

        alineacion = [self.alineacion_local, self.alineacion_visitante]

        num_parte = 1  # Parte de partido que se está jugando
        equipo_comienza = 0

        # Inicializar variables para el partido
        # --------------------------------------
        # Se incrementa un 10% la moral de los locales
        moral = [(1 + ((alineacion[0].get_valor_moral() - 50) / 500.0)) * 1.1,
                 1 + ((alineacion[1].get_valor_moral() - 50) / 500.0)]

        ataque = [int(alineacion[0].get_valor_ataque() * moral[0]),
                  int(alineacion[1].get_valor_ataque() * moral[1])]

        defensa = [int(alineacion[0].get_valor_defensa() * moral[0]),
                   int(alineacion[1].get_valor_defensa() * moral[1])]

        pases = [int(alineacion[0].get_valor_pases() * moral[0]),
                 int(alineacion[1].get_valor_pases() * moral[1])]

        velocidad = [int(alineacion[0].get_valor_velocidad() * moral[0]),
                     int(alineacion[1].get_valor_velocidad() * moral[1])]

        anotacion = [int(alineacion[0].get_valor_anotacion() * moral[0]),
                     int(alineacion[1].get_valor_anotacion() * moral[1])]

        portero = [int(alineacion[0].get_valor_portero() * moral[0]),
                   int(alineacion[1].get_valor_portero() * moral[1])]

        # --------------------------------------

        mostrar_datos = True
        if mostrar_datos:
            print("-------------------------------------------")
            print(alineacion[0].equipo.nombre)
            print("Moral: " + str(moral[0]))
            print("Ataque: " + str(ataque[0]))
            print("Defensa: " + str(defensa[0]))
            print("Pases: " + str(pases[0]))
            print("Velocidad: " + str(velocidad[0]))
            print("Anotacion: " + str(anotacion[0]))
            print("Portero: " + str(portero[0]))
            print("-------------------------------------------")
            print(alineacion[1].equipo.nombre)
            print("Moral: " + str(moral[1]))
            print("Ataque: " + str(ataque[1]))
            print("Defensa: " + str(defensa[1]))
            print("Pases: " + str(pases[1]))
            print("Velocidad: " + str(velocidad[1]))
            print("Anotacion: " + str(anotacion[1]))
            print("Portero: " + str(portero[1]))
            print("-------------------------------------------")

        fin = time.time()
        print('Tiempo en cargar datos del partido: ' + str("%.3f" % (fin - ini)))

        ini = time.time()
        # Continuar jugando mientras no se hayan acabado las 2 partes del partido
        while num_parte <= 2:
            # Establecer equipo que comienza a jugar la parte
            if num_parte == 1:
                # Sortear equipo que comienza
                equipo_comienza = randint(0, 1)
                id_equipo_atacante = equipo_comienza
                segundos_jugados = 0
            else:
                if equipo_comienza == 0:
                    id_equipo_atacante = 1
                else:
                    id_equipo_atacante = 0
                segundos_jugados = 2700  # 45min * 60seg/min

            if id_equipo_atacante == 0:
                equipo_suceso = self.equipo_local
            else:
                equipo_suceso = self.equipo_visitante

            # Suceso de comienzo de parte
            lista_sucesos.append(
                Suceso(partido=self, segundo_partido=segundos_jugados, tipo=Suceso.COMENZAR, equipo=equipo_suceso))

            # Iniciar variables
            seg_restantes = 2700  # 45min * 60seg/min
            seg_descuento = 0
            tiempo_descuento = False

            # Continuar jugando mientras no se haya acabado el tiempo de la parte actual
            while seg_restantes > 0:
                # Establecer id del defensor
                if id_equipo_atacante == 0:
                    id_equipo_defensor = 1
                else:
                    id_equipo_defensor = 0

                if id_equipo_atacante == 0:
                    equipo_suceso = self.equipo_local
                else:
                    equipo_suceso = self.equipo_visitante

                # Crear jugada
                # Las jugadas tendrán entre 2 y 16 acciones, la mayoría será un valor central.
                num_acciones = (randint(2, 16) + randint(2, 16) + randint(2, 16)) / 3
                seg_accion = 1 + int((100.0 - velocidad[id_equipo_atacante]) / 10) + randint(0, 2)

                # Suceso de contraataque
                if num_acciones <= 5:
                    lista_sucesos.append(
                        Suceso(partido=self, segundo_partido=segundos_jugados, tipo=Suceso.CONTRAATAQUE,
                               equipo=equipo_suceso))

                # print "\t" + "num_acciones: " + str(num_acciones) + " (" + str(seg_accion) + " seg / accion)"
                formula = ataque[id_equipo_atacante] / (10.0 * pases[id_equipo_atacante])
                prob_regate = probabilidad_exito(formula)
                # print "Prob Pase/Regate (" + str(prob_regate) + "%) "
                accion = 1
                while (accion <= num_acciones) and (id_equipo_defensor != id_equipo_atacante):
                    # print "\t" + str(accion) + ".- "

                    # Realizar una de las acciones de la jugada completa
                    # Acciones posibles:
                    # - Movimiento con balón
                    # - Pase
                    # - Regate
                    if accion != num_acciones:
                        # Calcular probabilidad de que la acción sea moverse con el balón, un pase o un regate
                        p = randint(1, 120)
                        # Regate
                        if p <= prob_regate:
                            formula = (1.0 * ataque[id_equipo_atacante] / defensa[id_equipo_defensor])
                            prob_exito = probabilidad_exito(formula)
                            # print "Regate (" + str(prob_exito) + "%) "
                            # Regate fallado
                            if randint(1, 100) > prob_exito:
                                id_equipo_atacante = id_equipo_defensor

                                lista_sucesos.append(
                                    Suceso(partido=self, segundo_partido=segundos_jugados, tipo=Suceso.REGATE, valor=0,
                                           equipo=equipo_suceso))
                            # Regate realizado
                            else:
                                lista_sucesos.append(
                                    Suceso(partido=self, segundo_partido=segundos_jugados, tipo=Suceso.REGATE, valor=1,
                                           equipo=equipo_suceso))
                        # Pase
                        elif p <= 100:
                            formula = (pases[id_equipo_atacante] * 2.0) / (
                                defensa[id_equipo_defensor] + velocidad[id_equipo_defensor])
                            prob_exito = probabilidad_exito(formula)
                            # print "Pase (" + str(prob_exito) + "%) "
                            # Pase fallado
                            if randint(1, 100) > prob_exito:
                                id_equipo_atacante = id_equipo_defensor

                                lista_sucesos.append(
                                    Suceso(partido=self, segundo_partido=segundos_jugados, tipo=Suceso.PASE, valor=0,
                                           equipo=equipo_suceso))
                            # Pase realizado
                            else:
                                lista_sucesos.append(
                                    Suceso(partido=self, segundo_partido=segundos_jugados, tipo=Suceso.PASE, valor=1,
                                           equipo=equipo_suceso))
                        # Moverse con el balón
                        else:
                            # Movimiento realizado
                            lista_sucesos.append(
                                Suceso(partido=self, segundo_partido=segundos_jugados, tipo=Suceso.MOVIMIENTO_BALON,
                                       equipo=equipo_suceso))

                    # Disparo a puerta
                    else:
                        # Calcular probabilidad de que el disparo vaya a portería (95% de la anotación)
                        prob_exito = (20 + anotacion[id_equipo_atacante])
                        if prob_exito > 100:
                            prob_exito = 100
                        prob_exito *= 0.95
                        # print "Prob. disparo a porteria (" + str(prob_exito) + "%) "

                        # Si el balón va a portería
                        if randint(1, 100) <= prob_exito:
                            formula = (1.0 * anotacion[id_equipo_atacante] / portero[id_equipo_defensor])
                            prob_exito = probabilidad_exito(formula)
                            # print "Disparo a puerta (" + str(prob_exito) + "%) "
                            if randint(1, 100) > prob_exito:
                                # Disparo parado
                                lista_sucesos.append(
                                    Suceso(partido=self, segundo_partido=segundos_jugados, tipo=Suceso.DISPARO, valor=1,
                                           equipo=equipo_suceso))
                            # Marcar gol
                            else:
                                num_goles[id_equipo_atacante] += 1

                                # Gol
                                lista_sucesos.append(
                                    Suceso(partido=self, segundo_partido=segundos_jugados, tipo=Suceso.GOL,
                                           equipo=equipo_suceso))

                                # Tiempo perdido en la celebración del gol
                                seg_restantes -= 30
                                segundos_jugados += 30
                                seg_descuento += 30
                        # Fuera
                        else:
                            # Disparo fuera
                            lista_sucesos.append(
                                Suceso(partido=self, segundo_partido=segundos_jugados, tipo=Suceso.DISPARO, valor=0,
                                       equipo=equipo_suceso))

                            seg_descuento += 10

                        # El equipo contrario se hace con el balón
                        id_equipo_atacante = id_equipo_defensor

                    seg_restantes -= seg_accion
                    segundos_jugados += seg_accion
                    accion += 1

                # Minutos de descuento
                if seg_restantes <= 0:
                    if not tiempo_descuento:
                        tiempo_descuento = True
                        min_descuento = 1 + (seg_descuento / 60)
                        seg_restantes += ((min_descuento * 60) + randint(0, 30))

                        lista_sucesos.append(
                            Suceso(partido=self, segundo_partido=segundos_jugados - (segundos_jugados % 60),
                                   tipo=Suceso.TIEMPO_DESCUENTO, valor=min_descuento, equipo=equipo_suceso))
                    else:
                        lista_sucesos.append(
                            Suceso(partido=self, segundo_partido=segundos_jugados, tipo=Suceso.FIN_PARTE,
                                   valor=num_parte, equipo=equipo_suceso))

            num_parte += 1

        fin = time.time()
        print('Tiempo en simular el partido: ' + str("%.3f" % (fin - ini)))

        ini = time.time()
        self.goles_local = num_goles[0]
        self.goles_visitante = num_goles[1]
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

        fin = time.time()
        print('Tiempo en guardar datos del partido: ' + str("%.3f" % (fin - ini)))

        return lista_sucesos

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
    CONTRAATAQUE = 201
    REGATE = 300
    PASE = 301
    DISPARO = 400
    GOL = 666

    TIPO_SUCESOS = (
        (COMENZAR, 'Comienza equipo'),
        (FIN_PARTE, 'Fin de la parte'),
        (TIEMPO_DESCUENTO, 'Tiempo de descuento'),
        (MOVIMIENTO_BALON, 'Movimiento del balon'),
        (CONTRAATAQUE, 'Contrataque'),
        (REGATE, 'Regate'),
        (PASE, 'Pase'),
        (DISPARO, 'Disparo'),
        (GOL, 'Gol'),
    )
    segundo_partido = models.PositiveIntegerField(null=True, blank=True)
    tipo = models.PositiveIntegerField(choices=TIPO_SUCESOS)

    # Valor adicional del suceso (minutos de descuento, que parte ha acabado)
    valor = models.PositiveIntegerField(default=None, null=True, blank=True)

    equipo = models.ForeignKey(Equipo)
    # jugador = models.ForeignKey(Jugador)
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
        if self.valor is not None:
            if self.tipo == Suceso.COMENZAR:
                cadena += "\"" + self.equipo.nombre + "\""
            elif self.tipo == Suceso.REGATE:
                if self.valor == 0:
                    cadena += " fallado"
                elif self.valor == 1:
                    cadena += " realizado"
            elif self.tipo == Suceso.PASE:
                if self.valor == 0:
                    cadena += " fallado"
                elif self.valor == 1:
                    cadena += " realizado"
            elif self.tipo == Suceso.DISPARO:
                if self.valor == 0:
                    cadena += " fuera"
                elif self.valor == 1:
                    cadena += " parado"
            elif self.tipo == Suceso.FIN_PARTE:
                if self.valor == 1:
                    cadena = "Fin de la primera parte"
                else:
                    cadena = "Fin del partido"
            elif self.tipo == Suceso.TIEMPO_DESCUENTO:
                cadena += ": " + str(self.valor) + " minutos"
            else:
                cadena += " " + str(self.valor)
        return cadena

    def get_tiempo(self):
        """ Devuelve el tiempo como una cadena formateada """
        return "%02d:%02d" % (self.get_minuto(), self.get_segundo())

    def __str__(self):
        """ Devuelve una cadena de texto en unicode representando al Suceso """
        return self.get_tiempo() + " - " + self.get_texto()

########################################################################