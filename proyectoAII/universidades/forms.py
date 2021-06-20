from django import forms
from .models import Universidad, Centro

UNIVERSITY_CHOICES = (
    ('Buscar en todas', 'Buscar en todas'),
    ('Universidad de Sevilla', 'Universidad de Sevilla'),
    ('Universidad de Granada', 'Universidad de Granada'),
    ('Universidad de Jaén', 'Universidad de Jaén'),
)

class UniversidadChoiceForm(forms.Form):
    universidad = forms.ChoiceField(choices=UNIVERSITY_CHOICES)
    
class CentroChoiceForm(forms.Form):
    centro = forms.ModelChoiceField(queryset=Centro.objects.all(), empty_label="Mostrar Todos", required=False)

BUSCADORES = [
    ('descripcion',"Por Descripción"),
    ('perfil_recomendado',"Por Perfil Recomendado"),
    ('objetivos',"Por Objetivos"),
    ('salida_profesional', "Por Salidas")
]

class GradoSearchForm(forms.Form):
    texto_a_buscar = forms.CharField(max_length=255, required=True)
    tipo_de_busqueda = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=BUSCADORES,
        required=True,
        )