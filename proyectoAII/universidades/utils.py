from .models import Universidad, Centro, Grado, Departamento, Asignatura

from bs4 import BeautifulSoup
import urllib.request

from time import sleep


def populate_bd(universidad):
    
        if universidad == "Universidad de Sevilla":  
            return universidad_sevilla(universidad)
        elif universidad == "Universidad de Granada":  
            return universidad_granada(universidad)
        elif universidad == "Universidad de Jaen":  
            return universidad_jaen(universidad)
        else: return (0,0,0)
    

def universidad_sevilla(universidad):
    url_us = "https://www.us.es"
    url_principal="https://www.us.es/estudiar/que-estudiar/grados-por-orden-alfabetico"
    grados = list()

    f = urllib.request.urlopen(url_us)
    s = BeautifulSoup(f,"lxml")

    num_centros = 0
    num_grados = 0
    num_asignaturas = 0

    # Datos fáciles donde no merece la pena hacer scrapping
    nombre = universidad
    localidad = "Sevilla"

    logo = s.find("a", class_="site-branding__logo").find("img")['src']
    logo_name = save_logo(url_us+logo, nombre)

    universidad_obj, creado = Universidad.objects.get_or_create(
        nombre=nombre,
        logo=logo_name,
        localidad = localidad,
        )

    def extraer_urls_grados_us(url_principal):
        f = urllib.request.urlopen(url_principal)
        s = BeautifulSoup(f,"lxml")
        urls = list()
        l = s.findAll("span",class_="enlace-flecha")
        return [x.find("a")['href'] for x in l]

    urls_grados = extraer_urls_grados_us(url_principal)

    for url in urls_grados:
        try:
            print("Trying")
            f = urllib.request.urlopen(url_us + url)
            s = BeautifulSoup(f,'lxml')
            
            nombre = " ".join(s.find("h1", class_="grado").getText().split())
            nombre_centro = s.find('div', class_="field--name-field-centro-s-responsables-del-").getText().replace("\n","")

            centro_obj, centro_creado = Centro.objects.get_or_create(
                nombre = nombre_centro,
                localidad = localidad,
                universidad = universidad_obj,
                )

            print(centro_obj)
            if centro_creado:
                num_centros+=1

            grado_obj, grado_creado = Grado.objects.get_or_create(
                nombre=nombre,
                centro = centro_obj,
            )
            print(grado_obj)

            if grado_creado:
                num_grados+=1

            tabla_asignaturas = s.find('div', class_="table-responsive").find("tbody").findAll("tr")

            for asignatura in tabla_asignaturas:
                asig = asignatura.find("a")
                nombre_asig = asig.getText()
                
                rama = s.find('div', class_="field--name-field-rama-de-conocimiento").getText().replace("\n","")
                curso = asignatura.find("td",class_="views-field-field-cur-numcur").getText().replace(" ","")
                codigo = asignatura.find("td",class_="views-field-field-ass-codnum").getText().replace(" ","")
                creditos_asignatura = asignatura.find("td",class_="views-field-field-credito").getText().replace(" ","")
                tipo_asignatura = " ".join(asignatura.find("td",class_="views-field-field-caracter").getText().split())

                asignatura_obj, asignatura_creada = Asignatura.objects.get_or_create(
                    nombre = nombre_asig,
                    grado = grado_obj,
                    curso= int(curso),
                    rama_conocimiento = rama,
                    codigo = codigo,
                    creditos = float(creditos_asignatura),
                    tipo_asignatura = tipo_asignatura,                    
                )
                print(asignatura_obj)
                if asignatura_creada:
                    num_asignaturas+=1
            sleep(90)
        except:
            print("ERROR :C")
            sleep(120)
    return (num_grados,num_centros,num_asignaturas)



def save_logo(url, name):
    nombre = name+url[-4:]
    urllib.request.urlretrieve(url, nombre)
    return nombre