# -*- coding: utf-8 -*-
# Formularios del sistema. Los que deriven de una clase son rápidos de
# crear.
"""
Copyright 2013 by
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
from math import ceil

########################################################################

class SubastaForm(forms.ModelForm):
	''' Formulario para crear subastas '''
	def __init__(self, jugador, *args, **kwargs):
		''' Constructor que establece la cantidad minima de la subasta '''
		super(SubastaForm, self).__init__(*args, **kwargs)
		self.jugador = jugador

	def clean_fecha_fin(self):
		''' Comprueba que el numero de jornadas sea factible '''
		valor = self.cleaned_data['fecha_fin']
		# Comprobamos que sea positivo y no nulo
#		if valor < hoy:
#			raise forms.ValidationError("Debes de introducir una duracion de jornadas positiva y no nula")

		# Comprobamos que sea menor que las jornadas que quedan de liga
#		jornadas_restantes = 10000
#		if valor >= jornadas_restantes:
#			raise forms.ValidationError("Las subastas deben acabar antes de la ultima jornada de liga")

		return valor

	def clean_puja(self):
		''' Comprueba que el precio de subasta sea factible '''
		valor = self.cleaned_data['puja']
		# Comprobamos que sea positivo y no nulo
		if valor < 1:
			raise forms.ValidationError("Debes de introducir un precio de subasta no nulo")

		return valor

	def clean_precio_compra(self):
		''' Comprueba que el precio de compra sea mayor o igual que el de subasta '''
		valor = self.cleaned_data['precio_compra']
		if valor:
			subasta = self.cleaned_data['puja']

			if valor < subasta:
				raise forms.ValidationError("Debes de introducir un precio de compra superior al de subasta")

		return valor

	class Meta:
		model = Subasta
		exclude = ('estado', 'vendedor', 'comprador', 'atributos_jugador', 'liga', 'fecha_inicio')

########################################################################

class PujarForm(forms.Form):
	''' Acepta una cantidad para pujar por una subasta '''
	cantidad = forms.fields.IntegerField()

	def __init__(self, subasta, pujador, *args, **kwargs):
		''' Constructor que establece la cantidad minima de la subasta '''
		super(PujarForm, self).__init__(*args, **kwargs)

		self.puja_minima = int(ceil(subasta.puja * 1.10))
		self.fields['cantidad'].initial = self.puja_minima
		self.subasta = subasta
		self.pujador = pujador

	def clean_cantidad(self):
		""" Filtra la cantidad para comprobar si es correcta """
		valor = self.cleaned_data['cantidad']
		if valor < self.puja_minima:
			raise forms.ValidationError("Debe de apostar %d como mínimo" % self.puja_minima)
		if valor > self.pujador.dinero:
			raise forms.ValidationError("No tienes %d para pujar" % valor)
		if self.subasta.precio_compra:
			if valor >= self.subasta.precio_compra:
				raise forms.ValidationError("Tu estas tonto, no?")
		return valor

########################################################################
