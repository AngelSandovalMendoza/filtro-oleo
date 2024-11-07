import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import math
import threading  # Importamos threading para ejecutar tareas en segundo plano
import time  # Simulamos un proceso largo

class FiltroOleoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Filtro Oleo en Imagen")
        self.root.geometry("800x600")

        # Variables para almacenar la imagen
        self.imagen = None
        self.imagen_mostrar = None

        # Frame para los botones en horizontal
        self.frame_botones = tk.Frame(self.root)
        self.frame_botones.pack(pady=20)

        # Botones
        self.boton_cargar = tk.Button(self.frame_botones, text="Cargar Imagen", command=self.cargar_imagen)
        self.boton_cargar.pack(side='left', padx=10)
        self.boton_gris = tk.Button(self.frame_botones, text="Aplicar Filtro Oleo (Gris)", command=self.aplicar_filtro_gris)
        self.boton_gris.pack(side='left', padx=10)
        self.boton_color = tk.Button(self.frame_botones, text="Aplicar Filtro Oleo (Color)", command=self.aplicar_filtro_color)
        self.boton_color.pack(side='left', padx=10)
        self.boton_guardar = tk.Button(self.frame_botones, text="Guardar Imagen", command=self.guardar_imagen)
        self.boton_guardar.pack(side='left', padx=10)

        # Label para mostrar la imagen
        self.label_imagen = tk.Label(self.root)
        self.label_imagen.pack(pady=10)

        # Barra de progreso
        self.bar_progreso = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.bar_progreso.pack(pady=20)

    def cargar_imagen(self):
        """Carga una imagen desde el sistema de archivos en un hilo separado."""
        ruta = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.bmp")])
        if ruta:
            threading.Thread(target=self._proceso_cargar_imagen, args=(ruta,)).start()

    def _proceso_cargar_imagen(self, ruta):
        """Proceso en segundo plano para cargar la imagen con barra de progreso."""
        self.bar_progreso.start()
        try:
            time.sleep(2)  # Simula el tiempo de carga
            self.imagen = Image.open(ruta)
            self.mostrar_imagen(self.imagen)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
        self.bar_progreso.stop()

    def mostrar_imagen(self, imagen):
        """Muestra la imagen en la interfaz con redimensionamiento."""
        # Definir el tamaño máximo de previsualización
        max_width, max_height = 400, 400
        
        # Redimensionar la imagen manteniendo la relación de aspecto
        width, height = imagen.size
        scale = min(max_width / width, max_height / height)
        new_size = (int(width * scale), int(height * scale))
        
        # Redimensionar con el filtro LANCZOS
        imagen_resized = imagen.resize(new_size, Image.LANCZOS)
        
        # Convertir a PhotoImage para Tkinter
        imagen_tk = ImageTk.PhotoImage(imagen_resized)
        
        # Mostrar en el Label
        self.label_imagen.config(image=imagen_tk)
        self.label_imagen.image = imagen_tk

    def aplicar_filtro_gris(self):
        """Aplica el filtro oleo en tonos de gris en un hilo separado."""
        if self.imagen:
            threading.Thread(target=self._proceso_aplicar_filtro_gris).start()
        else:
            messagebox.showwarning("Advertencia", "Primero debes cargar una imagen.")

    def _proceso_aplicar_filtro_gris(self):
        """Proceso en segundo plano para aplicar filtro gris con barra de progreso."""
        self.bar_progreso.start()
        time.sleep(2)  # Simula el tiempo de aplicación del filtro
        nueva_imagen = self.filtro_oleo_tonos_gris(self.imagen)
        self.mostrar_imagen(nueva_imagen)
        self.imagen = nueva_imagen
        self.bar_progreso.stop()

    def aplicar_filtro_color(self):
        """Aplica el filtro oleo a color en un hilo separado."""
        if self.imagen:
            threading.Thread(target=self._proceso_aplicar_filtro_color).start()
        else:
            messagebox.showwarning("Advertencia", "Primero debes cargar una imagen.")

    def _proceso_aplicar_filtro_color(self):
        """Proceso en segundo plano para aplicar filtro color con barra de progreso."""
        self.bar_progreso.start()
        time.sleep(2)  # Simula el tiempo de aplicación del filtro
        nueva_imagen = self.filtro_oleo_color(self.imagen)
        self.mostrar_imagen(nueva_imagen)
        self.imagen = nueva_imagen
        self.bar_progreso.stop()

    def guardar_imagen(self):
        """Guarda la imagen procesada en un hilo separado."""
        if self.imagen:
            ruta = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
            if ruta:
                threading.Thread(target=self._proceso_guardar_imagen, args=(ruta,)).start()
        else:
            messagebox.showwarning("Advertencia", "No hay imagen para guardar.")

    def _proceso_guardar_imagen(self, ruta):
        """Proceso en segundo plano para guardar la imagen con barra de progreso."""
        self.bar_progreso.start()
        time.sleep(2)  # Simula el tiempo de guardado
        try:
            self.imagen.save(ruta)
            messagebox.showinfo("Éxito", "Imagen guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la imagen: {e}")
        self.bar_progreso.stop()

    def filtro_oleo_tonos_gris(self, imagen: Image, matriz_size: int = None):
        """Aplica el filtro oleo en tonos de gris."""
        imagen_gris = imagen.convert('L')
        ancho, alto = imagen_gris.size
        matriz_size = int(math.sqrt(((ancho * alto) * 0.05) / 100)) if matriz_size is None else matriz_size
        step = matriz_size // 2
        nueva_imagen = imagen.copy().convert('L')

        for x in range(step, ancho - step):
            for y in range(step, alto - step):
                bloque = imagen_gris.crop((x - step, y - step, x + step, y + step))
                valores = [bloque.getpixel((i, j)) for i in range(bloque.width) for j in range(bloque.height)]
                mayor = self.mayor_frecuencia(self.histograma(valores))
                nueva_imagen.putpixel((x, y), mayor)

        return nueva_imagen

    def filtro_oleo_color(self, imagen: Image, matriz_size: int = None):
        """Aplica el filtro oleo a color."""
        imagen_color = imagen.convert('RGB')
        ancho, alto = imagen_color.size
        matriz_size = int(math.sqrt(((ancho * alto) * 0.05) / 100)) if matriz_size is None else matriz_size
        step = matriz_size // 2
        nueva_imagen = imagen.copy().convert('RGB')

        for x in range(step, ancho - step):
            for y in range(step, alto - step):
                bloque = imagen_color.crop((x - step, y - step, x + step, y + step))
                nuevo_pixel = self.genera_pixel(bloque)
                nueva_imagen.putpixel((x, y), nuevo_pixel)

        return nueva_imagen

    def genera_pixel(self, imagen: Image):
        """Genera un pixel en base a la imagen."""
        valores_rojo, valores_verde, valores_azul = [], [], []

        for x in range(imagen.width):
            for y in range(imagen.height):
                r, g, b = imagen.getpixel((x, y))
                valores_rojo.append(r)
                valores_verde.append(g)
                valores_azul.append(b)

        mayor_rojo = self.mayor_frecuencia(self.histograma(valores_rojo))
        mayor_verde = self.mayor_frecuencia(self.histograma(valores_verde))
        mayor_azul = self.mayor_frecuencia(self.histograma(valores_azul))

        return (mayor_rojo, mayor_verde, mayor_azul)

    def histograma(self, valores: list):
        """Genera un histograma de una lista de valores."""
        histograma = {}
        for valor in valores:
            histograma[valor] = histograma.get(valor, 0) + 1
        return histograma

    def mayor_frecuencia(self, histograma: dict):
        """Regresa el valor con mayor frecuencia de un histograma."""
        mayor, frecuencia = None, -1
        for clave, valor in histograma.items():
            if valor > frecuencia:
                frecuencia, mayor = valor, clave
        return mayor

if __name__ == "__main__":
    root = tk.Tk()
    app = FiltroOleoApp(root)
    root.mainloop()
