# -*- coding: utf-8 -*-
# Formularios del sistema. Los que deriven de una clase son rápidos de
# crear.
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

from django import forms


########################################################################

class PrepararEquipoForm(forms.Form):
    """ Formulario de preparacion de equipos locales """
    jugadores_disponibles = forms.fields.MultipleChoiceField(required=False)
    defensas = forms.fields.MultipleChoiceField()
    centrocampistas = forms.fields.MultipleChoiceField()
    portero = forms.fields.ChoiceField()
    delanteros = forms.fields.MultipleChoiceField()
    suplentes = forms.fields.MultipleChoiceField(required=False)

    def __init__(self, alineacion, equipo, *args, **kwargs):
        """ Constructor que establece la lista de valores de los titulares """
        super(PrepararEquipoForm, self).__init__(*args, **kwargs)

        # Establecemos los valores de la lista multiple como los jugadores del equipo local
        jugadores = equipo.get_jugadores()
        lista_jugadores = [[choice.id, choice.nombre] for choice in jugadores]

        self.fields['jugadores_disponibles'].choices = lista_jugadores
        self.fields['defensas'].choices = lista_jugadores
        self.fields['centrocampistas'].choices = lista_jugadores
        self.fields['delanteros'].choices = lista_jugadores
        self.fields['suplentes'].choices = lista_jugadores

        valor_nulo = [0, "Nadie"]
        lista_porteros = list(lista_jugadores)
        lista_porteros.insert(0, valor_nulo)
        self.fields['portero'].choices = lista_porteros

    def clean(self):
        """ Valida los datos del formulario """
        datos = self.cleaned_data

        # Comprobacion de que haya cumplimentado los campos
        dato = datos.get("portero")
        if dato is not 0:
            lista = [dato]
        else:
            raise forms.ValidationError("Claro que sí, sin portero...")

        dato = datos.get("defensas")
        if dato:
            lista += list(dato)
        else:
            raise forms.ValidationError("Pon algún defensa bonico")

        dato = datos.get("centrocampistas")
        if dato:
            lista += list(dato)
        else:
            raise forms.ValidationError("Menudo extremista eres, nadie en medio. Pues va a ser que no.")

        dato = datos.get("delanteros")
        if dato:
            lista += list(dato)
        else:
            raise forms.ValidationError("Algún delantero podría ser útil para marcar goles y eso...")

        # Comprobacion de los suplentes
        dato = datos.get("suplentes")
        if dato:
            lista_completa = lista + list(dato)
            # Comprobacion de que sean únicos
            for dato in lista_completa:
                if lista_completa.count(dato) != 1:
                    raise forms.ValidationError("Los jugadores no son amebas, no pueden dividirse y estar en "
                                                "2 sitios a la vez.")

        num_jugadores = len(lista)
        if num_jugadores != 11:
            raise forms.ValidationError("Tienes que indicar a 11 jugadores titulares.")

        num_suplentes = 7
        if len(datos.get("suplentes")) > num_suplentes:
            raise forms.ValidationError("Tienes que indicar como mucho " + str(num_suplentes) + " suplentes.")

        return datos

########################################################################
