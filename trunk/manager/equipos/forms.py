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

class PrepararEquipoLocalForm(forms.ModelForm):
	titulares_local = forms.fields.MultipleChoiceField()
	
	def __init__(self, *args, **kwargs):
		super(PrepararEquipoLocalForm, self).__init__(*args, **kwargs)
		self.fields['titulares_local'].choices = [[choice.id, choice.nombre] for choice in self.instance.equipo_local.jugador_set.all()]

	class Meta:
		model = Partido
		exclude = ('jornada', 'equipo_local', 'equipo_visitante', 'goles_local', 'goles_visitante', 'titulares_visitante')

class PrepararEquipoVisitanteForm(forms.ModelForm):
	titulares_visitante = forms.fields.MultipleChoiceField()
	
	def __init__(self, *args, **kwargs):
		super(PrepararEquipoVisitanteForm, self).__init__(*args, **kwargs)
		self.fields['titulares_visitante'].choices = [[choice.id, choice.nombre] for choice in self.instance.equipo_visitante.jugador_set.all()]

	def clean_titulares_visitante(self):
		valor = self.cleaned_data['titulares_visitante']
		if len(valor) != 11:
			raise forms.ValidationError("Solo puedes seleccionar 11 jugadores.")
		return valor

	class Meta:
		model = Partido
		exclude = ('jornada', 'equipo_local', 'equipo_visitante', 'goles_local', 'goles_visitante', 'titulares_local')

class LigaForm(forms.ModelForm):
	class Meta:
		model = Liga
		exclude = ('creador', 'fecha_creacion')
