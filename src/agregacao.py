# /src/agregacao.py

from collections import Counter
from .config import EMOCOES

def percentual_emocoes(tweets):
    total = len(tweets)
    if total == 0:
        return {}

    contador = Counter([t["emocao"] for t in tweets])

    percentuais = {
        emo: (contador.get(emo, 0) / total) * 100
        for emo in EMOCOES
    }

    return percentuais