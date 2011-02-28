# -*- coding: utf-8 -*-
# Archivo para añadir las clases al panel de administración. Por cada
# clase se añade una linea

from django.contrib import admin
from manager.gestion_entrenador.models import *

admin.site.register(Usuario)
admin.site.register(Equipo)
admin.site.register(Jugador)
admin.site.register(Liga)
admin.site.register(Jornada)
admin.site.register(Partido)
admin.site.register(ClasificacionEquipoJornada)
