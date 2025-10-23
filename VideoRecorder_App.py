import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import time
from datetime import timedelta

class VideoRecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Grabador de Video - Detección Facial")
        
        # Variables de estado
        self.cap = None
        self.is_previewing = False
        self.is_recording = False
        self.face_detection_enabled = False
        self.out = None
        self.current_frame = None
        self.fps_value = 30
        self.recording_start_time = None
        
        # Cargar clasificador de detección facial
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal que contiene todo
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame izquierdo para el video
        left_frame = tk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame para el video
        self.video_frame = tk.Frame(left_frame, bg="black", width=640, height=480)
        self.video_frame.pack()
        self.video_frame.pack_propagate(False)
        
        # Label para mostrar el video
        self.video_label = tk.Label(self.video_frame, bg="black")
        self.video_label.pack(expand=True)
        
        # Frame para indicador de grabación (debajo del video)
        self.rec_frame = tk.Frame(left_frame)
        self.rec_frame.pack(pady=5)
        
        self.rec_label = tk.Label(self.rec_frame, text="", font=("Arial", 16, "bold"), fg="red")
        self.rec_label.pack()
        
        # Frame derecho para los controles
        right_frame = tk.Frame(main_container)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(10, 0))
        
        # Título de controles
        tk.Label(right_frame, text="Controles", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Botón de Preview
        self.btn_preview = tk.Button(
            right_frame, 
            text="Iniciar Preview", 
            command=self.toggle_preview,
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.btn_preview.pack(pady=10)
        
        # Botón de Grabación
        self.btn_record = tk.Button(
            right_frame, 
            text="Iniciar Grabación", 
            command=self.toggle_recording,
            width=20,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            state=tk.DISABLED
        )
        self.btn_record.pack(pady=10)
        
        # Botón de Detección Facial
        self.btn_face = tk.Button(
            right_frame, 
            text="Activar Detección\nFacial", 
            command=self.toggle_face_detection,
            width=20,
            height=2,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            state=tk.DISABLED
        )
        self.btn_face.pack(pady=10)
        
        # Botón de Guardar
        self.btn_save = tk.Button(
            right_frame, 
            text="Guardar Video", 
            command=self.save_video,
            width=20,
            height=2,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10, "bold"),
            state=tk.DISABLED
        )
        self.btn_save.pack(pady=10)
        
        # Separador
        ttk.Separator(right_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Frame para control de FPS
        fps_frame = tk.LabelFrame(right_frame, text="Control de FPS", font=("Arial", 11, "bold"), padx=15, pady=15)
        fps_frame.pack(pady=10, fill="x")
        
        # Container para el slider horizontal
        slider_container = tk.Frame(fps_frame)
        slider_container.pack(pady=5)
        
        # Label con valor mínimo
        tk.Label(slider_container, text="15", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Slider de FPS (horizontal)
        self.fps_slider = tk.Scale(
            slider_container, 
            from_=15, 
            to=60, 
            orient=tk.HORIZONTAL,
            command=self.update_fps,
            length=180,
            width=20,
            font=("Arial", 10)
        )
        self.fps_slider.set(30)
        self.fps_slider.pack(side=tk.LEFT, padx=5)
        
        # Label con valor máximo
        tk.Label(slider_container, text="60", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Frame para Entry de FPS
        fps_entry_frame = tk.Frame(fps_frame)
        fps_entry_frame.pack(pady=10)
        
        tk.Label(fps_entry_frame, text="FPS:", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.fps_entry = tk.Entry(fps_entry_frame, width=6, font=("Arial", 12), justify='center')
        self.fps_entry.insert(0, "30")
        self.fps_entry.pack(side=tk.LEFT, padx=5)
        self.fps_entry.bind("<Return>", self.update_fps_from_entry)
        
    def update_fps(self, value):
        self.fps_value = int(float(value))
        self.fps_entry.delete(0, tk.END)
        self.fps_entry.insert(0, str(self.fps_value))
        
    def update_fps_from_entry(self, event):
        try:
            value = int(self.fps_entry.get())
            if 15 <= value <= 60:
                self.fps_value = value
                self.fps_slider.set(value)
            else:
                messagebox.showwarning("Advertencia", "El valor de FPS debe estar entre 15 y 60")
                self.fps_entry.delete(0, tk.END)
                self.fps_entry.insert(0, str(self.fps_value))
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un número válido")
            self.fps_entry.delete(0, tk.END)
            self.fps_entry.insert(0, str(self.fps_value))
    
    def toggle_preview(self):
        if not self.is_previewing:
            self.start_preview()
        else:
            self.stop_preview()
    
    def start_preview(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la cámara")
            return
        
        self.is_previewing = True
        self.btn_preview.config(text="Detener Preview", bg="#f44336")
        self.btn_record.config(state=tk.NORMAL)
        self.btn_face.config(state=tk.NORMAL)
        
        self.update_frame()
    
    def stop_preview(self):
        self.is_previewing = False
        if self.is_recording:
            self.stop_recording()
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.btn_preview.config(text="Iniciar Preview", bg="#4CAF50")
        self.btn_record.config(state=tk.DISABLED)
        self.btn_face.config(state=tk.DISABLED, text="Activar Detección\nFacial", bg="#FF9800")
        self.face_detection_enabled = False
        
        self.video_label.config(image="")
        
    def toggle_face_detection(self):
        if not self.is_recording:
            self.face_detection_enabled = not self.face_detection_enabled
            if self.face_detection_enabled:
                self.btn_face.config(text="Desactivar Detección\nFacial", bg="#FF5722")
            else:
                self.btn_face.config(text="Activar Detección\nFacial", bg="#FF9800")
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        if not self.cap:
            return
        
        # Desactivar detección facial durante grabación
        if self.face_detection_enabled:
            self.face_detection_enabled = False
            self.btn_face.config(text="Activar Detección\nFacial", bg="#FF9800")
        
        # Obtener propiedades del video
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Configurar el codec y crear VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.temp_filename = f"temp_recording_{int(time.time())}.mp4"
        self.out = cv2.VideoWriter(
            self.temp_filename, 
            fourcc, 
            self.fps_value, 
            (frame_width, frame_height)
        )
        
        self.is_recording = True
        self.recording_start_time = time.time()
        self.btn_record.config(text="Detener Grabación", bg="#f44336")
        self.btn_preview.config(state=tk.DISABLED)
        self.btn_face.config(state=tk.DISABLED)
        self.btn_save.config(state=tk.DISABLED)
        self.fps_slider.config(state=tk.DISABLED)
        self.fps_entry.config(state=tk.DISABLED)
        
    def stop_recording(self):
        self.is_recording = False
        if self.out:
            self.out.release()
            self.out = None
        
        self.recording_start_time = None
        self.rec_label.config(text="")
        self.btn_record.config(text="Iniciar Grabación", bg="#2196F3")
        self.btn_preview.config(state=tk.NORMAL)
        self.btn_face.config(state=tk.NORMAL)
        self.btn_save.config(state=tk.NORMAL)
        self.fps_slider.config(state=tk.NORMAL)
        self.fps_entry.config(state=tk.NORMAL)
        
    def save_video(self):
        if not hasattr(self, 'temp_filename'):
            messagebox.showwarning("Advertencia", "No hay video para guardar")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            title="Guardar video como"
        )
        
        if file_path:
            try:
                import shutil
                shutil.move(self.temp_filename, file_path)
                messagebox.showinfo("Éxito", f"Video guardado en:\n{file_path}")
                self.btn_save.config(state=tk.DISABLED)
                delattr(self, 'temp_filename')
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el video:\n{str(e)}")
    
    def update_frame(self):
        if not self.is_previewing:
            return
            
        ret, frame = self.cap.read()
        if ret:
            # Guardar frame si está grabando
            if self.is_recording and self.out:
                self.out.write(frame)
            
            # Aplicar detección facial solo si está habilitada y NO está grabando
            if self.face_detection_enabled and not self.is_recording:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30)
                )
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Convertir frame a formato compatible con Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Redimensionar para ajustarse al frame
            img.thumbnail((640, 480), Image.Resampling.LANCZOS)
            
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)
            
            # Actualizar indicador de grabación
            if self.is_recording and self.recording_start_time:
                elapsed = time.time() - self.recording_start_time
                time_str = str(timedelta(seconds=int(elapsed)))
                self.rec_label.config(text=f"● REC {time_str}")
        
        # Llamar a update_frame cada 30 ms usando after() en lugar de thread
        self.root.after(30, self.update_frame)
    
    def on_closing(self):
        if self.is_recording:
            self.stop_recording()
        if self.is_previewing:
            self.stop_preview()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoRecorderGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()