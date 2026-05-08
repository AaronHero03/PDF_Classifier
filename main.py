# main.py
from backend.motor import MotorOCR
from backend.reglas import ReglaExtraccion, ReglaClasificacion

if __name__ == "__main__":
    # 1. Inicializamos el motor
    motor = MotorOCR(r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    
    # 2. Configuramos rutas
    motor.set_ruta_entrada(r"C:\ruta\a\tus\pdfs")
    motor.set_form_salida("{Matricula} - {Tipo}.pdf")
    
    # 3. Creamos reglas de prueba
    regla1 = ReglaExtraccion("Matricula", [0], 0, "A0", 8)
    motor.agregar_regla(regla1)
    
    # 4. A TRABAJAR!
    motor.procesar_archivos()