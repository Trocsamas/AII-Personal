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