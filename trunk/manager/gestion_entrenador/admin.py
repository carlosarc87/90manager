# -*- coding: utf-8 -*-
from django.contrib import admin
from manager.gestion_entrenador.models import *

admin.site.register(Usuario)
admin.site.register(Equipo)
admin.site.register(Jugador)
admin.site.register(Liga)
admin.site.register(Jornada)
admin.site.register(Partido)
admin.site.register(ClasificacionEquipoJornada)
