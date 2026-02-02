# /src/utils.py

import os
import pandas as pd


def criar_pasta_resultados(adversario, data_hora):
    """
    Cria pastas separadas para dados brutos (data) e resultados (resultados)
    """
    base_nome = f"SPFC_vs_{adversario}_{data_hora}"

    # Pasta de dados
    base_data = f"data/{base_nome}"
    exec_count = 1
    pasta_data = f"{base_data}_EXEC{exec_count}"

    while os.path.exists(pasta_data):
        exec_count += 1
        pasta_data = f"{base_data}_EXEC{exec_count}"

    os.makedirs(pasta_data)

    # Pasta de resultados (mesmo EXEC)
    pasta_resultados = f"resultados/{base_nome}_EXEC{exec_count}"
    os.makedirs(pasta_resultados)

    return pasta_data, pasta_resultados


def salvar_tweets_csv(tweets, pasta_data, etapa, janela_inicio):
    if not tweets:
        return

    filename = f"{etapa}_{janela_inicio.strftime('%Y%m%d_%H%M')}.csv"
    path = os.path.join(pasta_data, filename)

    df = pd.DataFrame(tweets)
    df.to_csv(path, index=False, encoding="utf-8")

    print(f"[INFO] Janela salva em CSV: {path}")


import json
from datetime import datetime

def salvar_tweets_json(tweets, pasta_data, nome_etapa, inicio_janela):
    # converte datetimes em strings
    tweets_serializaveis = []
    for t in tweets:
        t_copy = t.copy()
        for k in ["timestamp", "janela"]:
            if isinstance(t_copy.get(k), datetime):
                t_copy[k] = t_copy[k].isoformat()
        tweets_serializaveis.append(t_copy)

    filename = f"{nome_etapa}_{inicio_janela.strftime('%Y%m%d_%H%M')}.json"
    path = os.path.join(pasta_data, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(tweets_serializaveis, f, ensure_ascii=False, indent=4)

    print(f"[INFO] Janela salva em JSON: {path}")