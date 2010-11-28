from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from manager.equipos.models import *
from manager.equipos.forms import *

def index(request):
	return HttpResponse("Hola guapo")
