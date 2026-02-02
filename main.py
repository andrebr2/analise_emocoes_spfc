# /main.py

from datetime import datetime
from src.janelas import calcular_janelas
from src.coleta import coletar_tweets
from src.utils import criar_pasta_resultados, salvar_tweets_csv, salvar_tweets_json
from src.analise_emocoes import analisar_tweets
from src.agregacao import percentual_emocoes
from src.visualizacao import gerar_grafico_barras, gerar_tabela_resumo
from src.config import PERFIL_SPFC, LIMITE_PRE_JOGO, LIMITE_DURANTE_POS

# Entrada do usuário
adversario = input("Adversário: ")
data_jogo = input("Data do jogo (DD-MM-AAAA): ")
hora_jogo = input("Hora de início (HH:MM): ")
hora_inicio_jogo = datetime.strptime(f"{data_jogo} {hora_jogo}", "%d-%m-%Y %H:%M")

# Identificador data_hora
data_hora = data_jogo.replace("-", "") + "_" + hora_jogo.replace(":", "")

# Pastas
pasta_resultados, pasta_data = criar_pasta_resultados(adversario, data_hora)

# Janelas
janelas = calcular_janelas(hora_inicio_jogo)

# Processar cada etapa
def processar_etapa(janelas_etapa, limite, nome_etapa):
    todos_tweets_etapa = []
    for janela in janelas_etapa:
        tweets_janela = coletar_tweets(janela, limite, PERFIL_SPFC)
        tweets_analisados = analisar_tweets(tweets_janela)
        salvar_tweets_csv(tweets_analisados, pasta_data, nome_etapa, janela[0])
        salvar_tweets_json(tweets_analisados, pasta_data, nome_etapa, janela[0])
        todos_tweets_etapa += tweets_analisados
    return todos_tweets_etapa

tweets_pre = processar_etapa(janelas["pre_jogo"], LIMITE_PRE_JOGO, "pre_jogo")
tweets_durante = processar_etapa(janelas["durante_jogo"], LIMITE_DURANTE_POS, "durante_jogo")
tweets_pos = processar_etapa(janelas["pos_jogo"], LIMITE_DURANTE_POS, "pos_jogo")

# Estatísticas (total e neutros)
def estatisticas_tweets(lista_tweets):
    total_tweets = len(lista_tweets)
    neutros_tweets = sum(1 for t in lista_tweets if t.get("emocao") == "neutro")
    percentual_neutros = (neutros_tweets / total_tweets) * 100 if total_tweets else 0
    return total_tweets, neutros_tweets, percentual_neutros

print("\n=== Estatísticas por etapa ===")
for nome, tweets in [
    ("Pré-jogo", tweets_pre),
    ("Durante o jogo", tweets_durante),
    ("Pós-jogo", tweets_pos)
]:
    total, neutros, perc = estatisticas_tweets(tweets)
    print(f"{nome}: {total} tweets | {neutros} neutros ({perc:.1f}%)")

# Agregação
percentuais_etapas = {
    "pre_jogo": percentual_emocoes(tweets_pre),
    "durante_jogo": percentual_emocoes(tweets_durante),
    "pos_jogo": percentual_emocoes(tweets_pos)
}

# Gráfico e tabela
todos_tweets = tweets_pre + tweets_durante + tweets_pos
percentuais_totais = percentual_emocoes(todos_tweets)

total_geral, neutros_geral, perc_neutros_geral = estatisticas_tweets(todos_tweets)
print("\n=== Estatísticas gerais ===")
print(f"Total de tweets: {total_geral}")
print(f"Tweets neutros: {neutros_geral} ({perc_neutros_geral:.1f}%)")

# Passar o identificador do jogo para gerar arquivos únicos e evitar sobrescrita
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