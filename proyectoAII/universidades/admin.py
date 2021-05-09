from django.contrib import admin
from .models import Universidad, Centro, Grado, Departamento, Asignatura

# Register your models here.
admin.site.register(Universidad)
admin.site.register(Centro)
admin.site.register(Grado)
admin.site.register(Departamento)
admin.site.register(Asignatura)