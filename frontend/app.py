import customtkinter as ctk
from tkinter import messagebox, filedialog
import os

# Importamos el motor y el wizard
from backend.motor import MotorOCR
from frontend.wizard import VentanaNuevaRegla

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DashboardPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OCR PDF Manager")
        self.geometry("900x700")

        # El motor (Ajustado para tu Arch Linux)
        self.motor = MotorOCR('/usr/bin/tesseract')
        self.dict_reglas = {} # Para guardar objetos vinculados a sus nombres

        # --- HEADER ---
        self.frame_header = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_header.pack(pady=20, padx=20, fill="x")
        
        self.entry_carpeta = ctk.CTkEntry(self.frame_header, width=400)
        self.entry_carpeta.pack(side="left", padx=5)
        ctk.CTkButton(self.frame_header, text="Examinar", command=self.seleccionar_carpeta).pack(side="left")

        # --- REGLAS ---
        self.frame_reglas = ctk.CTkFrame(self)
        self.frame_reglas.pack(pady=10, padx=20, fill="both", expand=True)
        
        header_r = ctk.CTkFrame(self.frame_reglas, fg_color="transparent")
        header_r.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header_r, text="Reglas de Extracción", font=("Arial", 16, "bold")).pack(side="left")
        ctk.CTkButton(header_r, text="+ Añadir Regla", command=self.abrir_wizard).pack(side="right")

        self.lista_reglas_frame = ctk.CTkScrollableFrame(self.frame_reglas)
        self.lista_reglas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- CONSTRUCTOR DE NOMBRE (EL ROMPECABEZAS) ---
        self.frame_puzzle = ctk.CTkFrame(self)
        self.frame_puzzle.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(self.frame_puzzle, text="Formato de Nombre Final:", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Aquí se pondrán los botones de las variables
        self.frame_tokens = ctk.CTkFrame(self.frame_puzzle, fg_color="transparent")
        self.frame_tokens.pack(fill="x", padx=10)
        
        self.entry_salida = ctk.CTkEntry(self.frame_puzzle, width=500, placeholder_text="Escribe o usa los botones de arriba...")
        self.entry_salida.pack(pady=10)

        self.btn_ejecutar = ctk.CTkButton(self, text="INICIAR PROCESAMIENTO", fg_color="green", height=50, command=self.procesar)
        self.btn_ejecutar.pack(pady=20)

    def seleccionar_carpeta(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_carpeta.delete(0, "end")
            self.entry_carpeta.insert(0, path)

    def abrir_wizard(self):
        VentanaNuevaRegla(self, self.recibir_regla)

    def recibir_regla(self, objeto_regla, resumen):
        nombre = objeto_regla.nombre
        
        # Fila visual en la lista
        fila = ctk.CTkFrame(self.lista_reglas_frame, fg_color="#2b2b2b")
        fila.pack(fill="x", pady=2, padx=5)
        ctk.CTkLabel(fila, text=f"{{{nombre}}} -> {resumen}").pack(side="left", padx=10)
        
        # Botón del rompecabezas
        btn_token = ctk.CTkButton(self.frame_tokens, text=f"{{{nombre}}}", width=80, 
                                 command=lambda n=nombre: self.insertar_token(n))
        btn_token.pack(side="left", padx=2)

        # GUARDAMOS AMBOS en el diccionario
        self.dict_reglas[nombre] = {
            "objeto": objeto_regla,
            "boton": btn_token
        }

        # Pasamos el frame de la fila Y el nombre para borrar
        ctk.CTkButton(fila, text="X", width=30, fg_color="red", 
                      command=lambda f=fila, n=nombre: self.eliminar_regla(f, n)).pack(side="right", padx=5)

    def insertar_token(self, nombre):
        pos = self.entry_salida.index(ctk.INSERT)
        self.entry_salida.insert(pos, f"{{{nombre}}}")

    def eliminar_regla(self, frame, nombre):
        # 1. Eliminar la fila de la lista
        frame.destroy()
        
        # 2. Eliminar el botón del rompecabezas y borrar del diccionario
        if nombre in self.dict_reglas:
            self.dict_reglas[nombre]["boton"].destroy() # <--- ¡Mágia!
            del self.dict_reglas[nombre]
            
    def procesar(self):
        ruta = self.entry_carpeta.get()
        formato = self.entry_salida.get()
        
        if not ruta or not os.path.exists(ruta):
            messagebox.showerror("Error", "Carpeta no válida")
            return
        
        if not self.dict_reglas:
            messagebox.showwarning("Error", "Agrega al menos una regla")
            return

        self.motor.set_ruta_entrada(ruta)
        self.motor.set_form_salida(formato)
        
        lista_objetos = [datos["objeto"] for datos in self.dict_reglas.values()]
        self.motor.reglas = lista_objetos
        
        try:
            self.motor.procesar_archivos()
            messagebox.showinfo("Listo", "Procesamiento terminado con éxito")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo: {str(e)}")
