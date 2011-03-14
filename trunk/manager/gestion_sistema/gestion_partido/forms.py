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
	jugadores_disponibles = forms.fields.MultipleChoiceField(required = False)
	defensas = forms.fields.MultipleChoiceField()
	centrocampistas = forms.fields.MultipleChoiceField()
	portero = forms.fields.ChoiceField()
	delanteros = forms.fields.MultipleChoiceField()
	suplentes = forms.fields.MultipleChoiceField()

	def __init__(self, alineacion, equipo, *args, **kwargs):
		''' Constructor que establece la lista de valores de los titulares '''
		super(PrepararEquipoForm, self).__init__(*args, **kwargs)
		# Establecemos los valores de la lista multiple como los jugadores del equipo local
		jugadores = equipo.jugador_set.all()
		self.fields['jugadores_disponibles'].choices = [[choice.id, choice.nombre] for choice in jugadores]
		self.fields['defensas'].choices = [[choice.id, choice.nombre] for choice in jugadores]
		self.fields['centrocampistas'].choices = [[choice.id, choice.nombre] for choice in jugadores]
		self.fields['portero'].choices = [[choice.id, choice.nombre] for choice in jugadores]
		self.fields['delanteros'].choices = [[choice.id, choice.nombre] for choice in jugadores]
		self.fields['suplentes'].choices = [[choice.id, choice.nombre] for choice in jugadores]

#	def clean_defensas(self):

#	def clean_centrocampistas(self):

#	def clean_portero(self):

#	def clean_delanteros(self):

#	def clean_suplentes(self):

	def clean(self):
		''' Valida los datos del formulario '''
		datos = self.cleaned_data

		# Comprobacion de que haya cumplimentado los campos
		dato = datos.get("portero")
		if dato:
			lista = [dato]
		else:
			raise forms.ValidationError("Claro que sí, sin portero...")

		dato = datos.get("defensas")
		if dato:
			lista += list(dato)
		else:
			raise forms.ValidationError("Pon algun defensa bonico")

		dato = datos.get("centrocampistas")
		if dato:
			lista += list(dato)
		else:
			raise forms.ValidationError("Menudo extremista eres, o defendiendo o atacando, nadie en medio. Pues no.")

		dato = datos.get("delanteros")
		if dato:
			lista += list(dato)
		else:
			raise forms.ValidationError("Algun delantero podría ser útil")

		# Comprobacion de los suplentes
		dato = datos.get("suplentes")
		if dato:
			lista_completa = lista + list(dato)
			# Comprobacion de que sean únicos
			for dato in lista_completa:
				if lista_completa.count(dato) != 1:
					raise forms.ValidationError("Los jugadores no son amebas, no pueden dividirse y estar en 2 sitios a la vez.")
		else:
			raise forms.ValidationError("Como se te rompa algun titular... no se que vas a hacer eh")

		if len(lista) != 11:
			raise forms.ValidationError("Tienes que indicar exactamente 11 titulares.")

		num_suplentes = 7
		if len(datos.get("suplentes")) != num_suplentes:
			raise forms.ValidationError("Tienes que indicar exactamente " + str(num_suplentes) + " suplentes.")
		return datos


########################################################################
