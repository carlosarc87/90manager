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
from models import Liga

########################################################################

class LigaForm(forms.ModelForm):
	''' Formulario para crear ligas '''
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
			raise forms.ValidationError("Debe de introducir un valor para que el numero de equipos sea par")
		if valor <= 0:
			raise forms.ValidationError("Deben de haber mas de 0 equipos")
		return valor

	class Meta:
		model = Liga
		exclude = ('creador', 'fecha_creacion', 'publica', 'nombre')

########################################################################################

