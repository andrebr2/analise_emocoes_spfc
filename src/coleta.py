# /src/coleta.py

import requests
from .config import API_BEARER_TOKEN
import re
import emoji
import time
from datetime import timezone

BASE_URL = "https://api.twitter.com/2/tweets/search/recent"


def limpar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"http\S+", "", texto)
    texto = re.sub(r"@\S+", "", texto)
    texto = re.sub(r"#\S+", "", texto)
    texto = emoji.demojize(texto)
    texto = texto.strip()
    return texto


def fazer_requisicao_com_retry(url, headers, params):
    """
    Faz requisição tratando erro 429 (rate limit)
    sem perder dados.
    """
    while True:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response

        if response.status_code == 429:
            reset_time = response.headers.get("x-rate-limit-reset")

            if reset_time:
                tempo_espera = int(reset_time) - int(time.time())
                tempo_espera = max(tempo_espera, 5)
            else:
                tempo_espera = 60

            print(f"[INFO] Rate limit atingido. Aguardando {tempo_espera} segundos...")
            time.sleep(tempo_espera)
            continue

        print(f"[ERRO] Requisição falhou: {response.status_code} - {response.text}")
        time.sleep(5)


def coletar_tweets(janela, perfil, id_perfil):
    """
    Coleta TODOS os tweets resposta aos tweets publicados
    pelo perfil oficial do clube dentro do intervalo informado.
    """

    inicio, fim = janela

    inicio_utc = inicio.astimezone(timezone.utc)
    fim_utc = fim.astimezone(timezone.utc)

    inicio_iso = inicio_utc.isoformat().replace("+00:00", "Z")
    fim_iso = fim_utc.isoformat().replace("+00:00", "Z")

    headers = {"Authorization": f"Bearer {API_BEARER_TOKEN}"}

    tweets_acumulados = []
    ids_unicos = set()

    # ==================================================
    # 1) BUSCAR TODOS OS TWEETS DO CLUBE NO INTERVALO
    # ==================================================
    query_clube = f"from:{perfil} lang:pt"
    next_token_clube = None
    tweets_clube = []

    while True:
        params_clube = {
            "query": query_clube,
            "start_time": inicio_iso,
            "end_time": fim_iso,
            "max_results": 100,
            "tweet.fields": "id,conversation_id,created_at"
        }

        if next_token_clube:
            params_clube["next_token"] = next_token_clube

        try:
            resp_clube = fazer_requisicao_com_retry(BASE_URL, headers, params_clube)

            json_resp = resp_clube.json()
            data = json_resp.get("data", [])
            meta = json_resp.get("meta", {})

            if not data:
                break

            tweets_clube.extend(data)

            next_token_clube = meta.get("next_token")
            if not next_token_clube:
                break

            time.sleep(1)

        except Exception as e:
            print(f"[ERRO] Exceção ao buscar tweets do clube: {e}")
            break

    # ==================================================
    # 2) BUSCAR TODAS AS RESPOSTAS PARA CADA CONVERSATION_ID
    # ==================================================
    for tweet_clube in tweets_clube:
        conversation_id = tweet_clube["conversation_id"]
        next_token = None

        while True:
            params_respostas = {
                "query": f"conversation_id:{conversation_id} lang:pt",
                "start_time": inicio_iso,
                "end_time": fim_iso,
                "max_results": 100,
                "tweet.fields": "id,text,created_at,public_metrics,in_reply_to_user_id"
            }

            if next_token:
                params_respostas["next_token"] = next_token

            try:
                response = fazer_requisicao_com_retry(BASE_URL, headers, params_respostas)

                json_resp = response.json()
                data = json_resp.get("data", [])
                meta = json_resp.get("meta", {})

                if not data:
                    break

                respostas = [
                    t for t in data
                    if t.get("in_reply_to_user_id") == id_perfil
                ]

                for t in respostas:
                    if t["id"] in ids_unicos:
                        continue

                    ids_unicos.add(t["id"])

                    tweets_acumulados.append({
                        "id_tweet": t["id"],
                        "texto": t["text"],
                        "retweets": t.get("public_metrics", {}).get("retweet_count", 0),
                        "likes": t.get("public_metrics", {}).get("like_count", 0),
                        "texto_limpo": limpar_texto(t["text"]),
                        "timestamp": t["created_at"],
                        "janela": inicio
                    })

                next_token = meta.get("next_token")
                if not next_token:
                    break

                time.sleep(1)

            except Exception as e:
                print(f"[ERRO] Falha na coleta de respostas: {e}")
                break

    print(f"[INFO] Total coletado no intervalo: {len(tweets_acumulados)} tweets")
    return tweets_acumulados