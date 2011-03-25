# -*- coding: utf-8 -*-
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

from django.shortcuts import render_to_response
from django import forms
from django.utils.safestring import mark_safe

########################################################################

def devolverMensaje(request, mensaje, url_salida = None):
	''' Devuelve un mensaje rapidamente como una pagina nueva

		Parametros:
		mensaje    -- mensaje a mostrar
		url_salida -- url hacia la que redireccionar
	'''
	return render_to_response("mensaje.html", {"usuario" : request.user, "mensaje" : mensaje, "url_salida" : url_salida})

########################################################################

class HorizRadioRenderer(forms.RadioSelect.renderer):
	''' Pone los radiobuttons horizontalmente '''
	def render(self):
		''' Mostrar los radiobuttons '''
		return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

########################################################################
