# /src/coleta.py

import requests
from src.config import API_BEARER_TOKEN

BASE_URL = "https://api.twitter.com/2/tweets/search/recent"

def coletar_tweets(janela, limite, perfil):
    inicio, fim = janela
    inicio_iso = inicio.isoformat("T") + "Z"
    fim_iso = fim.isoformat("T") + "Z"

    headers = {"Authorization": f"Bearer {API_BEARER_TOKEN}"}
    query = f"to:{perfil}"

    params = {
        "query": query,
        "start_time": inicio_iso,
        "end_time": fim_iso,
        "max_results": limite,
        "tweet.fields": "id,text,created_at,public_metrics"
    }

    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code != 200:
            print(f"[ERRO] API retornou {response.status_code}: {response.text}")
            return []

        data = response.json().get("data", [])
        tweets = [
            {
                "id_tweet": t["id"],
                "texto": t["text"],
                "retweets": t.get("public_metrics", {}).get("retweet_count", 0),
                "likes": t.get("public_metrics", {}).get("like_count", 0),
                "timestamp": t["created_at"],
                "janela": inicio
            }
            for t in data
        ]
        return tweets

    except Exception as e:
        print(f"[ERRO] Falha na coleta: {e}")
        return []