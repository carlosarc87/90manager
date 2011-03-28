from django.core.management.base import BaseCommand, CommandError
from gestion_usuario.models import Usuario

class Command(BaseCommand):
	help = "Crea un administrador"

	args = "[nombre, clave, email ...]"

	def handle(self, *args, **options):
		if len(args) < 3:
			raise CommandError('Se requieren 3 parametros para que funcione la orden')

		nombre = args[0]
		password = args[1]
		email = args[2]

		if Usuario.objects.filter(username = nombre).count:
			raise CommandError('Ya existe un usuario con ese nombre')

		# Crear el usuario
		admin = Usuario.objects.create(username = nombre, email = email, is_active = True, is_staff = True, is_superuser = True)
		admin.set_password(password)
		admin.save()


