import re
import PyPDF2
import urllib.request
from os import remove
from time import sleep

# Esta función recibe una url de un pdf y devuelve un objeto con el lector de pdf
def openPDF(url):
    nombre = "PDF.pdf"
    urllib.request.urlretrieve(url,nombre)
    pdfFileObj = open(nombre, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    return (pdfReader,pdfFileObj)

def analizePDF(tuplapdf):
    pdfReader,pdfFileObj = tuplapdf
    re_competencias = re.compile(r"(\nC[A-Z.\s]{1,9}\d{1,2}[\s]{1,2}- )")
    texto_doc = ""
    for page in range(0,pdfReader.getNumPages()):
        text_page = pdfReader.getPage(page).extractText()
        if "4. ACCESO Y ADMISIÓN DE ESTUDIANTES" in text_page:
            text_page.split("4. ACCESO Y ADMISIÓN DE ESTUDIANTES")
            texto_doc+=text_page.split("4. ACCESO Y ADMISIÓN DE ESTUDIANTES")[0]
            break
        texto_doc+=text_page
    ls = re.split(re_competencias,texto_doc)[1:]
    text = "\n".join([(x+y).replace("\n"," ") for x,y in zip(ls[::2],ls[1::2])])
    re_pdfjunk = re.compile(r"([a-zI]{13}[\s:]{3}[0-9\s]{4,}[/\s\t\n]*[0-9]{1,})")
    text = re.sub(re_pdfjunk,"",text)
    pdfFileObj.close()
    return text

def abreSacaCompetencias(url):
    pdfReader = openPDF(url)
    competencias = analizePDF(pdfReader)
    return competencias