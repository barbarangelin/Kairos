import tensorflow as tf
import numpy as np
from PIL import Image
import cv2 as cv

modelo_original_de_rede_neural = tf.keras.models.load_model("keras_model.h5", compile=False)
with open("labels.txt", "r") as f:
    classes_do_dataset = [linha.strip() for linha in f.readlines()]

def analise_da_imagem(imagem):
    
    imagem = cv.cvtColor(imagem, cv.COLOR_BGR2RGB)
    imagem_analisada = Image.fromarray(imagem)

    imagem_analisada = imagem_analisada.resize((224,224))
    imagem_analisada_array = np.array(imagem_analisada)
    imagem_analisada_array = (imagem_analisada_array.astype(np.float32) / 127.5) - 1.0
    imagem_analisada_array = np.expand_dims(imagem_analisada_array, axis=0)

    previsao_feita_pela_rede_neural = modelo_original_de_rede_neural.predict(imagem_analisada_array)
    classe_da_previsao = np.argmax(previsao_feita_pela_rede_neural)
    confianca_da_classe_prevista = previsao_feita_pela_rede_neural[0][classe_da_previsao]
    nome_da_classe = classes_do_dataset[classe_da_previsao].split(' ', 1)[1]
    print("Situação identificada pela rede neural = ", nome_da_classe)

    return nome_da_classe, confianca_da_classe_prevista


