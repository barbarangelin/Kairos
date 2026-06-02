import tensorflow as tf
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def carregar_imagem_de_analise(imagem_caminho):
    imagem = Image.open(imagem_caminho)
    imagem = imagem.convert("L")
    imagem = imagem.resize((28,28))
    imagem_array = np.array(imagem)
    imagem_array = 255 - imagem_array
    imagem_array = imagem_array / 255
    return imagem_array

dados_roupas = tf.keras.datasets.fashion_mnist
(x_treino, y_treino), (x_teste, y_teste) = dados_roupas.load_data()

classes_do_dataset_fashion = [
    "Camiseta",
    "Calça",
    "Pullover",
    "Vestido",
    "Casaco",
    "Sandália",
    "Camisa",
    "Tênis",
    "Bolsa",
    "Bota"
]

x_treino = x_treino / 255
x_teste = x_teste / 255

modelo_rede_neural = tf.keras.models.Sequential(
    [tf.keras.layers.Flatten(input_shape=(28,28)),
     tf.keras.layers.Dense(128, activation="relu"),
     tf.keras.layers.Dense(10, activation="softmax")]
)

modelo_rede_neural.compile(optimizer = "adam",
                           loss="sparse_categorical_crossentropy",
                           metrics=["accuracy"])

modelo_rede_neural.fit(x_treino, y_treino, epochs = 5)
loss, accuracy = modelo_rede_neural.evaluate(x_teste, y_teste)
print("Acurácia do modelo: ", accuracy)

imagem_de_entrada = np.expand_dims(carregar_imagem_de_analise("fotoParaAnalise.jpg"), axis=0)
previsao_da_imagem = modelo_rede_neural.predict(imagem_de_entrada)
classe_de_previsao = np.argmax(previsao_da_imagem)
print("Classe prevista: ", classes_do_dataset_fashion[classe_de_previsao])

for i in range(10):
    print(f"{classes_do_dataset_fashion[i]}: {previsao_da_imagem[0][i] * 100:.2f}%")

plt.imshow(carregar_imagem_de_analise("fotoParaAnalise.jpg"), cmap="gray")

plt.title(
    f"Previsão da rede neural: {classes_do_dataset_fashion[classe_de_previsao]}"
)

plt.show()