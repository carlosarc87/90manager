from django.core.management import call_command
from django.conf import settings

import django

# Configurar django
settings.configure()

django.setup()

# Crear la bd
call_command('makemigrations')
call_command('migrate')

# Crear el administrador
call_command('crearadmin', 'admin', '1234', 'admin@admin.net')

print("Fin del script")
