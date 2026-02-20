# /src/coleta.py

import requests
from .config import API_BEARER_TOKEN, HASHTAGS_SPFC
import re
import emoji
import time

BASE_URL = "https://api.twitter.com/2/tweets/search/recent"


def limpar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"http\S+", "", texto)  # remove URLs
    texto = re.sub(r"@\S+", "", texto)  # remove menções
    texto = re.sub(r"#\S+", "", texto)  # remove hashtags
    texto = emoji.demojize(texto)  # emojis para palavras
    texto = texto.strip()
    return texto


def coletar_tweets(janela, limite, perfil):
    inicio, fim = janela
    inicio_iso = inicio.isoformat("T") + "Z"
    fim_iso = fim.isoformat("T") + "Z"

    headers = {"Authorization": f"Bearer {API_BEARER_TOKEN}"}

    # Query combinando respostas ao perfil oficial + hashtags
    hashtags_query = " OR ".join(HASHTAGS_SPFC)
    query = f"(to:{perfil} OR {hashtags_query}) lang:pt"

    tweets_acumulados = []
    next_token = None

    while True:
        # Calcula quantos tweets ainda faltam
        falta = limite - len(tweets_acumulados)

        # Define quantos tweets pegar neste request:
        # - Mínimo 10 (exigência da API)
        # - Máximo 100 (limite da API)
        # - Se faltar menos que 10, pede 10 mesmo assim
        if falta < 10:
            max_results_este_request = 10
        else:
            max_results_este_request = min(100, falta)

        params = {
            "query": query,
            "start_time": inicio_iso,
            "end_time": fim_iso,
            "max_results": max_results_este_request,
            "tweet.fields": "id,text,created_at,public_metrics"
        }

        # Adiciona next_token se existir (para paginação)
        if next_token:
            params["next_token"] = next_token

        try:
            response = requests.get(BASE_URL, headers=headers, params=params)
            if response.status_code != 200:
                print(f"[ERRO] API retornou {response.status_code}: {response.text}")
                break

            data = response.json().get("data", [])
            meta = response.json().get("meta", {})

            # Se não veio nenhum tweet, encerra
            if len(data) == 0:
                break

            # Processa os tweets desta página
            tweets_pagina = [
                {
                    "id_tweet": t["id"],
                    "texto": t["text"],
                    "retweets": t.get("public_metrics", {}).get("retweet_count", 0),
                    "likes": t.get("public_metrics", {}).get("like_count", 0),
                    "texto_limpo": limpar_texto(t["text"]),
                    "timestamp": t["created_at"],
                    "janela": inicio
                }
                for t in data
            ]

            tweets_acumulados.extend(tweets_pagina)

            # Verifica se há mais páginas e se não atingiu o limite
            next_token = meta.get("next_token")
            if not next_token or len(tweets_acumulados) >= limite:
                break

            # Pequena pausa entre requests para evitar rate limiting
            time.sleep(1)

        except Exception as e:
            print(f"[ERRO] Falha na coleta: {e}")
            break

    return tweets_acumulados