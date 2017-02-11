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
# Formularios del sistema. Los que deriven de una clase son rápidos de
# crear.

from django import forms

from .models import Equipo


########################################################################

class EquipoForm(forms.ModelForm):
    """ Formulario para crear un equipo """

    def __init__(self, liga, *args, **kwargs):
        """ Constructor que establece la lista de valores de los titulares """
        super(EquipoForm, self).__init__(*args, **kwargs)
        self.liga = liga

    def clean_siglas(self):
        """ Comprueba si las siglas del equipo existen en la misma liga """
        siglas = self.cleaned_data['siglas']
        siglas = siglas.upper()

        if self.liga.equipo_set.filter(siglas=siglas).count() > 0:
            raise forms.ValidationError("Las siglas ya existen en la liga")

        return siglas

    class Meta:
        model = Equipo
        exclude = ('usuario', 'liga', 'dinero')

########################################################################
