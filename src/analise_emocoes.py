# /src/analise_emocoes.py

import torch
import unicodedata
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from .config import MODELO_PATH, ID_TO_EMOCAO, MAX_LEN


# ==================================================
# CARREGAMENTO DO MODELO FINE-TUNING
# ==================================================

def carregar_modelo():
    """
    Carrega o modelo BERTimbau fine-tuning.
    O modelo deve estar salvo em MODELO_PATH/final
    """
    model_dir = os.path.join(MODELO_PATH, "final")

    if not os.path.exists(model_dir):
        raise RuntimeError(
            f"Modelo não encontrado em {model_dir}. "
            "Execute primeiro o fine-tuning com src/fine_tuning.py"
        )

    print(f"[INFO] Carregando modelo de: {model_dir}")

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)

    # Configura para modo de avaliação
    model.eval()

    # Verifica dispositivo disponível
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    print(f"[INFO] Modelo carregado em: {device}")

    return tokenizer, model, device


# Carrega o modelo uma única vez
tokenizer, model, device = carregar_modelo()


def remover_acentos(texto):
    """
    Remove acentos para padronizar texto.
    """
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def classificar_emocao(texto):
    """
    Classifica emoção dominante em um texto usando o BERTimbau fine-tuning.

    Args:
        texto (str): Texto do tweet já limpo

    Returns:
        tuple: (emocao, confianca)
    """
    if not texto or not texto.strip():
        return "neutro", 0.0

    # Pré-processamento
    texto = remover_acentos(texto.lower())

    try:
        # Tokeniza o texto
        inputs = tokenizer(
            texto,
            truncation=True,
            padding="max_length",
            max_length=MAX_LEN,
            return_tensors="pt"
        ).to(device)

        # Faz a predição
        with torch.no_grad():
            outputs = model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
            prediction = torch.argmax(probabilities, dim=-1)
            confidence = probabilities[0][prediction[0]].item()

        # Converte ID para emoção
        emocao = ID_TO_EMOCAO[prediction[0].item()]

        return emocao, confidence

    except Exception as e:
        print(f"[ERRO] Falha na classificação: {e}")
        return "neutro", 0.0


def analisar_tweets(tweets):
    """
    Aplica análise de emoções a uma lista de tweets.
    Mantém a mesma interface do código original.

    Args:
        tweets (list): Lista de dicionários com os tweets

    Returns:
        list: Mesma lista com as chaves 'emocao' e 'confianca' adicionadas
    """
    for tweet in tweets:
        emocao, confianca = classificar_emocao(tweet["texto_limpo"])
        tweet["emocao"] = emocao
        tweet["confianca"] = confianca

    return tweets


# Função de compatibilidade
analyzer = None  # Mantido para compatibilidade, mas não usado