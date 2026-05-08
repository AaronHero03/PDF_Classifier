import re

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
    def __init__(self, nombre, paginas, condicion, valor, longitud, ignorar_mayus):
        super().__init__(nombre, paginas)
        self.condicion = condicion
        self.valor = valor
        self.longitud = longitud
        self.ignorar_mayus = ignorar_mayus

    def ejecutar_logica(self, texto):
        val_esc = re.escape(self.valor)
        
        if self.longitud == 0:
            cuantificador = r"\w*" 
        else:
            l_faltante = max(0, self.longitud - len(self.valor))
            cuantificador = rf"\w{{{l_faltante}}}"

        if self.condicion == 0:
            regex = rf"\b{val_esc}{cuantificador}\b"
            
        elif self.condicion == 1:
            regex = rf"\b{cuantificador}{val_esc}\b"
            
        elif self.condicion == 2:
            if self.longitud == 0:
                regex = rf"\b\w*{val_esc}\w*\b"
            else:
                regex = rf"\b(?=\w*{val_esc}\w*)\w{{{self.longitud}}}\b"
        
        flags = re.IGNORECASE if self.ignorar_mayus else 0
        resultado = re.search(regex, texto, flags=flags)
            
        return resultado.group(0) if resultado else "NO_ENCONTRADO"
        
class ReglaClasificacion(Regla):
    def __init__(self, nombre, paginas, palabras_clave, salida_v, salida_f):
        super().__init__(nombre, paginas)
        self.palabras_clave = palabras_clave
        self.salida_v = salida_v
        self.salida_f = salida_f

    def ejecutar_logica(self, texto):
        texto_minusculas = texto.lower()
        
        if isinstance(self.palabras_clave, str):
            lista_palabras = [palabra.strip().lower() for palabra in self.palabras_clave.split(",") if palabra.strip()]
        else:
            lista_palabras = [palabra.lower() for palabra in self.palabras_clave]

        if any(palabra in texto_minusculas for palabra in lista_palabras):
            return self.salida_v
            
        return self.salida_f