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