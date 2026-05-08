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
    def __init__(self, nombre, paginas, condicion, valor, longitud):
        super().__init__(nombre, paginas)
        self.condicion = condicion
        self.valor = valor
        self.longitud = longitud

    def ejecutar_logica(self, texto):
        
        # 0 -> Empieza con. 1 -> Termina con. 2 -> Contiene
        l_faltante = self.longitud - len(self.valor)
        
        regex = ""
        if self.condicion == 0:
            regex = rf"\b{self.valor}\d{{{l_faltante}}}\b"
            
        elif self.condicion == 1:
            regex = rf"\b\d{{{l_faltante}}}{self.valor}\b"
            
        elif self.condicion == 2:
            regex = rf"\b(?=\w*{self.valor}\w*)\w{{{self.longitud}}}\b"
        
        resultado = re.search(regex, texto)
        return resultado.group(0) if resultado else "NO_ENCONTRADO"
        
class ReglaClasificacion(Regla):
    def __init__(self, nombre, paginas, palabras_clave, salida_v, salida_f):
        super().__init__(nombre, paginas)
        self.palabras_clave = palabras_clave
        self.salida_v = salida_v
        self.salida_f = salida_f

    def ejecutar_logica(self, texto):
        pass
