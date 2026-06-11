import cv2 as cv
import mysql.connector as sql
import dotenv as env
import os
import rede_neural_keras

def registrar_observacao_no_MySQL():
    banco = sql.connect(host= os.getenv("HOST_MYSQL"), username= os.getenv("USERNAME_MYSQL"),password=
                        os.getenv("PASSWORD_MYSQL"), database= os.getenv("DATABASE_MYSQL"))
    if banco.is_connected:
        print("Conexão com o banco foi bem sucedida")
        cursor = banco.cursor()
        comando = "insert into observacao (Tempo_de_observacao_total, Tempo_em_foco, Tempo_cabeca_inclinada, Tempo_sonolento, Tempo_olhando_para_o_lado, Tempo_usando_celular, Tempo_ausente,  Aproveitamento) values (%s,%s,%s,%s,%s,%s,%s,%s)"
        valores = (round(tempo_de_observacao_total), round(tempo_em_foco), round(tempo_cabeca_inclinada), round(tempo_sonolento),
                   round(tempo_olhando_para_o_lado), round(tempo_usando_celular), round(tempo_ausente), tempo_em_foco/tempo_de_observacao_total)
        cursor.execute(comando,valores)
        banco.commit()
        print("O novo registro de observação Kairos foi inserido no banco de dados")
        cursor.close()
        banco.close()

"""BGR"""
def sinalizador_textual_de_situação(imagem, classe, confianca_classe):
    if classe == "Focada(o)":
        cor = (0, 255, 0)
    elif classe == "Cabeca inclinada":
        cor = (0, 255, 255)
    elif classe == "Sonolenta (o)":
        cor = (0, 165, 255)
    elif classe == "Olhando para o lado":
        cor = (0, 0, 255)
    elif classe == "Usando celular":
        cor = (128, 0, 128)
    else:
        cor = (0, 0, 0)
    return cv.putText(imagem, classe, (20,50), cv.FONT_HERSHEY_SIMPLEX, 1.5, cor, 5), cv.putText(imagem, str(confianca_classe), (20,100), cv.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)


def sinalizador_de_status (imagem):
    cv.putText(imagem, "Tempo total = " + str(round(tempo_de_observacao_total)) + "(s)", (20,300), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv.putText(imagem, "Tempo em foco = " + str(round(tempo_em_foco)) + "(s)", (20,325), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv.putText(imagem, "Tempo de cabeca inclinada = " + str(round(tempo_cabeca_inclinada)) + "(s)", (20,350), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv.putText(imagem, "Tempo sonolenta(o) = " + str(round(tempo_sonolento)) + "(s)", (20,375), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
    cv.putText(imagem, "Tempo olhando para o lado = " + str(round(tempo_olhando_para_o_lado)) + "(s)", (20,400), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv.putText(imagem, "Tempo usando celular = " + str(round(tempo_usando_celular)) + "(s)", (20,425), cv.FONT_HERSHEY_SIMPLEX, 0.6, (128, 0, 128), 2)
    cv.putText(imagem, "Tempo ausente = " + str(round(tempo_ausente)) + "(s)", (20,450), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)


tempo_de_observacao_total = 0
tempo_em_foco = 0
tempo_cabeca_inclinada = 0
tempo_sonolento = 0
tempo_olhando_para_o_lado = 0
tempo_usando_celular = 0
tempo_ausente = 0

def atualizar_contadores_de_tempo(situacao):
    global tempo_de_observacao_total, tempo_em_foco, tempo_cabeca_inclinada, tempo_sonolento, tempo_olhando_para_o_lado, tempo_usando_celular, tempo_ausente
    tempo_de_observacao_total += 0.1
    if situacao == "Focada(o)":
        tempo_em_foco += 0.1
    elif situacao == "Cabeca inclinada":
        tempo_cabeca_inclinada += 0.1
    elif situacao == "Sonolenta (o)":
        tempo_sonolento += 0.1
    elif situacao == "Olhando para o lado":
        tempo_olhando_para_o_lado += 0.1
    elif situacao == "Usando celular":
        tempo_usando_celular += 0.1
    elif situacao == "Ausente":
        tempo_ausente += 0.1

def webcam_CV2():
    caputura_de_imagens = cv.VideoCapture(0)
    validacao, frame = caputura_de_imagens.read()
    while validacao:
        validacao, frame = caputura_de_imagens.read()
        frame = cv.flip(frame,1)
        situação_verificada, confiança = rede_neural_keras.analise_da_imagem(frame)
        atualizar_contadores_de_tempo(situação_verificada)
        sinalizador_textual_de_situação(frame, situação_verificada, confiança)
        sinalizador_de_status(frame)
        cv.imshow('Kairos', frame)
        if cv.waitKey(100) == 27:
            break
    caputura_de_imagens.release()
    cv.destroyWindow("Kairos")
    registrar_observacao_no_MySQL()
    

if __name__ == '__main__':
    env.load_dotenv()
    webcam_CV2()
