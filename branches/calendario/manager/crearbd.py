from django.core.management import setup_environ, call_command
import settings

# Configurar django
setup_environ(settings)

# Crear la bd
call_command('syncdb', interactive = False)

# Crear el administrador
call_command('crearadmin', 'admin', '1234', 'admin@admin.net')

print "Fin del script"
