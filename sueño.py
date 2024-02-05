def detector_de_sueno():

    #deteccion sueños

    import cv2
    import cvzone
    from cvzone.FaceMeshModule import FaceMeshDetector
    import tkinter
    import pygame, sys
    from pygame import mixer
    import mediapipe as mp 
    import math
    import time
    from tkinter import messagebox

    #videocaptura
    #cap = cv2.VideoCapture('1.mov') para algun video en especidifico

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    #Variables de control
    parpadeo = False
    conteo = 0 
    tiempo = 0
    inicio = 0
    final = 0
    conteo_sueno = 0
    conteo_somn = 0
    muestra = 0
    ventana = True 

    #Funcion de dibujo
    mpDibujo = mp.solutions.drawing_utils
    ConfDibu = mpDibujo.DrawingSpec(thickness = 1, circle_radius = 0) #configura el dibujo

    #Dibujo donde almacena la malla facial
    mpMallaFacial = mp.solutions.face_mesh
    MallaFacial = mpMallaFacial.FaceMesh(max_num_faces=1,) #creado el objeto
    detector = FaceMeshDetector(maxFaces=1)

    def playaudio():
        pygame.init()
        file = 'westminster-chimes.mp3'
        pygame.mixer.music.load(file)
        pygame.mixer.music.play(100)

    def stopaudio():
        pygame.init()
        pygame.mixer.music.stop()

    #bucle principal
    while True:
        ret, frame = cap.read()
        frame, faces = detector.findFaceMesh(frame, draw=False)
        if ret==False:
            break
        frame = cv2.flip(frame, 1)

        #pasamos a color

        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #see the results

        resultados = MallaFacial.process(frameRGB)

        #Listas que guardarán los resultados

        px = []
        py = []
        lista = []
        r = 5
        t = 3

        if resultados.multi_face_landmarks: #si se detecta un rostro
            for rostros in resultados.multi_face_landmarks: #se muestra el rostro
                mpDibujo.draw_landmarks (
                    frame, rostros, mpMallaFacial.FACEMESH_CONTOURS, ConfDibu, ConfDibu
                )
                #mpDibujo.draw_landmarks(frame, coordinates_left_eye, coordinates_right_eye, ConfDibu, ConfDibu)

                #Extraemos los puntos del rostro detectado
                for id, puntos in enumerate(rostros.landmark):
                    #print(puntos) #Nos da una proporcion
                    al, an, c = frame.shape
                    x, y = int(puntos.x * an), int(puntos.y * al)
                    px.append(x)
                    py.append(y)
                    lista.append([id, x, y])

                    if len(lista) == 468:
                        if faces:
                            face = faces[0]
                            pointleft = face[145]
                            pointright = face[374]
                            w, _=detector.findDistance (pointleft, pointright)

                            #Calcular la distancia a la camara
                            W = 6.3
                            f = 1100
                            d = ((W * f) / w) + 10
                            cv2.putText(frame, f"Distancia: {int(d)}cm", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3,)

                            #Ojo derecho
                            x1, y1 = lista[145][1:]
                            x2, y2 = lista[159][1:]
                            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2 

                            longitud1=math.hypot(x2 - x1, y2 - y1)
                            print(longitud1)

                            #Ojo izquierdo
                            x3, y3 = lista[374][1:]
                            x4, y4 = lista[386][1:]
                            cx2, cy2 = (x3 + x4) // 2, (y3 + y4) // 2 

                            longitud2=math.hypot(x4 - x3, y4 - y3)
                            print(longitud2)

                            #Conteo de parpadeos

                            cv2.putText(frame, f"Parpadeos: {int(conteo)}", (100,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3,)
                            cv2.putText(frame, f"Micro suenos: {int(conteo_sueno)}", (70,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3,)
                            cv2.putText(frame, f"Duracion: {str(muestra)}", (350,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3,)

                            if (d >= 40 and d <= 45):
                                if (longitud1 <= 24 and longitud2 <= 24 and parpadeo == False):   #Parpadeos
                                    conteo = conteo+1
                                    parpadeo = True
                                    inicio = time.time()
                                elif (longitud2 > 24 and longitud2 > 24 and parpadeo == True): 
                                    parpadeo = False
                                    final = time.time()

                            if (d >= 46 and d <= 50):
                                if (longitud2 <= 21 and longitud2 <= 21 and parpadeo == False): #Parpadeo
                                    conteo = conteo + 1
                                    parpadeo = True
                                    inicio = time.time()
                                elif (longitud2 > 21 and longitud2 > 21 and parpadeo == True):
                                    parpadeo = False
                                    final = time.time()

                                    #Temporizador
                            if (d >= 51 and d <=60):
                                if (longitud2 <= 16 and longitud2 <= 16 and parpadeo == False):
                                    conteo = conteo + 1 
                                    parpadeo = True
                                    inicio = time.time()
                                elif (longitud2 > 16 and longitud2 > 16 and parpadeo == True): # Seguridad de parpadeo
                                    parpadeo = False
                                    final = time.time()

                            #Temporizador
                            tiempo = round(final - inicio, 0)

                            #Contador de sueños
                            if tiempo >= 3:
                                time.sleep(1)
                                conteo_sueno = conteo_sueno + 1
                                conteo_somn = conteo_somn + 1
                                muestra = tiempo
                                inicio = 0
                                final = 0
                            if conteo_somn >= 1:
                                playaudio()
                                messagebox.showwarning("! ! ! WARNING ! ! !", "Señal de somnolencia")
                                stopaudio()
                                conteo_somn = 0

        cv2.imshow("Frame", frame)
        k = cv2.waitKey(20) & 0xFF
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()