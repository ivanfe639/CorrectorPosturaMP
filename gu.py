import tkinter as tk
import threading
import time

class App:
    def __init__(self, master):
        self.master = master
        master.title("Interfaz gráfica")

        # Crear botones
        self.start_button = tk.Button(master, text="Iniciar", command=self.start)
        self.stop_button = tk.Button(master, text="Detener", command=self.stop, state=tk.DISABLED)

        # Colocar botones en la ventana
        self.start_button.pack(side=tk.LEFT)
        self.stop_button.pack(side=tk.LEFT)

        # Variables para el hilo de ejecución
        self._running = False
        self._job = None

    def start(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self._running = True
        self._job = threading.Thread(target=self.countdown)
        self._job.start()

    def stop(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self._running = False

    def countdown(self):
        count = 10
        while count > 0 and self._running:
            print(count)
            time.sleep(1)
            count -= 1

        if self._running:
            print("Cuenta atrás completada")

            # Aquí iría el código que quieres ejecutar en segundo plano

            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self._running = False
            self._job = None

root = tk.Tk()
app = App(root)
root.mainloop()