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

from gestion_base.func import HorizRadioRenderer
from django import forms
from models import Liga

########################################################################

TIPOS_IA = ((1, 'Muy baja'), (2, 'Baja'), (3, 'Media'), (4, 'Alta'), (5, 'Muy alta'))
TIPOS_SEXO = ((0, 'Solo hombres'), (1, 'Solo mujeres'), (2, 'Hombres y mujeres'))
TIPOS_AVANCE = ((0, 'Manual'), (1, 'Automáticamente al acabar los usuarios los partidos'), (2, 'Automáticamente al acabar todos los partidos'))

########################################################################

class LigaForm(forms.ModelForm):
	''' Formulario para crear ligas '''
	inteligencia_bots = forms.ChoiceField(label = "Inteligencia de los robots", initial = 3, choices = TIPOS_IA)
	sexo_permitido = forms.ChoiceField(label = "Sexos permitidos", widget = forms.RadioSelect(renderer = HorizRadioRenderer), initial = 0, choices = TIPOS_SEXO)
	tipo_avance_jornadas = forms.ChoiceField(label = "Tipo de avance de jornadas", widget = forms.RadioSelect(renderer = HorizRadioRenderer), initial = 0, choices = TIPOS_AVANCE)
	
	num_jugadores_inicial = forms.IntegerField(initial = 20, min_value = 7, max_value = 99)
	nivel_max_jugadores_inicio = forms.IntegerField(initial = 50, min_value = 10, max_value = 100)
	
	class Meta:
		model = Liga
		exclude = ('creador', 'fecha_creacion', 'num_equipos')

########################################################################

class ActivarLigaForm(forms.ModelForm):
	''' Formulario de activacion de una liga '''
	equipos = forms.fields.MultipleChoiceField(required = False)

	def __init__(self, *args, **kwargs):
		''' Constructor que establece la lista de valores de los titulares '''
		super(ActivarLigaForm, self).__init__(*args, **kwargs)
		# Establecemos los valores de la lista multiple como los jugadores del equipo visitante
		self.fields['equipos'].choices = [[choice.id, choice.nombre] for choice in self.instance.equipo_set.all()]
		numero = len(self.instance.equipo_set.all())
		self.fields['num_equipos'] = forms.IntegerField(initial = str(123))

	def clean_num_equipos(self):
		''' Comprueba que haya un numero de equipos positivo y par y en caso afirmativo los devuelve '''
		valor = self.cleaned_data['num_equipos'] + len(self.instance.equipo_set.all())
		if valor % 2 != 0:
			raise forms.ValidationError("Debe de introducir un valor para que el número de equipos sea par")
		if valor <= 0:
			raise forms.ValidationError("Debe haber al menos 2 equipos")
		return valor

	class Meta:
		model = Liga
		exclude = ('creador', 'fecha_creacion', 'publica', 'nombre', 'sexo_permitido', 'permitir_bots', 'inteligencia_bots', 'tipo_avance_jornadas', 'dinero_inicial', 'num_jugadores_inicial', 'nivel_max_jugadores_inicio')

########################################################################################

