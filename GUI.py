# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 16:49:46 2023

@author: IOBREGON
To generate an exe file 
ver archivo gen_exe.txt

-F un solo archivo
-w windowed no
"""

import tkinter as tk
import threading
import time

import cv2
import math
import numpy as np
import mediapipe as mp
import simpleaudio as sa


TOLERANCE_PERC = 0.76
NUM_SAMPLES = 5

##COLORES##
COLOR_CORAL= "#ff7f50"

TOLERANCE_PERC = 0.76
NUM_SAMPLES = 5
SEG_MUESTREO = 60 #[s]
STATISTICS = [0 , 0]
  


def calcAngulo(results):
  
  x1 = results.pose_landmarks.landmark[12].x
  y1 = -results.pose_landmarks.landmark[12].y
  z1 = results.pose_landmarks.landmark[12].z
  
  x2 = results.pose_landmarks.landmark[11].x
  y2 = -results.pose_landmarks.landmark[11].y
  z2 = results.pose_landmarks.landmark[11].z   
  
  ptoMedioHombro = [ (x1+x2)/2, (y1+y2)/2, (z1+z2)/2];
  vecHombroOjo = [ results.pose_landmarks.landmark[0].x-ptoMedioHombro[0] , -results.pose_landmarks.landmark[0].y-ptoMedioHombro[1] ,results.pose_landmarks.landmark[0].z-ptoMedioHombro[2] ];
  vecPlano = [vecHombroOjo[0],ptoMedioHombro[1],0];
  angulo = math.acos( (vecHombroOjo[0]*vecPlano[0] + vecHombroOjo[1]*vecPlano[1] + vecHombroOjo[2]*vecPlano[2])/( math.sqrt( pow(vecHombroOjo[0],2)+pow(vecHombroOjo[1],2)+pow(vecHombroOjo[2],2) )*math.sqrt( pow(vecPlano[0],2)+pow(vecPlano[1],2)+pow(vecPlano[2],2) ) )    );

  angulo = angulo*180/math.pi - 90;
  
  return angulo, ptoMedioHombro;


def playSoundOk(): 
  # define an object to play
  wave_object = sa.WaveObject.from_wave_file("res\Approval_Sound.wav")
  print('playing sound using simpleaudio')
   
  # define an object to control the play
  play_object = wave_object.play()
  play_object.wait_done()
  
  
def playSoundBad():
  # define an object to play
  wave_object = sa.WaveObject.from_wave_file("res\error.wav")
  print('playing sound using simpleaudio')
   
  # define an object to control the play
  play_object = wave_object.play()
  play_object.wait_done()



def evalPosture(FIRST, REF_ANGLE, numSamples, statistics ):
  
  angulo = 90;    
  
  anglesArray = []
  
  # define a video capture object()
  vid = cv2.VideoCapture(0)
    
  mp_pose = mp.solutions.pose
  
  mp_drawing = mp.solutions.drawing_utils 
  mp_drawing_styles = mp.solutions.drawing_styles
  
  #Ciclo que toma numSamples angulos
  for i in range(0,numSamples): 
     
    ret, image = vid.read()
        
    # Run MediaPipe Pose and draw pose landmarks.
    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5, model_complexity=2) as pose:  
      
      # Convert the BGR image to RGB and process it with MediaPipe Pose.
      results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
      
      if (i==0):
        # Draw pose landmarks.
        annotated_image = image.copy()
        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        cv2.imwrite('res\imageTemp.png',annotated_image)        
      
      try:
        
        [angulo, ptoMedioHombro] = calcAngulo(results);
        
        anglesArray.append(angulo)
                
      except:
        print("No se pudo extraer")    
        
    time.sleep(0.5)
  
  # Promedio los valores de angulos obtenidos 
  anguloProm = np.mean(anglesArray)

  print("AnguloProm = ");
  print(anguloProm)
  print("REF_ANGLE = ");
  print(REF_ANGLE)
  print("FIRST = ");
  print(FIRST)
  
  if (FIRST == 1):
    REF_ANGLE = anguloProm
    playSoundOk()
    
  else:
    if (anguloProm > REF_ANGLE*TOLERANCE_PERC ):
      playSoundOk()
      statistics[0] = statistics[0] + 1
    else:
      playSoundBad()      
      statistics[1] = statistics[1] + 1
      
    
  print("anglesArray = ")
  print(anglesArray)
  vid.release()

  return REF_ANGLE, anguloProm;

class App:
  def __init__(self, master):
    self.master = master
    master.title("Interfaz gráfica")
    
    master.title("Corrector de postura")
    master.resizable(1,1)
    master.config(bg='blue')

    self.mainFrame = tk.Frame()
    self.mainFrame.pack()
    self.mainFrame.config(bg=COLOR_CORAL)
    self.mainFrame.config(width="665",height="630")
    
    # Variables Str asociadas a lo que se mostrará en pantalla
    self.anguloRefStr = tk.StringVar()
    self.anguloMedStr = tk.StringVar()
    self.msgFinalLabel = tk.StringVar()

    
    # Label nombre
    tk.Label(self.mainFrame, text="Nombre de la persona:", font=18, bg=COLOR_CORAL ).place(x=7,y=10)
    self.nombrePersona = tk.Entry(self.mainFrame, font=18)
    self.nombrePersona.place(x=220,y=12)

    # Crear botones
    self.start_button = tk.Button(self.mainFrame, text="Iniciar", font=18, command=self.start)
    self.stop_button = tk.Button(self.mainFrame, text="Detener", font=18, command=self.stop, state=tk.DISABLED)

    # Colocar botones en la ventana
    self.start_button.place(x=470,y=6)
    self.stop_button.place(x=550,y=6)

    # Imagen
    self.tempImage = tk.PhotoImage(file="res\imageTemp.png")
    self.imagen = tk.Label(self.mainFrame, image=self.tempImage, bg=COLOR_CORAL )
    self.imagen.place(x=10,y=50)
    
    # Label Angulo_Ref
    tk.Label(self.mainFrame, text="Ángulo referencia: ", font=18, bg=COLOR_CORAL).place(x=10,y=550)
    self.anguloRef = tk.Label(self.mainFrame, textvariable=self.anguloRefStr, font=18, bg=COLOR_CORAL)
    self.anguloRef.place(x=190,y=550)
    
    # Label Angulo_Med
    tk.Label(self.mainFrame, text="Ángulo Medido: ", font=18, bg=COLOR_CORAL).place(x=10,y=580)
    self.anguloMed = tk.Label(self.mainFrame, textvariable=self.anguloMedStr, font=18, bg=COLOR_CORAL)
    self.anguloMed.place(x=190,y=580)
      
    #Label resultados
    self.msgFin = tk.Label(self.mainFrame, textvariable=self.msgFinalLabel, font=18, bg=COLOR_CORAL)
    self.msgFin.place(x=270,y=550)
            
    # Variables para el hilo de ejecución
    self._running = False
    self._job = None


  # Funciones de control 
  def start(self):
    self.start_button.config(state=tk.DISABLED)
    self.stop_button.config(state=tk.NORMAL)
    self._running = True
    #self._job = threading.Thread(target=self.countdown)
    self._job = threading.Thread(target=self.startPostureControl)
    self._job.start()

  def stop(self):
    self.start_button.config(state=tk.NORMAL)
    self.stop_button.config(state=tk.DISABLED)
    self._running = False


  #Funciones procesamiento
  
  def startPostureControl(self):
    
    refAngle = 0
  
    # Toma los valores de referencia
    [refAngle , anguloActual] = evalPosture(1, refAngle, NUM_SAMPLES, STATISTICS)
    
    self.anguloRefStr.set("{:.2f}".format( refAngle )) 
    
    self.tempImage = tk.PhotoImage(file="res\imageTemp.png")
    self.imagen.config(image=self.tempImage)
    
    
    while (self._running == True):
    
      [refAngle , anguloActual] = evalPosture(0, refAngle, NUM_SAMPLES, STATISTICS)
      
      self.tempImage = tk.PhotoImage(file="res\imageTemp.png")
      self.imagen.config(image=self.tempImage)
      
      self.anguloMedStr.set("{:.2f}".format( anguloActual )) 
                             
      time.sleep(SEG_MUESTREO)
      
    if (self._running == False):
      
      print("STATISTICS")
      print(STATISTICS) 
      
      porcGood = STATISTICS[0]*100/(sum(STATISTICS)) 
      minGood = (SEG_MUESTREO*STATISTICS[0]/60)
      porcBad = STATISTICS[1]*100/(sum(STATISTICS)) 
      minBad = (SEG_MUESTREO*STATISTICS[1]/60)
      
      msgfinal = "||RESULTADOS||\nMinutos en buena postura: %.2f (%.2f %s)\nMinutos en mala postura: %.2f (%.2f %s)" % (minGood, porcGood, '%', minBad, porcBad, '%')
      
      self.msgFinalLabel.set(msgfinal)
      print(msgfinal)
      #guardar el csv
      pass
    
    
  def countdown(self):
    count = 10

    while count > 0 and self._running:
        print(count)
        time.sleep(1)
        count -= 1
        txt = "{:.2f}".format( (count) )
        
        self.anguloRefStr.set(txt)

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