# import cv2
# import numpy as np
# import utils
# import os

# ########################################################################
# #   PANEL DE CONTROL - VERSIÓN "DARK MODE" & AUTO-ROTACIÓN
# ########################################################################

# # 1. PEGA AQUÍ LA RUTA COMPLETA DE TU FOTO
# RUTA_COMPLETA = r"C:\Users\CAROLINA\Desktop\CAMARAS\PYTHON\imagenes_capturadas\Sesion_2025-12-02_20-38-53\botella_01_20-40-32.png"

# # 2. DATOS PARA LA CALIBRACIÓN
# DISTANCIA_CAMARA_MESA = 41.5   # cm
# DISTANCIA_CAMARA_BOQUILLA = 17.0 # cm
# PIXELES_POR_CM_MESA = 8.0 

# # 3. SENSIBILIDAD A LA OSCURIDAD (0 = Negro absoluto, 255 = Blanco)
# # Si no detecta la boquilla, SUDE este número a 100 o 120.
# # Si detecta sombras raras, BAJA este número a 50.
# UMBRAL_OSCURIDAD = 80 

# ########################################################################

# # Limpieza de ruta
# ruta_limpia = RUTA_COMPLETA.replace('"', '').strip()

# if not os.path.exists(ruta_limpia):
#     print("ERROR: No encuentro el archivo. Revisa la ruta.")
#     exit()

# img = cv2.imread(ruta_limpia)
# if img is None:
#     print("ERROR: OpenCV no pudo abrir la imagen.")
#     exit()

# # Calcular corrección de altura
# factor_correccion = DISTANCIA_CAMARA_BOQUILLA / DISTANCIA_CAMARA_MESA
# PIXELES_POR_CM_REAL = PIXELES_POR_CM_MESA / factor_correccion

# print(f"--- ANALIZANDO ---")
# print(f"Calibración ajustada: {PIXELES_POR_CM_REAL:.2f} px/cm")

# # Configuración Base A4
# scale = 3
# wP = 210 * scale
# hP = 297 * scale

# # --- PASO 1: DETECCIÓN PAPEL A4 ---
# imgContours, conts = utils.getContours(img, minArea=50000, filter=4, draw=True)

# if len(conts) != 0:
#     biggest = conts[0][2]
    
#     # --- CORRECCIÓN DE "ALARGAMIENTO" (AUTO-ROTACIÓN) ---
#     # Revisamos si el contorno detectado es más ancho que alto
#     # Ordenamos puntos para saber la orientación
#     approx = utils.reorder(biggest)
#     pts = approx.reshape(4, 2)
    
#     # Calculamos ancho y alto visual del contorno en la foto original
#     dist_w = np.linalg.norm(pts[0] - pts[1])
#     dist_h = np.linalg.norm(pts[0] - pts[3])
    
#     # Si el ancho es mayor que el alto, invertimos las medidas del papel destino
#     if dist_w > dist_h:
#         print(" -> Orientación detectada: HORIZONTAL (Landscape)")
#         imgWarp = utils.warpImg(img, biggest, hP, wP) # Invertimos wP y hP
#     else:
#         print(" -> Orientación detectada: VERTICAL (Portrait)")
#         imgWarp = utils.warpImg(img, biggest, wP, hP)

#     # --- PASO 2: TRUCO PARA DETECTAR LO "OSCURO" ---
#     # Convertimos a escala de grises
#     imgGray = cv2.cvtColor(imgWarp, cv2.COLOR_BGR2GRAY)
    
#     # APLICAMOS UMBRAL INVERSO:
#     # "Todo lo que sea más oscuro que UMBRAL_OSCURIDAD se vuelve BLANCO puro,
#     #  y todo lo demás se vuelve NEGRO".
#     _, imgBinary = cv2.threshold(imgGray, UMBRAL_OSCURIDAD, 255, cv2.THRESH_BINARY_INV)
    
#     # Convertimos de nuevo a BGR para que utils.getContours no falle
#     imgBinaryBGR = cv2.cvtColor(imgBinary, cv2.COLOR_GRAY2BGR)
    
#     # Mostramos esta imagen "Fantasma" para que entiendas qué ve la computadora
#     cv2.imshow('1. Vision de Oscuridad (Lo blanco es lo oscuro)', imgBinaryBGR)

#     # --- PASO 3: DETECCIÓN SOBRE LA IMAGEN BINARIA ---
#     # Ahora buscamos el contorno blanco (que antes era el hueco negro)
#     imgContours2, conts2 = utils.getContours(imgBinaryBGR, 
#                                              minArea=1000, # Filtramos ruido pequeño
#                                              filter=0, 
#                                              cThr=[50,50], 
#                                              showCanny=False, 
#                                              draw=False)

#     # Dibujamos los resultados sobre la imagen a color (imgWarp) para que se vea bonito
#     imgResultado = imgWarp.copy()
    
#     AREA_MAXIMA_BOQUILLA = 15000 
#     encontrado = False
    
#     if len(conts2) != 0:
#         for obj in conts2:
#             area = obj[1]
#             x, y, w, h = obj[3]
            
#             # Filtro: Ignoramos si es demasiado grande (manchas de sombra gigantes)
#             if area < AREA_MAXIMA_BOQUILLA:
#                 encontrado = True
                
#                 # Dibujar contorno verde
#                 cv2.polylines(imgResultado, [obj[2]], True, (0, 255, 0), 2)
                
#                 # Medir
#                 ancho_cm = round((w / PIXELES_POR_CM_REAL), 2)
                
#                 # Flecha horizontal (Diámetro)
#                 cv2.arrowedLine(imgResultado, (x, y + h//2), (x + w, y + h//2), (255, 0, 255), 3, 8, 0, 0.05)
                
#                 # Texto centrado
#                 texto = f"Dia: {ancho_cm} cm"
#                 font = cv2.FONT_HERSHEY_SIMPLEX
#                 (text_w, text_h), _ = cv2.getTextSize(texto, font, 0.8, 2)
#                 text_x = x + (w // 2) - (text_w // 2)
#                 text_y = y - 10 # Un poco arriba
                
#                 cv2.rectangle(imgResultado, (text_x - 5, text_y - text_h - 5), 
#                               (text_x + text_w + 5, text_y + 5), (0,0,0), -1)
#                 cv2.putText(imgResultado, texto, (text_x, text_y), font, 0.8, (255, 255, 255), 2)
                
#                 print(f" -> BOQUILLA DETECTADA: {ancho_cm} cm")

#     if not encontrado:
#         print("AVISO: No encontré zonas oscuras del tamaño adecuado.")
#         print("INTENTA: Subir el valor de UMBRAL_OSCURIDAD en el código (línea 19).")

#     cv2.imshow('2. Resultado Final', imgResultado)
#     print("\nPresiona cualquier tecla para cerrar.")
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

# else:
#     print("\n[FALLO] -> No se detectó la hoja A4.")



import cv2
import numpy as np
import utils
import os

########################################################################
#   PANEL DE CONTROL - MEDICIÓN MANUAL (LIMPIO)
########################################################################

# 1. PEGA AQUÍ LA RUTA COMPLETA DE TU FOTO
RUTA_COMPLETA = r"C:\Users\CAROLINA\Desktop\CAMARAS\PYTHON\imagenes_capturadas\Sesion_2025-12-02_20-38-53\botella_01_20-40-32.png"

# 2. DATOS PARA LA CALIBRACIÓN (Factor Corregido)
# Usando 19.66 px/cm de base para corregir el error de medición.
DISTANCIA_CAMARA_MESA = 41.5      # cm
DISTANCIA_CAMARA_BOQUILLA = 17.0  # cm
PIXELES_POR_CM_MESA = 19.66       # px/cm (Valor corregido)

########################################################################
# Variables Globales para la medición manual
puntos_medicion = []
PIXELES_POR_CM_REAL = 0.0 # Se calculará más adelante
# La imagen donde se realizan los clics (la imagen de resultado)
imgResultado = None 
# Texto de instrucción
TEXTO_INSTRUCCION = "2 Clicks para medir diametro. 'r' para reiniciar. ESC para salir."
########################################################################

# --- Función de Callback del Ratón para la Medición ---
def mouse_callback(event, x, y, flags, param):
    global puntos_medicion, imgResultado, PIXELES_POR_CM_REAL, TEXTO_INSTRUCCION
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Si ya hay 2 puntos, no se agrega más hasta que se reinicie
        if len(puntos_medicion) >= 2:
            return

        puntos_medicion.append((x, y))
        print(f"Punto capturado: ({x}, {y})")

        # Dibujar el punto
        cv2.circle(imgResultado, (x, y), 5, (0, 0, 255), -1)
        
        # Si ya tenemos dos puntos, calculamos la distancia
        if len(puntos_medicion) == 2:
            pt1 = puntos_medicion[0]
            pt2 = puntos_medicion[1]
            
            # Dibujar la línea de medición
            cv2.line(imgResultado, pt1, pt2, (255, 0, 255), 2)
            
            # Calcular distancia en píxeles (usa la función utils.findDis)
            distancia_px = utils.findDis(pt1, pt2)
            
            # Convertir a cm usando el factor de calibración
            ancho_cm = round((distancia_px / PIXELES_POR_CM_REAL), 2)
            
            # Mostrar el resultado
            texto = f"Dia: {ancho_cm} cm"
            cv2.putText(imgResultado, texto, (pt1[0], pt1[1] - 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            
            TEXTO_INSTRUCCION = f"MEDIDA: {ancho_cm} cm. 'r' para otra medición. ESC para salir."
            
        # Actualizar la ventana
        mostrar_imagen_resultado()

# --- Función para mostrar la ventana de resultado con instrucciones ---
def mostrar_imagen_resultado():
    global imgResultado, TEXTO_INSTRUCCION
    
    if imgResultado is not None:
        # Crear una copia de la imagen para dibujar las instrucciones
        img_display = imgResultado.copy()
        
        # Colocar instrucciones en la esquina superior izquierda
        # Dibujar un rectángulo negro como fondo para mejor visibilidad del texto
        (text_w, text_h), baseline = cv2.getTextSize(TEXTO_INSTRUCCION, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        cv2.rectangle(img_display, (5, 5), (15 + text_w, 35), (0, 0, 0), -1)
        
        cv2.putText(img_display, TEXTO_INSTRUCCION, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2) # Texto blanco
        
        cv2.imshow('Resultado Final (Medicion Manual)', img_display)


# --- INICIO DEL PROGRAMA PRINCIPAL ---

# Limpieza de ruta
ruta_limpia = RUTA_COMPLETA.replace('"', '').strip()

if not os.path.exists(ruta_limpia):
    print("ERROR: No encuentro el archivo. Revisa la ruta.")
    exit()

img = cv2.imread(ruta_limpia)
if img is None:
    print("ERROR: OpenCV no pudo abrir la imagen.")
    exit()

# Calcular corrección de altura y factor de calibración real
factor_correccion = DISTANCIA_CAMARA_BOQUILLA / DISTANCIA_CAMARA_MESA
PIXELES_POR_CM_REAL = PIXELES_POR_CM_MESA / factor_correccion

print(f"--- ANALIZANDO ---")
print(f"Calibración ajustada: {PIXELES_POR_CM_REAL:.2f} px/cm")

# Configuración Base A4
scale = 3
wP = 210 * scale
hP = 297 * scale

# --- PASO 1: DETECCIÓN PAPEL A4 y CORRECCIÓN DE PERSPECTIVA ---
# Dibujar True para ver el contorno del papel detectado en la imagen original
imgContours, conts = utils.getContours(img, minArea=50000, filter=4, draw=True) 

if len(conts) != 0:
    biggest = conts[0][2]
    
    # Auto-Rotación (Lógica para determinar si el A4 está vertical u horizontal)
    approx = utils.reorder(biggest)
    pts = approx.reshape(4, 2)
    dist_w = np.linalg.norm(pts[0] - pts[1])
    dist_h = np.linalg.norm(pts[0] - pts[3])
    
    if dist_w > dist_h:
        print(" -> Orientación detectada: HORIZONTAL (Landscape)")
        imgWarp = utils.warpImg(img, biggest, hP, wP) # Invertimos wP y hP
    else:
        print(" -> Orientación detectada: VERTICAL (Portrait)")
        imgWarp = utils.warpImg(img, biggest, wP, hP)

    # El resultado para medición es la imagen a color con perspectiva corregida
    imgResultado = imgWarp.copy()

    # --- PASO 2: CONFIGURACIÓN DE MEDICIÓN MANUAL ---
    cv2.namedWindow('Resultado Final (Medicion Manual)')
    # Asignar la función del ratón a la ventana de resultado
    cv2.setMouseCallback('Resultado Final (Medicion Manual)', mouse_callback)

    print("\n--- MODO DE MEDICIÓN MANUAL ACTIVADO ---")
    print("INSTRUCCIÓN: Haz dos (2) clics en la imagen transformada para medir el diámetro.")
    
    while True:
        mostrar_imagen_resultado()
        
        k = cv2.waitKey(1) & 0xFF
        
        if k == 27: # ESC para salir
            break
        
        if k == ord('r'): # 'r' para reiniciar medición
            puntos_medicion = []
            imgResultado = imgWarp.copy() # Reiniciar imagen a la original warpeada
            TEXTO_INSTRUCCION = "2 Clicks para medir diametro. 'r' para reiniciar. ESC para salir."
            print("Medición reiniciada.")

    cv2.destroyAllWindows()

else:
    print("\n[FALLO] -> No se detectó la hoja A4. Asegúrate que esté visible y plana.")
    cv2.imshow('Imagen Original', cv2.resize(img, (0, 0), None, 0.4, 0.4))
    cv2.waitKey(0)
    cv2.destroyAllWindows()







