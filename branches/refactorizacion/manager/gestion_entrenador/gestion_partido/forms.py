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
from gestion_entrenador.gestion_partido.models import Partido

########################################################################

class PrepararEquipoLocalForm(forms.ModelForm):
	''' Formulario de preparacion de equipos locales '''
	titulares_local = forms.fields.MultipleChoiceField()

	def __init__(self, *args, **kwargs):
		''' Constructor que establece la lista de valores de los titulares '''
		super(PrepararEquipoLocalForm, self).__init__(*args, **kwargs)
		# Establecemos los valores de la lista multiple como los jugadores del equipo local
		jugadores = self.instance.equipo_local.jugador_set.all()
		self.fields['titulares_local'].choices = [[choice.id, choice.nombre] for choice in jugadores]

	def clean_titulares_local(self):
		''' Valida que se hayan seleccionado 11 jugadores y los devuelve '''
		valor = self.cleaned_data['titulares_local']
		if len(valor) != 11:
			raise forms.ValidationError("Solo puedes seleccionar 11 jugadores.")
		return valor

	class Meta:
		model = Partido
		exclude = ('jornada', 'equipo_local', 'equipo_visitante', 'goles_local', 'goles_visitante', 'alineacion_visitante', 'alineacion_local')

########################################################################

class PrepararEquipoVisitanteForm(forms.ModelForm):
	''' Formulario de preparacion de equipos locales '''
	titulares_visitante = forms.fields.MultipleChoiceField()

	def __init__(self, *args, **kwargs):
		''' Constructor que establece la lista de valores de los titulares '''
		super(PrepararEquipoVisitanteForm, self).__init__(*args, **kwargs)
		# Establecemos los valores de la lista multiple como los jugadores del equipo visitante
		self.fields['titulares_visitante'].choices = [[choice.id, choice.nombre] for choice in self.instance.equipo_visitante.jugador_set.all()]

	def clean_titulares_visitante(self):
		''' Valida que se hayan seleccionado 11 jugadores y los devuelve'''
		valor = self.cleaned_data['titulares_visitante']
		if len(valor) != 11:
			raise forms.ValidationError("Solo puedes seleccionar 11 jugadores.")
		return valor

	class Meta:
		model = Partido
		exclude = ('jornada', 'equipo_local', 'equipo_visitante', 'goles_local', 'goles_visitante', 'alineacion_local', 'alineacion_visitante')

########################################################################
