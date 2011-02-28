# -*- coding: utf-8 -*-
# Formularios del sistema. Los que deriven de una clase son rápidos de
# crear.

from django import forms
from gestion_entrenador.models import *

########################################################################

class UsuarioForm(forms.ModelForm):
	''' Formulario para registrar un usuario '''
	class Meta:
		model = Usuario
		exclude = ('is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'user_ptr_id', 'groups', 'user_permissions')

########################################################################

class EquipoForm(forms.ModelForm):
	''' Formulario para crear un equipo '''
	class Meta:
		model = Equipo
		exclude = ('usuario', 'liga')

########################################################################

class PrepararEquipoLocalForm(forms.ModelForm):
	''' Formulario de preparacion de equipos locales '''
	titulares_local = forms.fields.MultipleChoiceField()

	def __init__(self, *args, **kwargs):
		''' Constructor que establece la lista de valores de los titulares '''
		super(PrepararEquipoLocalForm, self).__init__(*args, **kwargs)
		# Establecemos los valores de la lista multiple como los jugadores del equipo local
		self.fields['titulares_local'].choices = [[choice.id, choice.nombre] for choice in self.instance.equipo_local.jugador_set.all()]

	def clean_titulares_local(self):
		''' Valida que se hayan seleccionado 11 jugadores y los devuelve '''
		valor = self.cleaned_data['titulares_local']
		if len(valor) != 11:
			raise forms.ValidationError("Solo puedes seleccionar 11 jugadores.")
		return valor

	class Meta:
		model = Partido
		exclude = ('jornada', 'equipo_local', 'equipo_visitante', 'goles_local', 'goles_visitante', 'titulares_visitante')

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
		exclude = ('jornada', 'equipo_local', 'equipo_visitante', 'goles_local', 'goles_visitante', 'titulares_local')

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
