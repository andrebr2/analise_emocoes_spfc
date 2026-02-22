# /main.py

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil import parser
from src.janelas import calcular_janelas
from src.coleta import coletar_tweets
from src.utils import criar_pasta_resultados, salvar_tweets_csv
from src.analise_emocoes import analisar_tweets
from src.agregacao import percentual_emocoes
from src.visualizacao import gerar_grafico_barras, gerar_tabela_resumo
from src.config import PERFIL_SPFC, MODELO_PATH, API_BEARER_TOKEN
import os
import requests


# ==================================================
# VERIFICAÇÃO DO MODELO
# ==================================================
def verificar_modelo():
    modelo_dir = os.path.join(MODELO_PATH, "final")
    if not os.path.exists(modelo_dir):
        print("\n" + "=" * 60)
        print("ERRO: Modelo fine-tuning não encontrado!")
        print("=" * 60)
        print(f"Pasta esperada: {modelo_dir}")
        print("\nExecute o fine-tuning primeiro:")
        print("  python -m src.fine_tuning")
        print("=" * 60)
        return False
    return True


# ==================================================
# OBTER ID DO USUÁRIO OFICIAL
# ==================================================
def obter_id_usuario(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {"Authorization": f"Bearer {API_BEARER_TOKEN}"}
    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        raise RuntimeError(f"Não foi possível obter ID do usuário {username}: {resp.text}")

    data = resp.json().get("data", {})
    user_id = data.get("id")

    if not user_id:
        raise RuntimeError("ID do usuário não encontrado na resposta da API.")

    print(f"[INFO] ID do perfil @{username}: {user_id}")
    return user_id


# ==================================================
# INÍCIO DO PIPELINE
# ==================================================
if not verificar_modelo():
    exit(1)

# Entrada do usuário
adversario = input("Adversário: ")
data_jogo = input("Data do jogo (DD-MM-AAAA): ")
hora_jogo = input("Hora de início (HH:MM): ")

timezone_br = ZoneInfo("America/Sao_Paulo")

hora_inicio_jogo = datetime.strptime(
    f"{data_jogo} {hora_jogo}",
    "%d-%m-%Y %H:%M"
).replace(tzinfo=timezone_br)

data_hora = data_jogo.replace("-", "") + "_" + hora_jogo.replace(":", "")

pasta_data, pasta_resultados = criar_pasta_resultados(adversario, data_hora)

janelas = calcular_janelas(hora_inicio_jogo)

print("\n[INFO] Janelas calculadas:")
for etapa, lista_janelas in janelas.items():
    print(f"\n{etapa.upper()}")
    for inicio_j, fim_j in lista_janelas:
        print(f"{inicio_j.strftime('%H:%M')} → {fim_j.strftime('%H:%M')}")

id_spfc = obter_id_usuario(PERFIL_SPFC)


# ==================================================
# COLETA CONTÍNUA
# ==================================================
inicio_coleta = hora_inicio_jogo - timedelta(hours=1)
fim_coleta = hora_inicio_jogo + timedelta(hours=4)

print("\n[INFO] Coleta contínua:")
print(f"{inicio_coleta.strftime('%H:%M')} → {fim_coleta.strftime('%H:%M')}")

tweets_coletados = coletar_tweets(
    janela=(inicio_coleta, fim_coleta),
    perfil=PERFIL_SPFC,
    id_perfil=id_spfc
)

print(f"[INFO] Total bruto coletado: {len(tweets_coletados)} tweets")

tweets_coletados = analisar_tweets(tweets_coletados)


# ==================================================
# DISTRIBUIR NAS JANELAS (CORRIGIDO)
# ==================================================
def filtrar_por_janela(lista_tweets, intervalo):
    inicio_intervalo, fim_intervalo = intervalo
    filtrados = []

    for tweet in lista_tweets:
        # Parse timestamp (UTC vindo da API)
        timestamp_utc = parser.isoparse(tweet["timestamp"])

        # Converter para horário do Brasil
        timestamp_br = timestamp_utc.astimezone(timezone_br)

        if inicio_intervalo <= timestamp_br < fim_intervalo:
            filtrados.append(tweet)

    return filtrados


tweets_pre = []
tweets_durante = []
tweets_pos = []

for intervalo in janelas["pre_jogo"]:
    tweets_j = filtrar_por_janela(tweets_coletados, intervalo)
    salvar_tweets_csv(tweets_j, pasta_data, "pre_jogo", intervalo[0])
    tweets_pre += tweets_j

for intervalo in janelas["durante_jogo"]:
    tweets_j = filtrar_por_janela(tweets_coletados, intervalo)
    salvar_tweets_csv(tweets_j, pasta_data, "durante_jogo", intervalo[0])
    tweets_durante += tweets_j

for intervalo in janelas["pos_jogo"]:
    tweets_j = filtrar_por_janela(tweets_coletados, intervalo)
    salvar_tweets_csv(tweets_j, pasta_data, "pos_jogo", intervalo[0])
    tweets_pos += tweets_j


# ==================================================
# ESTATÍSTICAS
# ==================================================
def estatisticas_tweets(lista_tweets):
    total_tweets = len(lista_tweets)
    neutros_tweets = sum(1 for t in lista_tweets if t.get("emocao") == "neutro")
    percentual_neutros = (neutros_tweets / total_tweets) * 100 if total_tweets else 0
    return total_tweets, neutros_tweets, percentual_neutros


print("\n=== Estatísticas por etapa ===")
for nome, lista in [
    ("Pré-jogo", tweets_pre),
    ("Durante o jogo", tweets_durante),
    ("Pós-jogo", tweets_pos)
]:
    total, neutros, perc = estatisticas_tweets(lista)
    print(f"{nome}: {total} tweets | {neutros} neutros ({perc:.1f}%)")


# ==================================================
# AGREGAÇÃO
# ==================================================
percentuais_etapas = {
    "pre_jogo": percentual_emocoes(tweets_pre),
    "durante_jogo": percentual_emocoes(tweets_durante),
    "pos_jogo": percentual_emocoes(tweets_pos)
}

todos_tweets = tweets_pre + tweets_durante + tweets_pos
percentuais_totais = percentual_emocoes(todos_tweets)

total_geral, neutros_geral, perc_neutros_geral = estatisticas_tweets(todos_tweets)

print("\n=== Estatísticas gerais ===")
print(f"Total de tweets: {total_geral}")
print(f"Tweets neutros: {neutros_geral} ({perc_neutros_geral:.1f}%)")


# ==================================================
# VISUALIZAÇÃO
# ==================================================
gerar_grafico_barras(
    percentuais_totais,
    pasta_resultados,
    identificador_jogo=data_hora,
    titulo="Distribuição de Emoções dos Torcedores"
)

gerar_tabela_resumo(
    percentuais_etapas,
    pasta_resultados,
    identificador_jogo=data_hora
)