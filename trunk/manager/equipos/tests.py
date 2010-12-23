"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

user1 = 'BOT'
pass1 = 'bot'

class URLTest(TestCase):
	def setUp(self):
		user = User.objects.create_user(user1, 'user1@dominio.com', pass1)
		
		
	
	def test_url_index(self):
		client = Client()
		response = client.get('/')
		self.failUnlessEqual(response.status_code, 200)
	
	def test_url_admin(self):
		client = Client()
		response = client.get('/admin/')
		self.failUnlessEqual(response.status_code, 200)
	
	def test_url_registrarse(self):
		client = Client()
		response = client.get('/registrarse/')
		self.failUnlessEqual(response.status_code, 200)
	
	def test_url_cuentas_logout(self):
		client = Client()
		response = client.get('/cuentas/logout')
		self.failUnlessEqual(response.status_code, 200)
	
	def test_url_cuentas_login(self):
		client = Client()
		response = client.get('/cuentas/login/')
		self.failUnlessEqual(response.status_code, 200)
	
	def test_url_cuentas_perfil(self):
		client = Client()
		response = client.get('/cuentas/perfil/')
		self.failUnlessEqual(response.status_code, 200)
	
	def test_url_crear_liga_identificado(self):
		client = Client()
		client.login(username=user1, password=pass1)
		response = client.get('/ligas/crear_liga/')
		self.failUnlessEqual(response.status_code, 200)
	
	def test_url_ver_equipo_identificado(self):
		client = Client()
		client.login(username=user1, password=pass1)
		response = client.get('/equipos/5')
		self.failUnlessEqual(response.status_code, 200)
	
	def test_url_ver_liga_identificado(self):
		client = Client()
		client.login(username=user1, password=pass1)
		response = client.get('/ligas/5')
		self.failUnlessEqual(response.status_code, 200)
	
	def test_url_ver_jugadores_identificado(self):
		client = Client()
		client.login(username=user1, password=pass1)
		response = client.get('/jugadores/5')
		self.failUnlessEqual(response.status_code, 200)
	
	def test_url_ver_jornada_identificado(self):
		client = Client()
		client.login(username=user1, password=pass1)
		response = client.get('/jornadas/5')
		self.failUnlessEqual(response.status_code, 200)
	
	def test_url_ver_partido_identificado(self):
		client = Client()

		if not client.login(username=user1, password=pass1):
			self.fail('BEEEEEEE')
		response = client.get('/partidos/5/')
		self.failUnlessEqual(response.status_code, 200)

	#~ def test_url_sin_identificar(self):
		#~ client = Client()
		#~ client.login(username=user1, password=pass1)
		#~ url = 'ligas/crear_liga/'
		#~ expected_url = '/cuentas/login?next=' + url
		#~ response = client.get('/ligas/crear_liga/')
		#~ TestCase.assertRedirects(self, response, expected_url, status_code=302, target_status_code=200, msg_prefix='')



#~ 
#~ ^admin/
#~ ^/?$
#~ ^registrarse/
#~ ^cuentas/logout/$
#~ ^cuentas/login/$
#~ ^cuentas/perfil/$
#~ ^equipos/(?P<equipo_id>\d+)/$
#~ ^ligas/crear_liga/$
#~ ^ligas/(?P<liga_id>\d+)/$
#~ ^jugadores/(?P<jugador_id>\d+)/$
#~ ^jornadas/(?P<jornada_id>\d+)/$
#~ ^partidos/(?P<partido_id>\d+)/$
