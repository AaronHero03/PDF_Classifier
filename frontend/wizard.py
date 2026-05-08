import customtkinter as ctk
from tkinter import messagebox
# Importamos las clases de las reglas para poder instanciarlas
from backend.reglas import ReglaExtraccion, ReglaClasificacion

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VentanaNuevaRegla(ctk.CTkToplevel):
    def __init__(self, master, callback_guardar, regla_existente=None): # <-- Nuevo parámetro
        super().__init__(master)
        self.title("Editar Regla" if regla_existente else "Constructor de Reglas")
        self.geometry("600x350")
        self.callback_guardar = callback_guardar
        self.regla_existente = regla_existente # Guardamos la referencia

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
        
        if self.regla_existente:
            self.cargar_datos_regla()
            
    def cargar_datos_regla(self):
        # 1. Nombre
        self.entry_nombre.insert(0, self.regla_existente.nombre)
        # Bloqueamos el nombre para evitar conflictos en el diccionario del Dashboard
        self.entry_nombre.configure(state="disabled") 

        # 2. Tipo y campos específicos
        if isinstance(self.regla_existente, ReglaExtraccion):
            self.combo_accion.set("Extraer texto")
            self.cambiar_interfaz("Extraer texto")
            
            # Mapeo inverso para el combo de condición
            mapa_inv = {0: "Que empiece con", 1: "Que termine con", 2: "Que contenga"}
            self.combo_condicion.set(mapa_inv[self.regla_existente.condicion])
            self.entry_valor.insert(0, self.regla_existente.valor)
            self.entry_longitud.insert(0, str(self.regla_existente.longitud))
            
        elif isinstance(self.regla_existente, ReglaClasificacion):
            self.combo_accion.set("Clasificar documento")
            self.cambiar_interfaz("Clasificar documento")
            
            self.entry_palabras.insert(0, self.regla_existente.palabras_clave)
            self.entry_true.insert(0, self.regla_existente.salida_v)
            self.entry_false.insert(0, self.regla_existente.salida_f)

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
            self.entry_palabras = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Palabras clave (coma)", width=250)
            self.entry_palabras.grid(row=0, column=1, padx=5, pady=15, columnspan=2)

            self.entry_true = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Si V", width=80)
            self.entry_true.grid(row=1, column=1, padx=5, pady=15)
            self.entry_false = ctk.CTkEntry(self.frame_dinamico, placeholder_text="Si F", width=80)
            self.entry_false.grid(row=1, column=2, padx=5, pady=15)

    def guardar_regla(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Error", "Nombre de variable requerido")
            return

        paginas = [0]
        if self.combo_accion.get() == "Extraer texto":
            mapa_cond = {"Que empiece con": 0, "Que termine con": 1, "Que contenga": 2}
            cond = mapa_cond[self.combo_condicion.get()]
            val = self.entry_valor.get()
            try:
                long = int(self.entry_longitud.get() or 0)
            except ValueError:
                long = 0
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