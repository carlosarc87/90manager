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

import django
from django.conf import settings
from django.core.management import call_command

# Configurar django
settings.configure()
django.setup()

# Crear la bd
call_command('makemigrations', 'gestion_clasificacion gestion_equipo gestion_jornada gestion_jugador gestion_liga gestion_partido gestion_subasta gestion_usuario', interactive = False)
call_command('migrate', interactive = False)

# Crear el administrador
call_command('crearadmin', 'admin', '1234', 'admin@admin.net')

print('Fin del script "crearbd"')
