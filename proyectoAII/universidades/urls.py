from django.urls import path
from .views import (
    home_view,
    universities_list,
    carga_view,
    grados_from_centro_view,
    busca_grados_view,
    GradoDetailView,
    UniversidadDetailView,
    )

app_name = 'universidades'
urlpatterns = [
    path("", home_view, name="home"),
    path("universidades/", universities_list, name="universidades"),
    path("carga/", carga_view, name="carga"),
    path("grados_centro/",grados_from_centro_view, name="grados"),
    path("grado/<pk>", GradoDetailView.as_view(), name="grado-detail"),
    path("universidad/<pk>", UniversidadDetailView.as_view(), name="universidad-detail"),
    path("buscador/", busca_grados_view, name="buscador")
]
