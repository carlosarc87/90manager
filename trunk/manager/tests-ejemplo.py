#!/usr/bin/python

"""
This file is part of GeoRemindMe.

GeoRemindMe is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

GeoRemindMe is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with GeoRemindMe.  If not, see <http://www.gnu.org/licenses/>.

"""

from django.utils import unittest
from models import User

"""
    Tests creation and use of a single user
"""

class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.uno = User.objects.create(email="este@ema.il", password='unpass')
        self.otro = User.objects.create(email="este@ema.il", password='otro')

    def testPut(self):
        self.uno.put()
        self.uno.toggle_active()
        self.assertEqual(self.uno.is_active(), 'Putting one')
        self.assertRaises(TypeError,self.otro.put)

        

