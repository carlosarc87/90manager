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

from gestion_base.func import clamp


########################################################################

# Devuelve la probabilidad dada la fórmula
def probabilidad_exito_jugada(formula, posicion_balon):
    # Calcular probabilidad de éxito según la fórmula dada
    v = 120 - (100 / (formula + 1))

    # Calcular probabilidad de éxito según la posición del balón.
    # Cuanto más cerca de la portería rival menor probabilidad de éxito
    v *= (1.5 - posicion_balon)

    # Limitar probabilidad de éxito. Siempre habrá un 1% de probabilidad de fallo
    v = clamp(v, 0, 99)

    return v

########################################################################
