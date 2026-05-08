import customtkinter as ctk
from tkinter import messagebox

# Configuración básica de aspecto
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VentanaNuevaRegla(ctk.CTkToplevel):
    def __init__(self, master, callback_guardar):
        super().__init__(master)
        self.title("Constructor de Reglas")
        self.geometry("600x350")
        
        self.callback_guardar = callback_guardar

        # --- SECCIÓN FIJA: Nombre y Acción ---
        self.frame_fijo = ctk.CTkFrame(self)
        self.frame_fijo.pack(pady=10, padx=20, fill="x")

        # [ Nombre de Variable ]
        ctk.CTkLabel(self.frame_fijo, text="Nombre de variable:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.entry_nombre = ctk.CTkEntry(self.frame_fijo, width=150, placeholder_text="Ej. Matricula")
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=10)

        # [ Acción ] (El menú que cambia el resto de la ventana)
        ctk.CTkLabel(self.frame_fijo, text="Acción:").grid(row=0, column=2, padx=5, pady=10, sticky="w")
        self.combo_accion = ctk.CTkComboBox(self.frame_fijo, values=["Extraer texto", "Clasificar documento"], command=self.cambiar_interfaz)
        self.combo_accion.grid(row=0, column=3, padx=5, pady=10)

        # --- CONTENEDOR DINÁMICO ---
        self.frame_dinamico = ctk.CTkFrame(self)
        self.frame_dinamico.pack(pady=10, padx=20, fill="both", expand=True)

        # --- BOTÓN GUARDAR ---
        self.btn_guardar = ctk.CTkButton(self, text="Guardar Regla", fg_color="green", hover_color="darkgreen", command=self.guardar_regla)
        self.btn_guardar.pack(pady=15)

        # Cargar la interfaz inicial
        self.cambiar_interfaz("Extraer texto")

        # --- CORRECCIÓN AQUÍ ---
        # Le decimos a la ventana que se enfoque, pero le damos 100ms para que se dibuje primero
        self.focus()
        self.after(100, self.grab_set)
        
    def limpiar_frame_dinamico(self):
        for widget in self.frame_dinamico.winfo_children():
            widget.destroy()

    def cambiar_interfaz(self, accion):
        self.limpiar_frame_dinamico()

        if accion == "Extraer texto":
            # Frase: [Condición] [Valor]
            ctk.CTkLabel(self.frame_dinamico, text="Condición:").grid(row=0, column=0, padx=5, pady=15, sticky="w")
            self.combo_condicion = ctk.CTkComboBox(self.frame_dinamico, values=["Que empiece con", "Que contenga", "Que termine con"], width=150)
            self.combo_condicion.grid(row=0, column=1, padx=5, pady=15)
            
            self.entry_valor_extraccion = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Ej. A0 o A", width=100)
            self.entry_valor_extraccion.grid(row=0, column=2, padx=5, pady=15)

            # Frase: [Longitud] [Número] [caracteres]
            ctk.CTkLabel(self.frame_dinamico, text="Longitud:").grid(row=1, column=0, padx=5, pady=15, sticky="w")
            self.combo_longitud = ctk.CTkComboBox(self.frame_dinamico, values=["Exactamente", "Cualquier longitud"], width=150)
            self.combo_longitud.grid(row=1, column=1, padx=5, pady=15)
            
            self.entry_longitud = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Ej. 8", width=50)
            self.entry_longitud.grid(row=1, column=2, padx=5, pady=15)
            ctk.CTkLabel(self.frame_dinamico, text="caracteres.").grid(row=1, column=3, padx=5, pady=15, sticky="w")

        elif accion == "Clasificar documento":
            # Frase: Si contiene [Palabras clave]
            ctk.CTkLabel(self.frame_dinamico, text="Si contiene las palabras:").grid(row=0, column=0, padx=5, pady=15, sticky="w")
            self.entry_palabras = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Ej. Aviso, Privacidad", width=250)
            self.entry_palabras.grid(row=0, column=1, padx=5, pady=15, columnspan=3)

            # Frase: Salida verdadera / falsa
            ctk.CTkLabel(self.frame_dinamico, text="Salida Verdadera:").grid(row=1, column=0, padx=5, pady=15, sticky="w")
            self.entry_true = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Ej. AP", width=80)
            self.entry_true.grid(row=1, column=1, padx=5, pady=15, sticky="w")

            ctk.CTkLabel(self.frame_dinamico, text="Salida Falsa:").grid(row=1, column=2, padx=5, pady=15, sticky="w")
            self.entry_false = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Ej. CC", width=80)
            self.entry_false.grid(row=1, column=3, padx=5, pady=15, sticky="w")

    def guardar_regla(self):
        nombre = self.entry_nombre.get().strip()
        accion = self.combo_accion.get()

        if not nombre:
            messagebox.showwarning("Faltan datos", "Por favor, asigna un nombre a la variable.")
            return

        # Construir el resumen textual para el Dashboard
        if accion == "Extraer texto":
            resumen = f"Extraer: {self.combo_condicion.get()} '{self.entry_valor_extraccion.get()}'"
        else:
            resumen = f"Clasificar: Palabras '{self.entry_palabras.get()}' -> {self.entry_true.get()} / {self.entry_false.get()}"

        # Enviar la regla de vuelta a la ventana principal
        self.callback_guardar(nombre, resumen)
        self.destroy() # Cerrar el wizard


class DashboardPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Administrador de Reglas OCR - Estilo Excel")
        self.geometry("800x600")

        # --- HEADER: CARPETA ---
        self.frame_header = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_header.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(self.frame_header, text="Carpeta de origen:", font=("Arial", 14, "bold")).pack(side="left", padx=5)
        self.entry_carpeta = ctk.CTkEntry(self.frame_header, placeholder_text="G:\\GRADUACIÓN JUN2026\\CC - AP", width=300)
        self.entry_carpeta.pack(side="left", padx=5)
        ctk.CTkButton(self.frame_header, text="Examinar", width=80).pack(side="left", padx=5)

        # --- SECCIÓN CENTRAL: ADMINISTRADOR DE REGLAS ---
        self.frame_reglas = ctk.CTkFrame(self)
        self.frame_reglas.pack(pady=15, padx=20, fill="both", expand=True)

        # Título y botón superior de las reglas
        self.header_reglas = ctk.CTkFrame(self.frame_reglas, fg_color="transparent")
        self.header_reglas.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(self.header_reglas, text="Reglas Activas", font=("Arial", 16, "bold")).pack(side="left")
        ctk.CTkButton(self.header_reglas, text="+ Añadir Regla", command=self.abrir_wizard).pack(side="right")

        # Contenedor donde se apilarán las reglas visualmente
        self.lista_reglas_frame = ctk.CTkScrollableFrame(self.frame_reglas)
        self.lista_reglas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- FOOTER: CONSTRUCTOR DE SALIDA ---
        self.frame_salida = ctk.CTkFrame(self)
        self.frame_salida.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.frame_salida, text="Formato de Nombre Final:", font=("Arial", 14, "bold")).pack(pady=(10,0))
        ctk.CTkLabel(self.frame_salida, text="Usa llaves para tus variables. Ej: {Matricula} - {Tipo}.pdf", text_color="gray").pack()
        
        self.entry_salida = ctk.CTkEntry(self.frame_salida, placeholder_text="{Variable1} {Variable2}.pdf", width=400, justify="center")
        self.entry_salida.pack(pady=10)

        self.btn_ejecutar = ctk.CTkButton(self, text="▶ INICIAR PROCESAMIENTO", font=("Arial", 16, "bold"), fg_color="green", hover_color="darkgreen")
        self.btn_ejecutar.pack(pady=10)

    def abrir_wizard(self):
        VentanaNuevaRegla(self, self.agregar_regla_al_dashboard)

    def agregar_regla_al_dashboard(self, nombre, resumen):
        # Crear una pequeña "tarjeta" o "fila" para la regla
        fila = ctk.CTkFrame(self.lista_reglas_frame, fg_color="#2b2b2b")
        fila.pack(fill="x", pady=5, padx=5)

        texto_mostrar = f"Variable: {{{nombre}}}  |  {resumen}"
        ctk.CTkLabel(fila, text=texto_mostrar, font=("Arial", 13)).pack(side="left", padx=15, pady=10)
        
        # Botón para eliminar (funcionalidad visual)
        ctk.CTkButton(fila, text="Eliminar", width=60, fg_color="#8b0000", hover_color="#5c0000", 
                      command=fila.destroy).pack(side="right", padx=10)

if __name__ == "__main__":
    app = DashboardPrincipal()
    app.mainloop()