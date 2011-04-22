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

########################################################################

def actualizarLiga(function=None, redirect_field_name=None):
	"""Check that the user is NOT logged in.

	This decorator ensures that the view functions it is called on can be
	accessed only by anonymous users. When an authenticated user accesses
	such a protected view, they are redirected to the address specified in
	the field named in `next_field` or, lacking such a value, the URL in
	`home_url`, or the `USER_HOME_URL` setting.
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

