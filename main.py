import matplotlib.pyplot as plt
import cv2 as cv
import tensorflow as tf
import mediapipe as mp
from mediapipe.tasks import python as py
from mediapipe.tasks.python import vision as vsn

"""--------------------- código oficial do google ---------------------"""
def draw_landmarks_on_image(rgb_image, detection_result):
    if not detection_result or not detection_result.hand_landmarks:
        return rgb_image
        
    hand_landmarks_list = detection_result.hand_landmarks
    frame_revisionado = rgb_image.copy()

    for hand_landmarks in hand_landmarks_list:
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands

        from mediapipe.framework.formats import landmark_pb2
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) 
            for landmark in hand_landmarks
        ])

        mp_drawing.draw_landmarks(
            frame_revisionado,
            hand_landmarks_proto,
            mp_hands.HAND_CONNECTIONS
        )

        
    return frame_revisionado
"""--------------------- código oficial do google ---------------------"""

def verificacao_do_joinha(resultado_da_deteccao):
    for hand_landmarks in resultado_da_deteccao.hand_landmarks:
        pontos_da_mao = hand_landmarks
        polegar_para_cima = pontos_da_mao[3].y > pontos_da_mao[4].y
        indicador_fechado = pontos_da_mao[8].y > pontos_da_mao[5].y
        pitoco_fechado = pontos_da_mao[12].y > pontos_da_mao[9].y
        anelar_fechado = pontos_da_mao[16].y > pontos_da_mao[13].y
        mindinho_fechado = pontos_da_mao[20].y > pontos_da_mao[17].y
        if polegar_para_cima and indicador_fechado and pitoco_fechado and anelar_fechado and mindinho_fechado:
            return True
        else:
            return False


opcoes_base = py.BaseOptions(model_asset_path='hand_landmarker.task')
opcoes = vsn.HandLandmarkerOptions(base_options=opcoes_base,
                                       num_hands=2)
detector = vsn.HandLandmarker.create_from_options(opcoes)

def webcam_CV2():
    caputura_de_imagens = cv.VideoCapture(0)
    caputura_de_imagens.set(cv.CAP_PROP_FRAME_WIDTH, 1120)
    caputura_de_imagens.set(cv.CAP_PROP_FRAME_HEIGHT, 1120)
    validacao, frame = caputura_de_imagens.read()
    while validacao:
        validacao, frame = caputura_de_imagens.read()
        frame = cv.flip(frame,1)
        frame_mp_formato = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv.cvtColor(frame, cv.COLOR_BGR2RGB))
        resultado_da_deteccao = detector.detect(frame_mp_formato)
        frame_revisionado= draw_landmarks_on_image(frame_mp_formato.numpy_view(), resultado_da_deteccao)
        if verificacao_do_joinha(resultado_da_deteccao):
            print("há um joinha!!!! Foto tirada xisssss")
            break
        if frame_revisionado is not None:
            cv.imshow('WebcamOpenCV2', cv.cvtColor(frame_revisionado, cv.COLOR_RGB2BGR))
        else:
            cv.imshow('WebcamOpenCV2', frame)
        cv.waitKey(1)
    cv.imwrite("fotoParaAnalise.jpg", frame)

if __name__ == '__main__':
    webcam_CV2()
