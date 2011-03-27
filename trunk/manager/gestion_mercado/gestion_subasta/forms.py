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
from models import Subasta

########################################################################

class SubastaForm(forms.ModelForm):
	''' Formulario para crear subastas '''

	def clean_expira(self):
		''' Comprueba que el numero de jornadas sea factible '''
		valor = self.cleaned_data['expira']
		# Comprobamos que sea positivo y no nulo
		if valor < 1:
			raise forms.ValidationError("Debes de introducir una duracion de jornadas positiva y no nula")
		# Comprobamos que sea menor que las jornadas que quedan de liga
		jornadas_restantes = 10000
		if valor >= jornadas_restantes:
			raise forms.ValidationError("Las subastas deben acabar antes de la ultima jornada de liga")

		return valor

	def clean_oferta(self):
		''' Comprueba que el precio de subasta sea factible '''
		valor = self.cleaned_data['oferta']
		# Comprobamos que sea positivo y no nulo
		if valor < 1:
			raise forms.ValidationError("Debes de introducir un precio de subasta no nulo")

		return valor

	def clean_precio_compra(self):
		''' Comprueba que el precio de compra sea mayor o igual que el de subasta '''
		valor = self.cleaned_data['precio_compra']
		if valor:
			subasta = self.cleaned_data['oferta']

			if valor < subasta:
				raise forms.ValidationError("Debes de introducir un precio de compra superior al de subasta")

		return valor

	class Meta:
		model = Subasta
		exclude = ('estado', 'vendedor', 'comprador', 'atributos_jugador', 'liga')

########################################################################
	def clean_num_equipos(self):
		''' Comprueba que haya un numero de equipos positivo y par y en caso afirmativo los devuelve '''
		valor = self.cleaned_data['num_equipos'] + len(self.instance.equipo_set.all())
		if valor % 2 != 0:
			raise forms.ValidationError("Debe de introducir un valor para que el número de equipos sea par")
		if valor <= 0:
			raise forms.ValidationError("Debe haber al menos 2 equipos")
		return valor
