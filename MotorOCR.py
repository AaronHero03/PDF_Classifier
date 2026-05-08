import re
import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io


class Regla:
    def __init__(self, nombre, paginas):
        self.nombre = nombre
        self.paginas = paginas
        
    def evaluar(self, diccionario_textos):
        texto_a_evaluar = ""
        for pag in self.paginas:
            if pag in diccionario_textos:
                texto_a_evaluar += diccionario_textos[pag] + " "
                
        return self.ejecutar_logica(texto_a_evaluar)

    def ejecutar_logica(self, texto):
        pass

class ReglaExtraccion(Regla):
    def __init__(self, nombre, paginas, condicion, valor, longitud):
        super().__init__(nombre, paginas)
        self.condicion = condicion
        self.valor = valor
        self.longitud = longitud

    def ejecutar_logica(self, texto):
        pass

class ReglaClasificacion(Regla):
    def __init__(self, nombre, paginas, palabras_clave, salida_v, salida_f):
        super().__init__(nombre, paginas)
        self.palabras_clave = palabras_clave
        self.salida_v = salida_v
        self.salida_f = salida_f

    def ejecutar_logica(self, texto):
        pass

class MotorOCR:
#        tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    def __init__(self, tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        self.reglas = []
        self.formato_salida = ""
        self.ruta_entrada = ""
        
    def agregar_regla(self, regla: Regla):
        self.reglas.append(regla)
        
    def set_ruta_entrada(self, ruta):
        self.ruta_entrada = ruta
    
    def set_form_salida(self, formato):
        self.formato_salida = formato
        
        
    def procesar_archivos(self):
        
        archivos = [f for f in os.listdir(self.ruta_entrada) 
            if f.lower().endswith(".pdf")]

        print(f"Encontrados {len(archivos)} archivos")
        
        for archivo in archivos:
            
            ruta_antigua = os.path.join(self.ruta_entrada, archivo)
            print(f"Procesando: {archivo}...", end="\r")
            
            resultados = self.procesar_archivo_actual(ruta_antigua)
            
            renombrar(resultados)
            
                   
    def renombrar(self, resultados):
        print("Renombrar")
        # Logica para rennombrar los archivos con base a los resultados y al formato de salida especificado

    
    
    # Funcion principal para procesar cada archivo independiente
    def procesar_archivo_actual(self, ruta_individual):
        paginas_necesarias = set()
        for regla in self.reglas:
            for p in regla.paginas:
                paginas_necesarias.add(p)
                
        textos_por_pagina = self.extraer_textos(list(paginas_necesarias), ruta_individual)
        
        resultados = {}
        for regla in self.reglas:
            resultados[regla.nombre] = regla.evaluar(textos_por_pagina)
            
        return resultados
    
    # Extraer el texto del documento de todas las paginas necesarias
    # Salida: Diccionario Pagina:Texto 
    def extraer_texto(paginas, ruta):
        doc = fitz.open(ruta)
        textos_extraidos = {}

        
        for pag in paginas:
            if pag < len(doc):
                pagina = doc[pag]
                pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2)) 
                imagen_data = pix.tobytes("png")
                imagen = Image.open(io.BytesIO(imagen_data))
        
                texto = pytesseract.image_to_string(imagen, lang='eng')
                textos_extraidos[pag] = " ".join(texto.split())
                        
        doc.close()
        return textos_extraidos
    
