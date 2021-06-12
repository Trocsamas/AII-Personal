from .models import Universidad, Centro, Grado, Departamento, Asignatura

#Imports para el Scrapping
from bs4 import BeautifulSoup
import urllib.request
from time import sleep

#Imports para la indexación mediante whoosh
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, ID, KEYWORD
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
import os

#Imports de funciones adicionales
from utils_pdf import abreSacaBorraPDF

#Imports para mi
import traceback


def populate_bd(universidad):

    schem_grado = Schema(gradoId=ID(Stored=True),
                    nombre=TEXT(stored=True),
                    descripcion=TEXT(stored=True),
                    perfil_recomendado=TEXT(stored=True),
                    objetivos=TEXT(stored=True),
                    competencias=TEXT(stored=True),
                    salida_profesional=TEXT(stored=True),
                    url=ID(stored=True),
                    )
    
    #Comprobamos si no hay un index
    if not os.path.exists("Index-Grados"):
        os.mkdir("Index-Grados")
        ix = create_in("Index-Grados", schema=schem_grado)

    if universidad == "Buscar en todas":
        return universidad_sevilla("Universidad de Sevilla") + universidad_jaen("Universidad de Jaén")
    elif universidad == "Universidad de Sevilla":  
        return universidad_sevilla(universidad)
    elif universidad == "Universidad de Granada":  
        return universidad_granada(universidad)
    elif universidad == "Universidad de Jaén":  
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
    logo_name = save_logo(url_us+logo, nombre.replace(" ", "_"))

    
    universidad_obj, creado = Universidad.objects.get_or_create(
        nombre=nombre,
        logo=logo_name,
        localidad = localidad,
        )

    def extraer_urls_grados_us(url_principal):
        f = urllib.request.urlopen(url_principal)
        s = BeautifulSoup(f,"lxml")
        l = s.findAll("span",class_="enlace-flecha")
        return [x.find("a")['href'] for x in l]

    urls_grados = extraer_urls_grados_us(url_principal)

    #Abrimos el indice
    ix = open_dir("Index-Grados")

    #creamos un writer para poder añadir documentos al indice
    writer = ix.writer()

    for url in urls_grados[::15]:
        try:
            f = urllib.request.urlopen(url_us + url)
            s = BeautifulSoup(f,'lxml')
            #Tiempo de espera tras cada peticion a la US
            sleep(90)

            nombre = " ".join(s.find("h1", class_="grado").getText().split())
            nombre_centro = s.find('div', class_="field--name-field-centro-s-responsables-del-").getText().replace("\n","")

            centro_obj, centro_creado = Centro.objects.get_or_create(
                nombre = nombre_centro.title(),
                localidad = localidad,
                universidad = universidad_obj,
                )

            print(centro_obj)
            if centro_creado:
                num_centros+=1

            rama = s.find('div', class_="field--name-field-rama-de-conocimiento").getText().replace("\n","")
            
            grado_obj, grado_creado = Grado.objects.get_or_create(
                nombre=nombre,
                centro = centro_obj,
                rama_conocimiento = rama,
            )
            print(grado_obj)

            if grado_creado:
                num_grados+=1

            tabla_asignaturas = s.find('div', class_="table-responsive").find("tbody").findAll("tr")

            for asignatura in tabla_asignaturas:
                asig = asignatura.find("a")
                nombre_asig = asig.getText()
                
                curso = asignatura.find("td",class_="views-field-field-cur-numcur").getText().replace(" ","")
                codigo = asignatura.find("td",class_="views-field-field-ass-codnum").getText().replace(" ","")
                creditos_asignatura = asignatura.find("td",class_="views-field-field-credito").getText().replace(" ","")
                tipo_asignatura = " ".join(asignatura.find("td",class_="views-field-field-caracter").getText().split())

                asignatura_obj, asignatura_creada = Asignatura.objects.get_or_create(
                    nombre = nombre_asig,
                    grado = grado_obj,
                    curso= int(curso),
                    codigo = codigo,
                    creditos = float(creditos_asignatura),
                    tipo_asignatura = tipo_asignatura,                    
                )
                if asignatura_creada:
                    num_asignaturas+=1
            
            # Código lioso que busca la descripción
            #  y quita información irrelevante
            # (lo del idioma se mantiene porque es importante)
            # y regular que se encuentra en todas las descripciones de la US,
            # y por tanto no importa que se le aplique a todo.

            descripcion=[]
            texto = [text for text in 
                    s.find("div",class_="field--name-field-presentacion-y-guia")
                    .stripped_strings]
            for text in texto:
                descripcion.append(text)
                if  "MCERL" in text:
                    break
            descripcion = " ".join(descripcion)

            # Función para dejar el código más limpio
            def scrapeoyformateo(clase):
                return " ".join([text for text in 
                    s.find("div",class_=clase)
                    .stripped_strings])

            perfil = scrapeoyformateo("field--name-field-perfil-recomendado")
            objetivos = scrapeoyformateo("field--name-field-objetivos")
            competencias = scrapeoyformateo("field--name-field-competencias")
            salidas = scrapeoyformateo("field--name-field-salidas-profesionales")

            writer.add_document(gradoId=grado_obj.pk,
                    nombre=str(grado_obj.nombre),
                    descripcion=str(descripcion),
                    perfil_recomendado=str(perfil),
                    objetivos=str(objetivos),
                    competencias=str(competencias),
                    salida_profesional=str(salidas),
                    url=url_us + url,
                    )

        except Exception:
            traceback.print_exc()
            #En caso de un time-out la espera es mayor
            sleep(120)

    writer.commit()
    return (num_grados,num_centros,num_asignaturas)

def universidad_jaen(universidad):
    url_uja = "https://www.ujaen.es/"
    url_principal = "https://www.ujaen.es/estudios/oferta-academica/grados"

    grados = list()

    f = urllib.request.urlopen(url_uja)
    s = BeautifulSoup(f,'lxml')

    num_centros = 0
    num_grados = 0
    num_asignaturas = 0

    nombre = universidad
    localidad = "Jaén"
    
    logo_url = url_uja + s.find("a", class_="icon uja-header__logo").find("img")['src']
    logo_name = save_logo(logo_url, universidad)

    universidad_obj, creado = Universidad.objects.get_or_create(
        nombre = nombre,
        localidad = localidad,
        logo = logo_name,
    )

    def extraer_urls_grados_uja(url_principal):
            f = urllib.request.urlopen(url_principal)
            s = BeautifulSoup(f,"lxml")
            l = s.findAll("tbody")
            ls_tr = [x.findAll("tr") for x in l]
            #Aplano la lista
            l_trs = [item for sublist in ls_tr for item in sublist]
            # La página es muy rara y tiene duplicidad de datos
            return [x.find("a")['href'] for x in l_trs[1::2]]

    urls_grados = extraer_urls_grados_uja(url_principal)

    #Abrimos el indice
    ix = open_dir("Index-Grados")

    #creamos un writer para poder añadir documentos al indice
    writer = ix.writer()

    for url in urls_grados[::15]:
        try:
            f = urllib.request.urlopen(url_uja + url)
            s = BeautifulSoup(f,'lxml')
            sleep(90)
            print(url_uja +url)
            nombre_centro = s.find("div", class_="field--name-field-centro").find("div", class_="field__item").getText().strip()
            localidad = s.find("div", class_="field--name-field-campus").find("div", class_="field__item").getText()
            if "Úbeda" in localidad:
                localidad = "Úbeda"
            elif "Linares" in localidad:
                localidad = "Linares"
            else:
                localidad = "Jaén"

            centro_obj, creado = Centro.objects.get_or_create(
                nombre = nombre_centro,
                localidad = localidad,
                universidad = universidad_obj,
            )
            num_centros += 1 if creado else 0

            nombre_grado = s.find("h1",class_="estudios__titulo").getText()
            grado_obj,creado = Grado.objects.get_or_create(
                nombre =  nombre_grado,
                centro = centro_obj,
            )

            num_grados += 1 if creado else 0
            # La página de la UJA es inconsistente por tanto hay que tener en cuenta
            hay_asignaturas_en_web = [a for a in s.findAll("h3") if 'Asignaturas y Profesorado' in a.getText()][0].find("button")
            if hay_asignaturas_en_web:
                #En la web no tienen el código, por tanto, hay que entrar en la asignatura,
                # ralentizando el proceso exponencialmente
                #Por suerte he visto que la url contiene el codigo de la asignatura, haciendo que no sea necesario entrar,
                # simplemente hay que procesar la url
                ls_captions = s.findAll("caption")
                lfilter_captions = [caption.parent for caption in ls_captions if "Asignaturas" in caption.getText()]
                cursos=[table.findAll("a") for table in lfilter_captions]

                for curso in cursos:
                    num_curso = curso[0].parent.parent.parent.parent.find("caption").getText()
                    if "Primer" in num_curso:
                        tipo = "Obligatoria" if "Optativas" not in num_curso else "Optativas"
                        num_curso = 1
                    elif ("Segundo" in num_curso):
                        tipo = "Obligatoria" if "Optativas" not in num_curso else "Optativas"
                        num_curso = 2
                    elif ("Tercer" in num_curso):
                        tipo = "Obligatoria" if "Optativas" not in num_curso else "Optativas"
                        num_curso = 3
                    elif ("Cuarto" in num_curso):
                        tipo = "Obligatoria" if "Optativas" not in num_curso else "Optativas"
                        num_curso = 4
                    elif ("Quinto" in num_curso):
                        tipo = "Obligatoria" if "Optativas" not in num_curso else "Optativas"
                        num_curso = 5
                    else:
                        tipo = "Obligatoria" if "Optativas" not in num_curso else "Optativas"
                        num_curso=None
                    for asignatura in curso:
                        nombre_asignatura = asignatura.getText()                   

                        asignatura_obj,creado = Asignatura.objects.get_or_create(
                            nombre = nombre_asignatura,
                            grado = grado_obj,
                            curso = num_curso,
                            codigo = asignatura['href'][-16:-8],
                            creditos = asignatura.parent.parent.contents[-2].getText(),
                            tipo_asignatura = tipo,
                        )
                        num_asignaturas += 1 if creado else 0
                
            else:
                sleep(90)  
                url_asigs = [a for a in s.findAll("h3") if "Asignaturas y Profesorado" in a.getText()][0].find("a")['href']
                f = urllib.request.urlopen(url_asigs)
                s = BeautifulSoup(f,'lxml')
                sleep(90)
                h2_asigs = s.find("div", class_="clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item").findAll("h2")
                for h2 in h2_asigs:
                    #Para poder recorrer de forma decente las tablas,
                    # se va a recurrir a los titulos y buscar los hermanos
                    # con nextSibling
                    
                    primer_c = h2.nextSibling.nextSibling.nextSibling
                    segundo_c = h2.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling

                    if "Primer" in h2.getText():
                        num_curso = 1
                    elif ("Segundo" in h2.getText()):
                        num_curso = 2
                    elif ("Tercer" in h2.getText()) and ("Cuarto o Tercer" not in h2.getText()):
                        # Los dobles grados estan puestos un tanto raros
                        num_curso = 3
                    elif ("Cuarto" in h2.getText()):
                        # Aqui no sería necesaria la comprobación ya que lo cubre lo anterior
                        num_curso = 4
                    elif ("Quinto" in h2.getText()):
                        num_curso = 5
                    elif "Listado de Optativas" in h2.getText():
                        primer_c = h2.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling
                        segundo_c = h2.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling

                        num_curso = 4
                    else:
                        num_curso=None

                    asignaturas_curso = primer_c.findAll("tr")[1:] + segundo_c.findAll("tr")[1:]
                    for asignatura in asignaturas_curso:
                        if "Optativa" not in asignatura.contents[2].getText():
                            tipo = asignatura.contents[4].getText()
                            if "OB" in tipo and "Listado de Optativas" not in h2.getText():
                                tipo = "Obligatoria"
                            elif "FB" in tipo and "Listado de Optativas" not in h2.getText():
                                tipo = "Formación Básica"
                            else:
                                tipo = "Optativa"
                            try:
                                asignatura_obj,creado = Asignatura.objects.get_or_create(
                                    nombre = asignatura.contents[2].getText(),
                                    grado = grado_obj,
                                    curso = num_curso,
                                    codigo = asignatura.contents[0].getText(),
                                    creditos = asignatura.contents[6].getText().replace(",","."),
                                    tipo_asignatura = tipo,
                                )
                                num_asignaturas += 1 if creado else 0
                            except Exception:
                                traceback.print_exc()
            
            descripcion = s.find("div",class_="field--name-field-texto").getText()
            perfil = s.find("button",text="  Perfil de Ingreso\n").parent.next_sibling.next_sibling.getText().strip()
            objetivos =  s.find("button",text="  Objetivos Principales\n").parent.next_sibling.next_sibling.getText().replace("\n", " ").strip()
            url_mem = s.find("span",class_="file--mime-application-pdf").find("a")['href']
            competencias = abreSacaBorraPDF(url_mem)
            salidas =  s.find("button",text="  Salidas profesionales\n").parent.next_sibling.getText().strip()
            
            writer.add_document(gradoId=grado_obj.pk,
                    nombre=str(grado_obj.nombre),
                    descripcion=str(descripcion),
                    perfil_recomendado=str(perfil),
                    objetivos=str(objetivos),
                    competencias=str(competencias),
                    salida_profesional=str(salidas),
                    url=url_uja + url,
                    )

        except Exception:
            traceback.print_exc()
            sleep(120)

    writer.commit()
    return (num_grados,num_centros,num_asignaturas)


def save_logo(url, name):
    nombre = "media/universidades/"+name+url[-4:]
    urllib.request.urlretrieve(url, nombre)
    return nombre[6:]