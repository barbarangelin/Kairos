import cv2 as cv
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from PyQt6 import QtWidgets,uic, QtGui
import smtplib as smtp
from email.message import EmailMessage
import matplotlib.pyplot as plt
import mysql.connector as sql
from winotify import Notification, audio
import dotenv as env
import os
import sys

import rede_neural_keras


def visualizar_notificacao_desktop(titulo, mensagem):
    caminho_pasta_projeto_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_icone_notificacao = os.path.join(caminho_pasta_projeto_atual,"imgs","notificacao_icone.png")
    notificacao_desktop = Notification(app_id="KAIROS", title=titulo, icon=caminho_icone_notificacao,
                                       msg=mensagem, duration="short")
    notificacao_desktop.set_audio(audio.Mail, loop=False)
    notificacao_desktop.show()

def gerar_grafico_pizza_focado_desfocado():
    fatias = [tempo_em_foco,(tempo_cabeca_inclinada+tempo_sonolento+tempo_olhando_para_o_lado+tempo_usando_celular), tempo_ausente]
    status = ["Focado(a)","Desfocado(a)","Ausente"]
    cores = ["green", "red", "black"]
    plt.figure(figsize=(8,5))
    plt.pie(fatias, colors=cores, startangle=90, shadow=True)
    plt.title("Tempo total em segundos passado focado, desfocado e ausente")
    plt.legend(status, title="Stats", loc="center left", bbox_to_anchor=(0.9,0.5))
    plt.savefig("grafico_pizza_focado_desfocado.png")
    plt.close()

def gerar_grafico_barra_tempo_desfocado():
    status = ["Cabeca inclinada", "Sonolento(a)", "Olhando para o lado", "Usando celular"]
    tempo_por_status = [tempo_cabeca_inclinada, tempo_sonolento, tempo_olhando_para_o_lado, tempo_usando_celular]
    cores_por_status = ["yellow", "orange", "red", "purple"]
    plt.figure(figsize=(10, 5))
    plt.barh(status, tempo_por_status, color=cores_por_status)
    plt.subplots_adjust(left=0.25, right=0.95, top=0.85, bottom=0.15)
    plt.ylabel("Status")
    plt.xlabel("Tempo (s)")
    plt.title("Tempo gasto durante cada status de desfoque")
    plt.savefig("grafico_barras_tempos_de_desfoque.png")
    plt.close()


def enviar_email_via_smtp(destinatario):
    mail_mensagem = EmailMessage()
    mail_mensagem['Subject'] = "KAIROS - HISTORICO DE OBSERVACOES"
    mail_mensagem['From'] = os.getenv("EMAIL")
    mail_mensagem['To'] = destinatario
    mail_mensagem.set_content("Segue em anexo os dados do último monitoramento KAIROS")
    
    gerar_grafico_pizza_focado_desfocado()
    gerar_grafico_barra_tempo_desfocado()

    with open("grafico_pizza_focado_desfocado.png", 'rb') as grafico_pizza_arquivo:
        grafico_pizza = grafico_pizza_arquivo.read()
        mail_mensagem.add_attachment(grafico_pizza, maintype='image', subtype='png', filename='grafico_pizza_focado_desfocado.png')

    with open("grafico_barras_tempos_de_desfoque.png", 'rb') as grafico_barras_arquivo:
        grafico_barras = grafico_barras_arquivo.read()
        mail_mensagem.add_attachment(grafico_barras, maintype='image', subtype='png', filename='grafico_barras_tempos_de_desfoque.png')

    with smtp.SMTP('smtp.gmail.com', 587) as servidor_smtp_gmail:
        servidor_smtp_gmail.starttls()
        servidor_smtp_gmail.login(os.getenv("EMAIL"), os.getenv("SENHA_EMAIL"))
        servidor_smtp_gmail.send_message(mail_mensagem)

    os.remove("grafico_pizza_focado_desfocado.png")
    os.remove("grafico_barras_tempos_de_desfoque.png")



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

def resetar_contadores_de_tempo():
    global tempo_de_observacao_total, tempo_em_foco, tempo_cabeca_inclinada, tempo_sonolento, tempo_olhando_para_o_lado, tempo_usando_celular, tempo_ausente
    tempo_de_observacao_total = 0
    tempo_em_foco = 0
    tempo_cabeca_inclinada = 0
    tempo_sonolento = 0
    tempo_olhando_para_o_lado = 0
    tempo_usando_celular = 0
    tempo_ausente = 0


def webcam_CV2(gui):
    resetar_contadores_de_tempo()
    gui.Start.setEnabled(False)
    gui.Finish.setEnabled(True)
    gui.finalizar_monitoramento = False
    gui.Finish.clicked.connect(lambda:maingui_Finish_clicado(gui))
    caputura_de_imagens = cv.VideoCapture(0)
    while gui.isVisible() and not gui.finalizar_monitoramento:
        validacao, frame = caputura_de_imagens.read()
        frame = cv.flip(frame,1)
        situação_verificada, confiança = rede_neural_keras.analise_da_imagem(frame)
        atualizar_contadores_de_tempo(situação_verificada)
        sinalizador_textual_de_situação(frame, situação_verificada, confiança)
        sinalizador_de_status(frame)
        frame_formato_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        altura, largura, _ = frame_formato_rgb.shape
        qt6_img_compativel = QtGui.QImage(frame_formato_rgb.data, largura, altura, largura*3, QtGui.QImage.Format.Format_RGB888)
        gui.webcam.setPixmap(QtGui.QPixmap.fromImage(qt6_img_compativel).scaled(gui.webcam.width(),gui.webcam.height()))
        QtWidgets.QApplication.processEvents()
        if cv.waitKey(100) == 27:
            break
    caputura_de_imagens.release()
    gui.webcam.clear()
    registrar_observacao_no_MySQL()
    gui.Start.setEnabled(True)
    gui.Relatorio_ultimo.setEnabled(True)

def maingui_Finish_clicado(gui):
    gui.Finish.setEnabled(False)
    gui.finalizar_monitoramento = True

def verificar_email (gui):
    email_do_destinaratio = gui.email_caixa.toPlainText()
    if email_do_destinaratio != "":
        enviar_email_via_smtp(email_do_destinaratio)
        gui.close()
    else:
        gui.texto_aviso.setText("email nao pode ser nulo")
        gui.texto_aviso.setStyleSheet("color: red;")

def email_input_dialago_gui():
    email_input_gui = uic.loadUi("./GUI/email_input_dialago.ui")
    email_input_gui.Ir.clicked.connect(lambda: verificar_email(email_input_gui))
    email_input_gui.exec()

def musica_background_gui():
    global musica_background
    musica_background = QSoundEffect()
    musica_background.setSource(QUrl.fromLocalFile("./music/Villa-Lobos_Melodia-Sentimental.wav"))
    musica_background.setLoopCount(-2)
    musica_background.setVolume(1.0)
    musica_background.play()

def interface_maingui():
    maingui = uic.loadUi("./GUI/maingui.ui")
    musica_background_gui()
    maingui.Start.clicked.connect(lambda: webcam_CV2(maingui))
    maingui.Relatorio_ultimo.clicked.connect(email_input_dialago_gui)
    maingui.Relatorio_completo.clicked.connect(email_input_dialago_gui)
    maingui.show()
    return maingui
    

if __name__ == '__main__':
    env.load_dotenv()
    aplicacao_gui = QtWidgets.QApplication(sys.argv)
    kairos_gui = interface_maingui()
    aplicacao_gui.exec()