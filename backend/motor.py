import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

from backend.reglas import Regla

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
            
            nuevo_nombre = self.generar_nombre(resultados)
            ruta_nueva = os.path.join(self.ruta_entrada, nuevo_nombre)
            
            try:
                os.rename(ruta_antigua, ruta_nueva)
                print(f"Renombrado: {archivo} -> {nuevo_nombre}")
            except FileExistsError:
                print(f"Error: El nombre {nuevo_nombre} ya existe. Se omitió {archivo}.")
            except Exception as e:
                print(f"No se pudo renombrar {archivo}: {e}")
                
                   
    def generar_nombre(self, resultados, formato_salida):
        """
        Recibe:
        resultados = {"Regla 1": "A00574813", "Regla 2": "CC"}
        formato_salida = "{Regla 1} Matricula {Regla 2}"
        """
        nombre_final = formato_salida
        
        for nombre_regla, valor_encontrado in resultados.items():
            # Buscamos literalmente la etiqueta con sus llaves, ej: "{Regla 1}"
            etiqueta_a_buscar = f"{{{nombre_regla}}}"
            
            # Reemplazamos la etiqueta con el valor real
            # Convertimos a string por si acaso el valor encontrado fuera un número
            nombre_final = nombre_final.replace(etiqueta_a_buscar, str(valor_encontrado))
            
        if not nombre_final.lower().endswith(".pdf"):
            nombre_final += ".pdf"
            
        nombre_final = " ".join(nombre_final.split())
            
        return nombre_final
    
    # Funcion principal para procesar cada archivo independiente
    def procesar_archivo_actual(self, ruta_individual):
        paginas_necesarias = set()
        for regla in self.reglas:
            for p in regla.paginas:
                paginas_necesarias.add(p)
                
        textos_por_pagina = self.extraer_textos(sorted(paginas_necesarias), ruta_individual)
        
        resultados = {}
        for regla in self.reglas:
            resultados[regla.nombre] = regla.evaluar(textos_por_pagina)
            
        return resultados
    
    # Extraer el texto del documento de todas las paginas necesarias
    # Salida: Diccionario Pagina:Texto 
    def extraer_textos(self, paginas, ruta):
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
    
