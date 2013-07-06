# -*- coding: utf-8 -*-
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
from datetime import datetime

from models import Usuario

def getUsuariosConectados():
    # Query all non-expired sessions
    sesiones = Session.objects.filter(expire_date__gte = datetime.now())
    uid_list = []

    # Build a list of user ids from that query
    for sesion in sesiones:
        data = sesion.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return Usuario.objects.filter(id__in = uid_list)
