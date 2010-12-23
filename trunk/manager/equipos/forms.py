from django import forms
from equipos.models import *

# Formulario para registrar a un usuario. Elimina los campos que no queremos que trastee
class UsuarioForm(forms.ModelForm):
	class Meta:
		model = Usuario
		exclude = ('is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'user_ptr_id', 'groups', 'user_permissions')

class EquipoForm(forms.ModelForm):
	class Meta:
		model = Equipo
		exclude = ('usuario', 'liga')

class LigaForm(forms.ModelForm):
	class Meta:
		model = Liga
		exclude = ('creador', 'fecha_creacion')
