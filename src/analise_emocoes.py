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
    resultados = classifier(tweet_texto)
    if not resultados:
        return "neutro", 0.0

    for r in sorted(resultados, key=lambda x: x['score'], reverse=True):
        label_modelo = r['label'].lower()
        if label_modelo in MAPEAMENTO:
            return MAPEAMENTO[label_modelo], r["score"]

    return "neutro", 0.0

def analisar_tweets(tweets):
    for tweet in tweets:
        emocao, confianca = classificar_emocao(tweet["texto"])
        tweet["emocao"] = emocao
        tweet["confianca"] = confianca
    return tweets