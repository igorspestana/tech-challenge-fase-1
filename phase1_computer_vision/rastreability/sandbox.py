import cv2

tracker = cv2.TrackerKCF_create() # Captura video de arquivos ou câmera
# tracker = cv2.TrackerCSRT_create() # Captura video de arquivos ou câmera
video = cv2.VideoCapture('videos/video1.mp4') # Captura video de arquivos ou câmeras

ok, frame = video.read() # Lê o primeiro quadro do vídeo. "ok" == True | "frame" == imagem do primeiro quadro

bbox = cv2.selectROI(frame) # Permite ao usuário selecionar uma Região de Interesses (ROI)

# print(box)

ok = tracker.init(frame, bbox) # Inicializa o rastreador com o primeiro frame e o bbox selecionado
# print(ok)

while True: # Inicia um loop Infinito para processar cada quadro do video
    ok, frame = video.read()
    # print(ok) # Verifica se a imagem esta sendo capturada (True)
    if not ok:
        break # Se a leitura do quadro falhar, o loop será interrompido
    
    ok, bbox = tracker.update(frame) # Atualiza o bbox
    print(bbox) # Verifica se as coordenadas do bbox estao sendo capturadas (0.0, 0.0, 0.0, 0.0)
    
    # Imprimindo o bounding box
    if ok:
        (x, y, w, h) = [int(v) for v in bbox]
        cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 255, 0), 2, 1)
        
    else:
        cv2.putText(frame,
                    "Error",
                    (100, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
        )
    
    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1) & 0XFF == 27: # ESC
        break
        