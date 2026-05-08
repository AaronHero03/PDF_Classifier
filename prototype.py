import os
import re
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# --- CONFIGURACIÓN DE TESSERACT ---
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def extraer_datos_ocr(ruta_pdf):
    try:
        doc = fitz.open(ruta_pdf)
        pagina = doc[0]
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2)) 
        imagen_data = pix.tobytes("png")
        imagen = Image.open(io.BytesIO(imagen_data))
        
        texto = pytesseract.image_to_string(imagen, lang='eng')
        doc.close()

        texto_limpio = " ".join(texto.split())

        # Buscar matrícula
        match_m = re.search(r'A00\d{6}|A01\d{6}', texto_limpio)
        if not match_m:
             match_m = re.search(r'A\d{8}', texto_limpio)
             
        matricula = match_m.group(0) if match_m else None
        
        # Determinar tipo
        if any(palabra in texto_limpio for palabra in ["Aviso", "Privacidad", "Tercero"]):
            tipo = "AP"
        else:
            tipo = "CC"
            
        return matricula, tipo
    except Exception as e:
        print(f"Error en OCR: {e}")
        return None, None

def renombrar_in_situ(directorio):
    # Filtramos: que sea PDF y que su nombre empiece con "1"
    archivos = [f for f in os.listdir(directorio) 
                if f.lower().endswith(".pdf") and f.startswith("1")]
    
    print(f"Encontrados {len(archivos)} archivos que empiezan con '1'.")

    for archivo in archivos:
        ruta_antigua = os.path.join(directorio, archivo)
        
        print(f"Procesando: {archivo}...", end="\r")
        
        matricula, tipo = extraer_datos_ocr(ruta_antigua)
        
        if matricula and tipo:
            nuevo_nombre = f"{matricula} {tipo}.pdf"
            ruta_nueva = os.path.join(directorio, nuevo_nombre)
            
            try:
                # Renombrar en la misma carpeta
                os.rename(ruta_antigua, ruta_nueva)
                print(f"Renombrado: {archivo} -> {nuevo_nombre}          ")
            except FileExistsError:
                print(f"Error: El nombre {nuevo_nombre} ya existe. Se omitió {archivo}.")
            except Exception as e:
                print(f"No se pudo renombrar {archivo}: {e}")
        else:
            print(f"Fallo: No se pudo identificar datos en {archivo}          ")

# --- RUTA ÚNICA ---
# Cambia esto a la carpeta donde tienes tus archivos
carpeta_trabajo = r"G:\GRADUACIÓN JUN2026\CC - AP"

renombrar_in_situ(carpeta_trabajo)