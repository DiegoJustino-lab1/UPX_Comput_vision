#opencv
import cv2
import pytesseract
import numpy as np
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\Tesseract.exe"

# Inicia a captura de vídeo da câmera padrão (geralmente a webcam do laptop)
cap = cv2.VideoCapture(0)

# Adiciona uma variável de controle
placa_detectada = False

# Abre o arquivo dados.csv em modo de anexação
with open("dados.csv", "a") as arquivo:
    while True:
        # Captura um único frame
        ret, frame = cap.read()

        # Se o frame foi capturado corretamente, ret é True
        if ret:
            # Converte a imagem para escala de cinza
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Aplica um desfoque para reduzir o ruído
            blur = cv2.bilateralFilter(gray, 11, 17, 17)

            # Encontra as bordas na imagem
            edges = cv2.Canny(blur, 30, 200)

            # Encontra os contornos na imagem
            contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Se a placa já foi detectada, pula o restante do loop
            if placa_detectada:
                continue

            # Ordena os contornos por área e mantém os maiores
            contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]

            # Itera sobre os contornos para encontrar a placa
            for contour in contours:
                # Aproxima o contorno
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

                # Se o contorno tem 4 vértices, assumimos que encontramos a placa
                if len(approx) == 4:
                    # Extrai a região da placa
                    x, y, w, h = cv2.boundingRect(approx)
                    plate = gray[y:y+h, x:x+w]

                    # Processa a região da placa com o Tesseract
                    resultado = pytesseract.image_to_string(plate)

                    # Verifica se o resultado corresponde ao padrão
                    if re.match(r'^[A-Za-z]{3}-\d{4}$', resultado) or re.match(r'^[A-Za-z]{3}\d{1}[A-Za-z]{1}\d{2}$', resultado) or re.match(r'^[A-Za-z]{3}\s\d{1}[A-Za-z]{1}\d{2}$', resultado) or re.match(r'^[A-Za-z]{3}\s\d{4}$', resultado):
                        print("Texto detectado:")
                        print(resultado)

                        # Escreve o resultado no arquivo
                        arquivo.write(resultado + "\n")

                        # Pergunta ao usuário se deseja liberar a passagem
                        print("Deseja liberar a passagem? (y/n)")
                        key = cv2.waitKey(0) # Aguarda até que uma tecla seja pressionada
                        if key == ord('y'):
                            print("Passagem liberada!")
                        elif key == ord('n'):
                            print("Passagem não liberada!")

                    break

            # Mostra o frame na janela
            cv2.imshow('Camera', frame)

        # Se a tecla 'q' for pressionada, sai do loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Libera os recursos da câmera e fecha as janelas
cap.release()
cv2.destroyAllWindows()