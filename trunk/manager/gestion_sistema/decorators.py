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

from functools import wraps
from gestion_sistema.func import calcularCambios
from gestion_base.func import devolverMensaje

########################################################################

def actualizarLiga(function = None, redirect_field_name = None):
	""" Realiza los cambios pertinentes en una liga cuando avanza el
		tiempo en esta
	"""

	def _dec(view_func):
		def _view(request, *args, **kwargs):
			calcularCambios(request)
			return view_func(request, *args, **kwargs)

		_view.__name__ = view_func.__name__
		_view.__dict__ = view_func.__dict__
		_view.__doc__ = view_func.__doc__

		return _view

	if function is None:
		return _dec
	else:
		return _dec(function)

########################################################################

def comprobarSesion(ids = None, function = None, redirect_field_name = None):
	""" Comprueba que los ids de las sesiones esten correctamente
	"""
	def _dec(view_func):
		def _view(request, *args, **kwargs):
			if ids is not None:
				for clave in ids:
					if clave not in request.session:
						return devolverMensaje(request, "Error de acceso")
			return view_func(request, *args, **kwargs)

		_view.__name__ = view_func.__name__
		_view.__dict__ = view_func.__dict__
		_view.__doc__ = view_func.__doc__

		return _view

	if function is None:
		return _dec
	else:
		return _dec(function)

########################################################################
