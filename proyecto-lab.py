#--------------------------------------Importamos librerias--------------------------------------------

from tkinter import *
import os
import cv2
from matplotlib import pyplot
from mtcnn.mtcnn import MTCNN
import numpy as np

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

def login_exitoso():
    pantalla3 = Toplevel(pantalla)
    pantalla3.title("Login Exitoso")
    pantalla3.geometry("500x400")

    # Aquí puedes agregar etiquetas, botones u otros elementos en pantalla3

    # Llamar al detector de sueño
    detector_de_sueno()

    pantalla3.mainloop()

def porcentaje_oscuridad(imagen):
    # Convertir la imagen a escala de grises
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    # Binzarizar la imagen en escala de grises
    _, binarizada = cv2.threshold(imagen_gris, 50, 255, cv2.THRESH_BINARY)
    # Calcular el número total de píxeles en la imagen
    total_pixeles = imagen.shape[0] * imagen.shape[1]
    # Contar el número de píxeles oscuros (negros) en la imagen binarizada
    pixeles_oscuros = np.count_nonzero(binarizada == 0)
    # Calcular el porcentaje de oscuridad en la imagen
    porcentaje = (pixeles_oscuros / total_pixeles) * 100
    # Devolver el porcentaje calculado
    return porcentaje

def mostrar_destello(duration=1000):
    # Crear una imagen blanca (destello) del tamaño de una pantalla estándar
    flash_lite = np.ones((1080, 1920), np.uint8) * 255
    # Mostrar la imagen blanca en una ventana llamada 'flash'
    cv2.imshow('flash', flash_lite)
    # Mover la ventana del destello a la esquina superior izquierda
    cv2.moveWindow('flash', 0, 0)
    # Esperar durante un tiempo especificado (por defecto, 1000 milisegundos o 1 segundo)
    cv2.waitKey(duration)

#------------------------ Crearemos una funcion que se encargara de registrar el usuario ---------------------

def registrar_usuario():
    usuario_info = usuario.get() #Obetnemos la informacion alamcenada en usuario
    contra_info = contra.get() #Obtenemos la informacion almacenada en contra

    archivo = open(usuario_info, "w") #Abriremos la informacion en modo escritura
    archivo.write(usuario_info + "\n")   #escribimos la info
    archivo.write(contra_info)
    archivo.close()

    #Limpiaremos los text variable
    usuario_entrada.delete(0, END)
    contra_entrada.delete(0, END)

    #Ahora le diremos al usuario que su registro ha sido exitoso
    Label(pantalla1, text = "Registro Convencional Exitoso", fg = "green", font = ("Calibri",11)).pack()
    
#--------------------------- Funcion para almacenar el registro facial --------------------------------------
  
def registro_facial():
    cap = cv2.VideoCapture(0)  # Elegimos la cámara con la que haremos la detección
    while True:
        ret, frame = cap.read()
        # Calcular el porcentaje de oscuridad en el frame actual
        porcentaje = porcentaje_oscuridad(frame)
        # Mostrar el porcentaje de oscuridad en el frame
        cv2.putText(frame, f'Porcentaje de oscuridad: {porcentaje:.2f}%', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
        # Si el porcentaje de oscuridad es mayor al 50%, mostrar destello
        if porcentaje > 50:
            print(f'Porcentaje de oscuridad: {porcentaje:.2f}%')
            mostrar_destello(2000)
        cv2.imshow('Registro Facial', frame) # Mostrar el video en pantalla
        if cv2.waitKey(1) == 27:  # Romper el bucle si se presiona la tecla "Escape" (27 en ASCII)
            break

    usuario_img = usuario.get() 
    cv2.imwrite(usuario_img + ".jpg", frame)
    cv2.destroyAllWindows() # Liberar los recursos de la cámara
    cap.release() # Cerrar todas las ventanas abiertas por OpenCV

    # Limpiar los text variables en la interfaz gráfica
    usuario_entrada.delete(0, END)
    contra_entrada.delete(0, END)
    
    # Mostrar un mensaje indicando que el registro facial fue exitoso
    Label(pantalla1, text="Registro Facial Exitoso", fg="green", font=("Calibri", 11)).pack()
    #----------------- Detectamos el rostro y exportamos los pixeles --------------------------
    
    def reg_rostro(img, lista_resultados):
        data = pyplot.imread(img)
        for i in range(len(lista_resultados)):
            x1,y1,ancho, alto = lista_resultados[i]['box']
            x2,y2 = x1 + ancho, y1 + alto
            pyplot.subplot(1, len(lista_resultados), i+1)
            pyplot.axis('off')
            cara_reg = data[y1:y2, x1:x2]
            cara_reg = cv2.resize(cara_reg,(150,200), interpolation = cv2.INTER_CUBIC) #Guardamos la imagen con un tamaño de 150x200
            cv2.imwrite(usuario_img+".jpg",cara_reg)
            pyplot.imshow(data[y1:y2, x1:x2])
        pyplot.show()

    img = usuario_img+".jpg"
    pixeles = pyplot.imread(img)
    detector = MTCNN()
    caras = detector.detect_faces(pixeles)
    reg_rostro(img, caras)   
    
#------------------------Crearemos una funcion para asignar al boton registro --------------------------------
def registro():
    global usuario
    global contra  #Globalizamos las variables para usarlas en otras funciones
    global usuario_entrada
    global contra_entrada
    global pantalla1
    pantalla1 = Toplevel(pantalla) #Esta pantalla es de un nivel superior a la principal
    pantalla1.title("Registro")
    pantalla1.geometry("300x250")  #Asignamos el tamaño de la ventana
    
    #--------- Empezaremos a crear las entradas ----------------------------------------
    
    usuario = StringVar()
    contra = StringVar()
    
    Label(pantalla1, text = "Registro facial: debe de asignar un usuario:").pack()
    #Label(pantalla1, text = "").pack()  #Dejamos un poco de espacio
    Label(pantalla1, text = "Registro tradicional: debe asignar usuario y contraseña:").pack()
    Label(pantalla1, text = "").pack()  #Dejamos un poco de espacio
    Label(pantalla1, text = "Usuario * ").pack()  #Mostramos en la pantalla 1 el usuario
    usuario_entrada = Entry(pantalla1, textvariable = usuario) #Creamos un text variable para que el usuario ingrese la info
    usuario_entrada.pack()
    Label(pantalla1, text = "Contraseña * ").pack()  #Mostramos en la pantalla 1 la contraseña
    contra_entrada = Entry(pantalla1, textvariable = contra) #Creamos un text variable para que el usuario ingrese la contra
    contra_entrada.pack()
    Label(pantalla1, text = "").pack()  #Dejamos un espacio para la creacion del boton
    Button(pantalla1, text = "Registro Tradicional", width = 15, height = 1, command = registrar_usuario).pack()  #Creamos el boton

    #------------ Vamos a crear el boton para hacer el registro facial --------------------
    Label(pantalla1, text = "").pack()
    Button(pantalla1, text = "Registro Facial", width = 15, height = 1, command = registro_facial).pack()

#------------------------------------------- Funcion para verificar los datos ingresados al login ------------------------------------
    
def verificacion_login():
    log_usuario = verificacion_usuario.get()
    log_contra = verificacion_contra.get()

    usuario_entrada2.delete(0, END)
    contra_entrada2.delete(0, END)

    lista_archivos = os.listdir()   #Vamos a importar la lista de archivos con la libreria os
    if log_usuario in lista_archivos:   #Comparamos los archivos con el que nos interesa
        archivo2 = open(log_usuario, "r")  #Abrimos el archivo en modo lectura
        verificacion = archivo2.read().splitlines()  #leera las lineas dentro del archivo ignorando el resto
        if log_contra in verificacion:
            print("Inicio de sesion exitoso")
            Label(pantalla2, text = "Inicio de Sesion Exitoso", fg = "green", font = ("Calibri",11)).pack()
            # Llamar a login_exitoso
            login_exitoso()

        else:
            print("Contraseña incorrecta, ingrese de nuevo")
            Label(pantalla2, text = "Contraseña Incorrecta", fg = "red", font = ("Calibri",11)).pack()
    else:
        print("Usuario no encontrado")
        Label(pantalla2, text = "Usuario no encontrado", fg = "red", font = ("Calibri",11)).pack()
    
#--------------------------Funcion para el Login Facial --------------------------------------------------------
def login_facial():
#------------------------------Vamos a capturar el rostro-----------------------------------------------------
    cap = cv2.VideoCapture(0)               #Elegimos la camara con la que vamos a hacer la deteccion
    while(True):
        ret,frame = cap.read()              #Leemos el video
        porcentaje = porcentaje_oscuridad(frame)
        cv2.putText(frame, f'Porcentaje de oscuridad: {porcentaje:.2f}%', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        if porcentaje > 50:
            print(f'Porcentaje de oscuridad: {porcentaje:.2f}%')
            mostrar_destello(2000)
        cv2.imshow('Login Facial',frame)         #Mostramos el video en pantalla
        if cv2.waitKey(1) == 27:            #Cuando oprimamos "Escape" rompe el video
            break
    usuario_login = verificacion_usuario.get()    #Con esta variable vamos a guardar la foto pero con otro nombre para no sobreescribir
    cv2.imwrite(usuario_login+"LOG.jpg",frame)       #Guardamos la ultima caputra del video como imagen y asignamos el nombre del usuario
    cap.release()                               #Cerramos
    cv2.destroyAllWindows()

    usuario_entrada2.delete(0, END)   #Limpiamos los text variables
    contra_entrada2.delete(0, END)

    #----------------- Funcion para guardar el rostro --------------------------
    
    def log_rostro(img, lista_resultados):
        data = pyplot.imread(img)
        for i in range(len(lista_resultados)):
            x1,y1,ancho, alto = lista_resultados[i]['box']
            x2,y2 = x1 + ancho, y1 + alto
            pyplot.subplot(1, len(lista_resultados), i+1)
            pyplot.axis('off')
            cara_reg = data[y1:y2, x1:x2]
            cara_reg = cv2.resize(cara_reg,(150,200), interpolation = cv2.INTER_CUBIC) #Guardamos la imagen 150x200
            cv2.imwrite(usuario_login+"LOG.jpg",cara_reg)
            return pyplot.imshow(data[y1:y2, x1:x2])
        pyplot.show()

    #-------------------------- Detectamos el rostro-------------------------------------------------------
    
    img = usuario_login+"LOG.jpg"
    pixeles = pyplot.imread(img)
    detector = MTCNN()
    caras = detector.detect_faces(pixeles)
    log_rostro(img, caras)

    #-------------------------- Funcion para comparar los rostros --------------------------------------------
    def orb_sim(img1,img2):
        orb = cv2.ORB_create()  #Creamos el objeto de comparacion
 
        kpa, descr_a = orb.detectAndCompute(img1, None)  #Creamos descriptor 1 y extraemos puntos claves
        kpb, descr_b = orb.detectAndCompute(img2, None)  #Creamos descriptor 2 y extraemos puntos claves

        comp = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True) #Creamos comparador de fuerza

        matches = comp.match(descr_a, descr_b)  #Aplicamos el comparador a los descriptores

        regiones_similares = [i for i in matches if i.distance < 70] #Extraemos las regiones similares en base a los puntos claves
        if len(matches) == 0:
            return 0
        return len(regiones_similares)/len(matches)  #Exportamos el porcentaje de similitud
        
    #---------------------------- Importamos las imagenes y llamamos la funcion de comparacion ---------------------------------
    
    im_archivos = os.listdir()   #Vamos a importar la lista de archivos con la libreria os
    if usuario_login+".jpg" in im_archivos:   #Comparamos los archivos con el que nos interesa
        rostro_reg = cv2.imread(usuario_login+".jpg",0)     #Importamos el rostro del registro
        rostro_log = cv2.imread(usuario_login+"LOG.jpg",0)  #Importamos el rostro del inicio de sesion
        similitud = orb_sim(rostro_reg, rostro_log)
        if similitud >= 0.90:
            Label(pantalla2, text = "Inicio de Sesion Exitoso", fg = "green", font = ("Calibri",11)).pack()
            print("Bienvenido al sistema usuario: ",usuario_login)
            print("Compatibilidad con la foto del registro: ",similitud)

            # Llamar a login_exitoso
            login_exitoso()

        else:
            print("Rostro incorrecto, Cerifique su usuario")
            print("Compatibilidad con la foto del registro: ",similitud)
            Label(pantalla2, text = "Incompatibilidad de rostros", fg = "red", font = ("Calibri",11)).pack()
    else:
        print("Usuario no encontrado")
        Label(pantalla2, text = "Usuario no encontrado", fg = "red", font = ("Calibri",11)).pack()
            

#------------------------Funcion que asignaremos al boton login -------------------------------------------------
        
def login():
    global pantalla2
    global verificacion_usuario
    global verificacion_contra
    global usuario_entrada2
    global contra_entrada2
    
    pantalla2 = Toplevel(pantalla)
    pantalla2.title("Login")
    pantalla2.geometry("300x250")   #Creamos la ventana
    Label(pantalla2, text = "Login facial: debe de asignar un usuario:").pack()
    Label(pantalla2, text = "Login tradicional: debe asignar usuario y contraseña:").pack()
    Label(pantalla2, text = "").pack()  #Dejamos un poco de espacio
    
    verificacion_usuario = StringVar()
    verificacion_contra = StringVar()
    
    #---------------------------------- Ingresamos los datos --------------------------
    Label(pantalla2, text = "Usuario * ").pack()
    usuario_entrada2 = Entry(pantalla2, textvariable = verificacion_usuario)
    usuario_entrada2.pack()
    Label(pantalla2, text = "Contraseña * ").pack()
    contra_entrada2 = Entry(pantalla2, textvariable = verificacion_contra)
    contra_entrada2.pack()
    Label(pantalla2, text = "").pack()
    Button(pantalla2, text = "Inicio de Sesion Tradicional", width = 20, height = 1, command = verificacion_login).pack()

    #------------ Vamos a crear el boton para hacer el login facial --------------------
    Label(pantalla2, text = "").pack()
    Button(pantalla2, text = "Inicio de Sesion Facial", width = 20, height = 1, command = login_facial).pack()
        
#------------------------- Funcion de nuestra pantalla principal ------------------------------------------------
    
def pantalla_principal():
    global pantalla          #Globalizamos la variable para usarla en otras funciones
    pantalla = Tk()
    pantalla.geometry("300x250")  #Asignamos el tamaño de la ventana 
    pantalla.title("Aprende e Ingenia")       #Asignamos el titulo de la pantalla
    Label(text = "Login Inteligente", bg = "gray", width = "300", height = "2", font = ("Verdana", 13)).pack() #Asignamos caracteristicas de la ventana
    
#------------------------- Vamos a Crear los Botones ------------------------------------------------------
    
    Label(text = "").pack()  #Creamos el espacio entre el titulo y el primer boton
    Button(text = "Iniciar Sesion", height = "2", width = "30", command = login).pack()
    Label(text = "").pack() #Creamos el espacio entre el primer boton y el segundo boton
    Button(text = "Registro", height = "2", width = "30", command = registro).pack()

    pantalla.mainloop()

pantalla_principal()
