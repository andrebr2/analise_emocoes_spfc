# /src/analise_emocoes.py

from transformers import pipeline

# Pipeline de classificação multilíngue de emoções
classifier = pipeline(
    "text-classification",
    model="AnasAlokla/multilingual_go_emotions_V1.2",
    top_k=None
)

# Mapeamento do modelo para categorias do TCC
MAPEAMENTO = {
    "joy": "alegria",
    "happiness": "alegria",
    "love": "alegria",
    "optimism": "alegria",
    "anger": "raiva",
    "annoyance": "raiva",
    "disgust": "raiva",
    "sadness": "tristeza",
    "grief": "tristeza",
    "fear": "medo",
    "surprise": "surpresa",
}

def classificar_emocao(tweet_texto):
    resultados = classifier(tweet_texto, top_k=None)

    # se for lista de listas, achamos o primeiro elemento
    if isinstance(resultados[0], list):
        resultados = resultados[0]

    if not resultados:
        return "neutro", 0.0

    # pegamos o resultado de maior score
    r_max = max(resultados, key=lambda x: x['score'])
    label_modelo = r_max['label'].lower()
    score = r_max['score']

    if label_modelo in MAPEAMENTO:
        return MAPEAMENTO[label_modelo], score

    return "neutro", score


def analisar_tweets(tweets):
    for tweet in tweets:
        tweet["emocao"], tweet["confianca"] = classificar_emocao(tweet["texto"])
    return tweets