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
from django.db import models
from django.contrib.auth.models import User, UserManager

########################################################################

# Usuario - hereda de la clase User de django
class Usuario(User):
	''' Representa a un usuario en el sistema '''
	objects = UserManager()

	def __unicode__(self):
		''' Devuelve una cadena de texto que representa la clase '''
		return self.username

	def save(self):
		''' Sobreescritura de la funcion save para arreglar un fallo con las contraseñas '''
		password = ""
		password = self.password
		self.set_password(self.password)
		if self.email == "":
			self.email = "none@none.net"
		User.save(self)

########################################################################
