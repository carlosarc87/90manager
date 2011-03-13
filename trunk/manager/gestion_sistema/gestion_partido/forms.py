# -*- coding: utf-8 -*-
# Formularios del sistema. Los que deriven de una clase son rápidos de
# crear.
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

from django import forms
from models import Partido

########################################################################

class PrepararEquipoForm(forms.Form):
	''' Formulario de preparacion de equipos locales '''
	jugadores_disponibles = forms.fields.MultipleChoiceField()
	defensas = forms.fields.MultipleChoiceField()
	centrocampistas = forms.fields.MultipleChoiceField()
	portero = forms.fields.ChoiceField()
	delanteros = forms.fields.MultipleChoiceField()
	suplentes = forms.fields.MultipleChoiceField()

	def __init__(self, *args, **kwargs):
		''' Constructor que establece la lista de valores de los titulares '''
		super(PrepararEquipoForm, self).__init__(*args, **kwargs)
		# Establecemos los valores de la lista multiple como los jugadores del equipo local
		jugadores = self.instance.equipo.jugador_set.all()
		self.fields['jugadores_disponibles'].choices = [[choice.id, choice.nombre] for choice in jugadores]

	def clean(self):
		''' Valida los datos del formulario '''
		datos = self.cleaned_data
		lista = list(datos.get("defensas"))
		lista += list(datos.get("portero"))
		lista += list(datos.get("delanteros"))
		lista += list(datos.get("centrocampistas"))
		print "Lista de datos: "
		print lista
		if len(lista) != 11:
			raise forms.ValidationError("Tienes que indicar exactamente 11 titulares.")
#		if len(datos.get("suplentes") != 5):
#			raise forms.ValidationError("Tienes que indicar exactamente 5 suplentes.");
		return datos


########################################################################
