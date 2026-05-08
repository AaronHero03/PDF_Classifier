import customtkinter as ctk
from tkinter import messagebox, filedialog
import os

# Importamos tus clases del backend
# Asumiendo que tus archivos se llaman motor.py y reglas.py dentro de una carpeta 'backend'
from backend.motor import MotorOCR
from backend.reglas import ReglaExtraccion, ReglaClasificacion

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VentanaNuevaRegla(ctk.CTkToplevel):
    def __init__(self, master, callback_guardar):
        super().__init__(master)
        self.title("Constructor de Reglas")
        self.geometry("600x350")
        self.callback_guardar = callback_guardar

        # --- SECCIÓN FIJA ---
        self.frame_fijo = ctk.CTkFrame(self)
        self.frame_fijo.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.frame_fijo, text="Nombre variable:").grid(row=0, column=0, padx=5, pady=10)
        self.entry_nombre = ctk.CTkEntry(self.frame_fijo, width=150, placeholder_text="Ej. Matricula")
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=10)

        ctk.CTkLabel(self.frame_fijo, text="Acción:").grid(row=0, column=2, padx=5, pady=10)
        self.combo_accion = ctk.CTkComboBox(self.frame_fijo, values=["Extraer texto", "Clasificar documento"], command=self.cambiar_interfaz)
        self.combo_accion.grid(row=0, column=3, padx=5, pady=10)

        self.frame_dinamico = ctk.CTkFrame(self)
        self.frame_dinamico.pack(pady=10, padx=20, fill="both", expand=True)

        self.btn_guardar = ctk.CTkButton(self, text="Guardar Regla", fg_color="green", command=self.guardar_regla)
        self.btn_guardar.pack(pady=15)

        self.cambiar_interfaz("Extraer texto")
        self.focus()
        self.after(100, self.grab_set)

    def limpiar_frame_dinamico(self):
        for widget in self.frame_dinamico.winfo_children():
            widget.destroy()

    def cambiar_interfaz(self, accion):
        self.limpiar_frame_dinamico()
        if accion == "Extraer texto":
            ctk.CTkLabel(self.frame_dinamico, text="Condición:").grid(row=0, column=0, padx=5, pady=15)
            self.combo_condicion = ctk.CTkComboBox(self.frame_dinamico, values=["Que empiece con", "Que termine con", "Que contenga"])
            self.combo_condicion.grid(row=0, column=1, padx=5, pady=15)
            
            self.entry_valor = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Valor (ej. A0)", width=100)
            self.entry_valor.grid(row=0, column=2, padx=5, pady=15)

            ctk.CTkLabel(self.frame_dinamico, text="Longitud:").grid(row=1, column=0, padx=5, pady=15)
            self.entry_longitud = ctk.CTkEntry(self.frame_dinamico, placeholder_text="8", width=50)
            self.entry_longitud.grid(row=1, column=1, padx=5, pady=15, sticky="w")
        else:
            ctk.CTkLabel(self.frame_dinamico, text="Si contiene:").grid(row=0, column=0, padx=5, pady=15)
            self.entry_palabras = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Palabras clave separadas por coma", width=250)
            self.entry_palabras.grid(row=0, column=1, padx=5, pady=15, columnspan=2)

            self.entry_true = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Si V (ej. AP)", width=80)
            self.entry_true.grid(row=1, column=1, padx=5, pady=15)
            self.entry_false = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Si F (ej. CC)", width=80)
            self.entry_false.grid(row=1, column=2, padx=5, pady=15)

    def guardar_regla(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Error", "Nombre de variable requerido")
            return

        paginas = [0] # Por defecto página 1 (índice 0)
        
        if self.combo_accion.get() == "Extraer texto":
            mapa_cond = {"Que empiece con": 0, "Que termine con": 1, "Que contenga": 2}
            cond = mapa_cond[self.combo_condicion.get()]
            val = self.entry_valor.get()
            long = int(self.entry_longitud.get() or 0)
            
            obj_regla = ReglaExtraccion(nombre, paginas, cond, val, long)
            resumen = f"Extraer {self.combo_condicion.get()} '{val}'"
        else:
            palabras = self.entry_palabras.get()
            v = self.entry_true.get()
            f = self.entry_false.get()
            obj_regla = ReglaClasificacion(nombre, paginas, palabras, v, f)
            resumen = f"Clasificar por '{palabras}'"

        self.callback_guardar(obj_regla, resumen)
        self.destroy()

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
        self.dict_reglas[nombre] = objeto_regla
        
        # Fila visual
        fila = ctk.CTkFrame(self.lista_reglas_frame, fg_color="#2b2b2b")
        fila.pack(fill="x", pady=2, padx=5)
        ctk.CTkLabel(fila, text=f"{{{nombre}}} -> {resumen}").pack(side="left", padx=10)
        ctk.CTkButton(fila, text="X", width=30, fg_color="red", command=lambda f=fila, n=nombre: self.eliminar_regla(f, n)).pack(side="right", padx=5)

        # Botón del rompecabezas
        btn_token = ctk.CTkButton(self.frame_tokens, text=f"{{{nombre}}}", width=80, 
                                 command=lambda n=nombre: self.insertar_token(n))
        btn_token.pack(side="left", padx=2)

    def insertar_token(self, nombre):
        pos = self.entry_salida.index(ctk.INSERT)
        self.entry_salida.insert(pos, f"{{{nombre}}}")

    def eliminar_regla(self, frame, nombre):
        frame.destroy()
        if nombre in self.dict_reglas:
            del self.dict_reglas[nombre]
        # Aquí podrías limpiar también el botón del token, pero por simplicidad lo dejamos así

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
        self.motor.reglas = list(self.dict_reglas.values())
        
        try:
            self.motor.procesar_archivos()
            messagebox.showinfo("Listo", "Procesamiento terminado con éxito")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo: {str(e)}")

if __name__ == "__main__":
    app = DashboardPrincipal()
    app.mainloop()