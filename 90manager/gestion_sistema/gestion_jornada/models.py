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

from django.db import models, transaction

from gestion_sistema.gestion_calendario.models import Evento


########################################################################

# Jornada
class Jornada(Evento):
    """ Representa una jornada en el sistema """
    numero = models.PositiveIntegerField()
    jugada = models.BooleanField(default=False)

    def get_fecha_jornada(self):
        """ Devuelve la fecha en que se juega toda la jornada """
        dia_ini = str(self.fecha_inicio.day)
        dia_fin = str(self.fecha_fin.day)
        mes_ini = str(self.fecha_inicio.month)
        mes_fin = str(self.fecha_fin.month)
        anio_ini = str(self.fecha_inicio.year)
        anio_fin = str(self.fecha_fin.year)

        if anio_ini == anio_fin:
            if mes_ini == mes_fin:
                fecha_jornada = dia_ini + ' - ' + dia_fin + ' de ' + mes_ini + ' de ' + anio_ini
            else:
                fecha_jornada = dia_ini + '/' + mes_ini + ' - ' + dia_fin + '/' + mes_fin + ' de ' + anio_ini
        else:
            fecha_jornada = dia_ini + '/' + mes_ini + '/' + anio_ini + ' - ' + dia_fin + '/' + mes_fin + '/' + anio_fin

        return fecha_jornada

    def get_clasificacion_equipo(self, equipo):
        """ Devuelve la posicion actual de un equipo en la jornada """
        return self.clasificacionequipojornada_set.get(equipo=equipo)

    def quedan_partidos_por_jugar(self):
        """ Devuelve si quedan partidos por jugar """
        return self.partido_set.filter(jugado=False).count() > 0

    @transaction.atomic
    def generar_clasificacion(self):
        """ Genera la clasificacion vacia de la jornada """
        from gestion_sistema.gestion_clasificacion.models import ClasificacionEquipoJornada

        partidos = self.partido_set.all()
        if self.numero == 1:  # Jornada 1
            for partido in partidos:
                clasificacion_local = ClasificacionEquipoJornada(jornada=self, equipo=partido.equipo_local,
                                                                 goles_favor=0, goles_contra=0, puntos=0)
                clasificacion_visitante = ClasificacionEquipoJornada(jornada=self, equipo=partido.equipo_visitante,
                                                                     goles_favor=0, goles_contra=0, puntos=0)

                clasificacion_local.save()
                clasificacion_visitante.save()
        else:
            for partido in partidos:
                jornada_anterior = self.liga.jornada_set.get(numero=int(self.numero) - 1)
                clas_local_anterior = jornada_anterior.clasificacionequipojornada_set.get(equipo=partido.equipo_local)
                clas_visitante_anterior = jornada_anterior.clasificacionequipojornada_set.get(
                    equipo=partido.equipo_visitante)

                clasificacion_local = ClasificacionEquipoJornada(jornada=self, equipo=partido.equipo_local,
                                                                 goles_favor=clas_local_anterior.goles_favor,
                                                                 goles_contra=clas_local_anterior.goles_contra,
                                                                 puntos=clas_local_anterior.puntos)
                clasificacion_visitante = ClasificacionEquipoJornada(jornada=self, equipo=partido.equipo_visitante,
                                                                     goles_favor=clas_visitante_anterior.goles_favor,
                                                                     goles_contra=clas_visitante_anterior.goles_contra,
                                                                     puntos=clas_visitante_anterior.puntos)

                clasificacion_local.save()
                clasificacion_visitante.save()

    @transaction.atomic
    def jugar_partidos_restantes(self):
        import time

        ''' Juega todos los partidos de la jornada que no se han finalizado '''
        partidos = self.partido_set.filter(jugado=False)
        num_partidos = len(partidos)
        suma_tiempo = 0

        for partido in partidos:
            ini = time.time()
            # Jugar partido
            lista_sucesos = partido.jugar()

            fin = time.time()
            total = fin - ini
            print('Tiempo en jugar el partido: ' + str("%.3f" % total))

            # Guardar clasificacion
            # ----------------------------------------------------------
            # Actualizar datos de la clasificacion dependiendo del ganador
            clasificacion_local = partido.jornada.get_clasificacion_equipo(partido.equipo_local)
            clasificacion_visitante = partido.jornada.get_clasificacion_equipo(partido.equipo_visitante)

            # Actualizar los goles
            clasificacion_local.goles_favor += partido.goles_local
            clasificacion_local.goles_contra += partido.goles_visitante
            clasificacion_visitante.goles_favor += partido.goles_visitante
            clasificacion_visitante.goles_contra += partido.goles_local

            # Actualizar las puntuaciones
            if partido.goles_local > partido.goles_visitante:
                clasificacion_local.puntos += 3
            elif partido.goles_local < partido.goles_visitante:
                clasificacion_visitante.puntos += 3
            else:
                clasificacion_local.puntos += 1
                clasificacion_visitante.puntos += 1

            # Guardar los cambios
            clasificacion_local.save()
            clasificacion_visitante.save()
            # ----------------------------------------------------------

            # Guardar sucesos
            for suceso in lista_sucesos:
                suceso.save()

            fin = time.time()
            total = fin - ini
            suma_tiempo += total

            print('Tiempo en completar guardado del partido: ' + str("%.3f" % total))

        if num_partidos > 0:
            print('Promedio tiempo jornada: ' + str("%.3f" % (suma_tiempo / num_partidos)))

        self.jugada = True
        self.save()

    @transaction.atomic
    def mantener_alineaciones(self, jornada_anterior):
        """ Mantiene las alineaciones de los jugadores para los partidos de esta jornada """
        # Cogemos los partidos que tengan algun equipo
        partidos = self.partido_set.exclude(equipo_local__usuario=None, equipo_visitante__usuario=None)

        for partido in partidos:
            if partido.equipo_local is not None:
                equipo = partido.equipo_local
                # Cogemos el partido que jugó la jornada anterior
                qs = jornada_anterior.partido_set.filter(equipo_local=equipo)

                if qs.count() > 0:
                    partido_anterior = qs[0]
                    alineacion_anterior = partido_anterior.alineacion_local
                else:
                    qs = jornada_anterior.partido_set.filter(equipo_visitante=equipo)
                    partido_anterior = qs[0]
                    alineacion_anterior = partido_anterior.alineacion_visitante

                # Una vez que tenemos la alineacion, copiamos para esta
                partido.alineacion_local.copiar_alineacion(alineacion_anterior)

            if partido.equipo_visitante is not None:
                equipo = partido.equipo_visitante
                # Cogemos el partido que jugó la jornada anterior
                qs = jornada_anterior.partido_set.filter(equipo_local=equipo)

                if qs.count() > 0:
                    partido_anterior = qs[0]
                    alineacion_anterior = partido_anterior.alineacion_local
                else:
                    qs = jornada_anterior.partido_set.filter(equipo_visitante=equipo)
                    partido_anterior = qs[0]
                    alineacion_anterior = partido_anterior.alineacion_visitante

                # Una vez que tenemos la alineacion, copiamos para esta
                partido.alineacion_visitante.copiar_alineacion(alineacion_anterior)

            partido.save()

    def __str__(self):
        return 'Jornada ' + str(self.numero) + ' de liga ' + str(self.liga.id)

########################################################################
