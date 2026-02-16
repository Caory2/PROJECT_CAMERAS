from pypylon import pylon
import cv2
import numpy as np
import utils  # Asegúrate de que utils.py esté en la misma carpeta

########################################################################
# CONFIGURACIÓN GENERAL
########################################################################
scale = 3
wP = 210 * scale
hP = 297 * scale

# --- CALIBRACIÓN (IMPORTANTE) ---
# Este es el valor que encontramos con tu caja de 10cm.
# Significa que 8 píxeles en la pantalla equivalen a 1 cm real.
FACTOR_CALIBRACION = 8.0  

# --- FILTRO DE TAMAÑO PARA LA BOTELLA ---
# Cualquier objeto con área mayor a esto se considera "Cuerpo de botella" (se ignora).
# Cualquier objeto menor, se considera "Boquilla" (se mide).
# Calculado para una botella de 8cm de cuerpo.
AREA_MAXIMA_BOQUILLA = 15000 
########################################################################

# --- 1. CONEXIÓN CON CÁMARA BASLER ---
try:
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()
except Exception as e:
    print("Error Crítico: No se detectó ninguna cámara Basler conectada.")
    print("Verifica el cable USB y los drivers.")
    exit()

# Configuración para video fluido
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

print("----------------------------------------------------")
print(" SISTEMA DE MEDICIÓN DE BOQUILLAS - LISTO")
print(f" Calibración: {FACTOR_CALIBRACION} px/cm")
print(" Presiona 'q' o 'ESC' en la ventana para salir.")
print("----------------------------------------------------")

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Obtener imagen de la cámara
        image = converter.Convert(grabResult)
        img = image.GetArray()

        # ----------------------------------------------------------------
        # PASO 1: DETECTAR LA HOJA DE PAPEL (REFERENCIA)
        # ----------------------------------------------------------------
        # filter=4: Buscamos un rectángulo (la hoja)
        imgContours, conts = utils.getContours(img, minArea=50000, filter=4, draw=True)

        if len(conts) != 0:
            # Si encontramos el papel, lo recortamos y enderezamos (Warp)
            biggest = conts[0][2]
            imgWarp = utils.warpImg(img, biggest, wP, hP)

            # ----------------------------------------------------------------
            # PASO 2: DETECTAR LA BOTELLA DENTRO DEL PAPEL
            # ----------------------------------------------------------------
            # filter=0: Detectamos cualquier forma (círculos)
            # minArea=100: Para ver cosas pequeñas como tapas
            imgContours2, conts2 = utils.getContours(imgWarp,
                                                     minArea=100, 
                                                     filter=0,
                                                     cThr=[50,50], 
                                                     showCanny=False, # Pon True si quieres ver blanco/negro
                                                     draw=False)

            if len(conts2) != 0:
                for obj in conts2:
                    # Obtenemos datos del objeto
                    area = obj[1]
                    # x,y = posición; w=ancho, h=alto
                    x, y, w, h = obj[3] 

                    # Imprimimos el área para depuración (Texto amarillo)
                    cv2.putText(imgContours2, f"Area:{int(area)}", (x, y + 20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                    # --- LÓGICA INTELIGENTE: ¿ES CUERPO O BOQUILLA? ---
                    if area < AREA_MAXIMA_BOQUILLA:
                        # >>> ES LA BOQUILLA (Círculo pequeño) <<<
                        
                        # 1. Dibujamos borde VERDE
                        cv2.polylines(imgContours2, [obj[2]], True, (0, 255, 0), 2)
                        
                        # 2. Matemáticas de Medición
                        ancho_cm = round((w / FACTOR_CALIBRACION), 1)
                        alto_cm = round((h / FACTOR_CALIBRACION), 1)
                        
                        # 3. Dibujar Flechas de Cota
                        # Flecha Horizontal (Ancho/Diámetro)
                        cv2.arrowedLine(imgContours2, (x, y + h//2), (x + w, y + h//2),
                                        (255, 0, 255), 3, 8, 0, 0.05)
                        # Flecha Vertical (Largo)
                        cv2.arrowedLine(imgContours2, (x + w//2, y), (x + w//2, y + h),
                                        (255, 0, 255), 3, 8, 0, 0.05)
                        
                        # 4. Poner el texto con la medida final
                        cv2.putText(imgContours2, f'{ancho_cm}cm', (x + w + 10, y + h // 2), 
                                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.5, (255, 0, 255), 2)
                        
                    else:
                        # >>> ES EL CUERPO DE LA BOTELLA (Círculo gigante) <<<
                        # Lo dibujamos en ROJO para indicar que lo ignoramos
                        cv2.polylines(imgContours2, [obj[2]], True, (0, 0, 255), 2)

            # Mostrar la ventana de medidas
            cv2.imshow('A4 - Medidas Basler', imgContours2)

        # Mostrar imagen original reducida (para referencia)
        img = cv2.resize(img, (0, 0), None, 0.5, 0.5)
        cv2.imshow('Vista Original', img)

    # Cerrar con ESC o 'q'
    key = cv2.waitKey(1)
    if key == 27 or key == ord('q'):
        break

camera.StopGrabbing()
cv2.destroyAllWindows()
