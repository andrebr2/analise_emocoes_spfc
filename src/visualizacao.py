# /src/visualizacao.py

import os
import matplotlib.pyplot as plt
from tabulate import tabulate

# Cores das 5 emoções do TCC
CORES_EMOCOES = {
    "raiva": "#e74c3c",  # vermelho
    "alegria": "#2ecc71",  # verde
    "frustracao": "#f39c12",  # laranja
    "ironia": "#9b59b6",  # roxo
    "neutro": "#95a5a6"  # cinza
}


def gerar_grafico_barras(percentuais, pasta_resultados, identificador_jogo, titulo="Distribuição de Emoções"):
    """
    Gera e salva um gráfico de barras com a distribuição percentual das emoções.

    Args:
        percentuais (dict): Dicionário com emoções e seus percentuais
        pasta_resultados (str): Pasta onde salvar o gráfico
        identificador_jogo (str): Identificador único do jogo (data_hora)
        titulo (str): Título do gráfico
    """
    # Ordena as emoções para consistência
    emocoes = ["raiva", "alegria", "frustracao", "ironia", "neutro"]
    valores = [percentuais.get(e, 0) for e in emocoes]
    cores = [CORES_EMOCOES.get(e, "#95a5a6") for e in emocoes]

    plt.figure(figsize=(8, 6))
    plt.bar(emocoes, valores, color=cores)
    plt.ylabel("% de tweets")
    plt.title(titulo)

    # Adiciona os valores sobre as barras
    for i, v in enumerate(valores):
        plt.text(i, v + 1, f"{v:.1f}%", ha="center")

    plt.tight_layout()

    # Salva o gráfico com identificador do jogo
    caminho = os.path.join(pasta_resultados, f"grafico_emocoes_{identificador_jogo}.png")
    plt.savefig(caminho)
    plt.close()


def gerar_tabela_resumo(percentuais_etapas, pasta_resultados, identificador_jogo):
    """
    Gera e salva uma tabela resumo com os percentuais por etapa e a emoção predominante.

    Args:
        percentuais_etapas (dict): Dicionário com etapas e seus percentuais
        pasta_resultados (str): Pasta onde salvar a tabela
        identificador_jogo (str): Identificador único do jogo (data_hora)
    """
    tabela = []

    # Define a ordem das etapas
    etapas_ordenadas = ["pre_jogo", "durante_jogo", "pos_jogo"]
    nomes_etapas = {
        "pre_jogo": "Pré-jogo",
        "durante_jogo": "Durante o jogo",
        "pos_jogo": "Pós-jogo"
    }

    # Define a ordem das emoções
    emocoes_ordenadas = ["raiva", "alegria", "frustracao", "ironia", "neutro"]

    for etapa in etapas_ordenadas:
        perc = percentuais_etapas.get(etapa, {})

        # Encontra a emoção predominante (maior percentual)
        if perc:
            predominante = max(perc.items(), key=lambda x: x[1])[0]
        else:
            predominante = "-"

        # Monta a linha da tabela
        linha = [nomes_etapas.get(etapa, etapa)]
        for emocao in emocoes_ordenadas:
            linha.append(f"{perc.get(emocao, 0):.1f}%")
        linha.append(predominante)

        tabela.append(linha)

    # Headers atualizados com as 5 emoções
    headers = ["Etapa", "Raiva", "Alegria", "Frustração", "Ironia", "Neutro", "Predominante"]

    # Gera a tabela formatada
    tabela_formatada = tabulate(tabela, headers=headers, tablefmt="grid")

    # Exibe no console
    print("\n" + "=" * 60)
    print("TABELA RESUMO DAS EMOÇÕES POR ETAPA")
    print("=" * 60)
    print(tabela_formatada)
    print("=" * 60 + "\n")

    # Salva a tabela em arquivo
    caminho = os.path.join(pasta_resultados, f"tabela_resumo_{identificador_jogo}.txt")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(tabela_formatada)

    print(f"[INFO] Tabela salva em: {caminho}")