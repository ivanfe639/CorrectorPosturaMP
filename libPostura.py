# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 16:01:37 2023

@author: IOBREGON
"""


import cv2
import math
import numpy as np
import mediapipe as mp
import simpleaudio as sa
import time

TOLERANCE_PERC = 0.76
NUM_SAMPLES = 5

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
  wave_object = sa.WaveObject.from_wave_file("Approval_Sound.wav")
  print('playing sound using simpleaudio')
   
  # define an object to control the play
  play_object = wave_object.play()
  play_object.wait_done()
  
  
def playSoundBad():
  # define an object to play
  wave_object = sa.WaveObject.from_wave_file("error.wav")
  print('playing sound using simpleaudio')
   
  # define an object to control the play
  play_object = wave_object.play()
  play_object.wait_done()



def evalPosture(FIRST, REF_ANGLE, numSamples ):
  
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
        cv2.imwrite('imageTemp.png',annotated_image)        
      
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
  
  if (anguloProm > REF_ANGLE*TOLERANCE_PERC):
    playSoundOk()
  else:
    playSoundBad()      
      
    
  print("anglesArray = ")
  print(anglesArray)
  vid.release()

  return REF_ANGLE, anguloProm;

