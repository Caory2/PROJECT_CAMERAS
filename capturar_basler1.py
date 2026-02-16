from pypylon import pylon
import cv2
import os
import time
from datetime import datetime

# ==============================================================================
# CONFIGURACIÓN DE GUARDADO (Plan "Carpeta Única")
# ==============================================================================
# 1. Ruta FIJA (Siempre será esta carpeta)
RUTA_CARPETA = r"C:\Users\CAROLINA\Desktop\CAMARAS\PYTHON\imagenes_capturadas"

# 2. Crear la carpeta si no existe|
os.makedirs(RUTA_CARPETA, exist_ok=True)

# Parámetros de captura
intervalo_segundos = 0.5       # Tiempo entre foto y foto
num_imagenes = 10              # Cuántas fotos tomará en esta tanda
escala_visual = 0.4            # Tamaño de la ventana en pantalla

# ==============================================================================
# INICIALIZACIÓN DE CÁMARA
# ==============================================================================
try:
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
except Exception as e:
    print("ERROR CRÍTICO: No se detectó la cámara Basler.")
    exit()

converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

print("----------------------------------------------------------------")
print("   SISTEMA DE CAPTURA - ARCHIVO CRONOLÓGICO")
print("----------------------------------------------------------------")
print(f" CARPETA DESTINO: {RUTA_CARPETA}")
print("----------------------------------------------------------------")
print(" [ S ] -> Iniciar captura de 10 fotos.")
print(" [ ESC ] -> Salir.")
print("----------------------------------------------------------------")

capturando = False
contador = 0
ultimo_tiempo = time.time()

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        img = image.GetArray()

        # Imagen pequeña para el monitor
        imgDisplay = cv2.resize(img, (0, 0), None, escala_visual, escala_visual)

        if not capturando:
            # --- MODO ESPERA ---
            cv2.putText(imgDisplay, "LISTO. Presiona 's' para capturar", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Recuadro guía
            h_disp, w_disp, _ = imgDisplay.shape
            cv2.rectangle(imgDisplay, (w_disp//2 - 100, 50), (w_disp//2 + 100, h_disp - 50), (255, 255, 0), 1)

        else:
            # --- MODO GRABACIÓN ---
            tiempo_actual = time.time()
            
            cv2.putText(imgDisplay, f"FOTO {contador+1} de {num_imagenes}", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            if tiempo_actual - ultimo_tiempo >= intervalo_segundos:
                contador += 1
                
                # --- AQUÍ ESTÁ EL CAMBIO CLAVE ---
                # Generamos el nombre con AÑO-MES-DIA_HORA-MIN-SEG
                # Ejemplo: botella_2023-10-27_15-30-05.png
                fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                nombre_archivo = f"botella_{fecha_hora}.png"
                
                ruta_completa = os.path.join(RUTA_CARPETA, nombre_archivo)
                
                # Guardamos la imagen
                cv2.imwrite(ruta_completa, img)
                
                print(f" -> Guardada: {nombre_archivo}")
                ultimo_tiempo = tiempo_actual

                if contador >= num_imagenes:
                    print("--- Tanda finalizada ---")
                    capturando = False
                    contador = 0
                    # Abrir carpeta al finalizar
                    try:
                        os.startfile(RUTA_CARPETA)
                    except:
                        pass

        cv2.imshow("Monitor Basler - Captura", imgDisplay)

        key = cv2.waitKey(1) & 0xFF
        if key == 27: # ESC
            break
        elif key == ord('s'):
            if not capturando:
                capturando = True
                contador = 0
                ultimo_tiempo = time.time() - intervalo_segundos
                print("Iniciando nueva tanda de fotos...")

    grabResult.Release()

camera.StopGrabbing()
cv2.destroyAllWindows()
