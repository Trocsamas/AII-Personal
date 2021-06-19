from django.shortcuts import render, redirect
from django.views.generic import DetailView
from whoosh.index import open_dir

from .models import Universidad, Grado, Centro
from .forms import (
    UniversidadChoiceForm, 
    CentroChoiceForm, 
)
from .utils import populate_bd

from whoosh.qparser import QueryParser
import pandas as pd
import random

# Create your views here.
def home_view(request):
    universidades_qs = Universidad.objects.all()
    context = {
        'universidades': universidades_qs,
    }
    return render(request, 'universidades/home.html', context)


def universities_list(request):
    universidades_qs = Universidad.objects.all()
    #De momento está simple
    grados_qs = list(Grado.objects.all())
    grados_rand = random.sample(grados_qs,3)
    ix = open_dir("Index-Grados")
    with ix.searcher() as searcher:
        results = []
        for grado in grados_rand:
            query = QueryParser("gradoId", ix.schema).parse(str(grado.pk))
            results.append(searcher.search(query)[0])
    

    context = {
        'universidades':universidades_qs,
        'grados':zip(grados_rand,results),

    }
    return render(request, 'universidades/universidades.html', context)

def carga_view(request):
    form = UniversidadChoiceForm(request.POST or None)
    mensaje = None
    context = {
        'form': form,
        'mensaje': mensaje,
    }
    if request.method == 'POST':
        if 'aceptar' in request.POST:
            universidad = request.POST.get('universidad')
            num_grados,num_centros,num_asignaturas = populate_bd(universidad)
            mensaje = "Se han registrado "+str(num_grados)+" grados, " +str(num_centros)+" centros y "+str(num_asignaturas)+" asignaturas."
            context = {
                'form': form,
                'mensaje': mensaje,
            }
            return render(request, 'universidades/confirmacion.html',context)
        else:
            return redirect('/')
    return render(request, 'universidades/confirmacion.html',context)

def grados_from_centro_view(request):
    form_centro = CentroChoiceForm(request.POST or None)
    grados = None
    if request.method == 'POST':
        centro = request.POST.get('centro')
        if centro:
            grados = Grado.objects.filter(centro__id=centro)
        else:
            grados = Grado.objects.all()
        extrainfo = request.POST.get('extrainfo')
    context = {
        'form_centro':form_centro,
        'grados':grados,
    }
    return render(request, 'universidades/grados_centro.html', context)

class GradoDetailView(DetailView):
    model = Grado
    template_name = "universidades/grado-detail.html"
