# main.py
from backend.motor import MotorOCR
from backend.reglas import ReglaExtraccion, ReglaClasificacion

if __name__ == "__main__":
    # 1. Inicializamos el motor
    motor = MotorOCR('/usr/bin/tesseract')
    
    # 2. Configuramos rutas
    motor.set_ruta_entrada("./pdfs_prueba")
    motor.set_form_salida("{Matricula} - {Carrera}.pdf")
    
    # 3. Creamos reglas de prueba
    regla1 = ReglaExtraccion("Matricula", [0], 0, "A0", 9)
    regla2 = ReglaClasificacion("Carrera", [0], "Computacionales", "ITC", "")
    motor.agregar_regla(regla1)
    motor.agregar_regla(regla2)
    
    # 4. A TRABAJAR!
    motor.procesar_archivos()