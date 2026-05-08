import os
import sys
from frontend.app import DashboardPrincipal
from backend.motor import MotorOCR

def obtener_ruta_tesseract():
    
    if getattr(sys, 'frozen', False):
        # Si es el .exe empaquetado
        base_path = sys._MEIPASS
    else:
        # Si es el script corriendo en tu carpeta de desarrollo
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, "tesseract_bin", "tesseract.exe")

if __name__ == "__main__":
    # 1. Calculamos la ruta del binario
    ruta_bin = obtener_ruta_tesseract()
    
    # 2. Lanzamos la App
    motor = MotorOCR(ruta_bin)
    app = DashboardPrincipal(motor)
    

    app.mainloop()