# /src/visualizacao.py

import os
import matplotlib.pyplot as plt
from tabulate import tabulate

CORES_EMOCOES = {
    "alegria": "#2ecc71",    # verde
    "raiva": "#e74c3c",      # vermelho
    "tristeza": "#3498db",   # azul
    "surpresa": "#f1c40f",   # amarelo
    "medo": "#9b59b6"        # roxo
}

def gerar_grafico_barras(percentuais, pasta_resultados, identificador_jogo, titulo="Distribuição de Emoções"):
    emocoes = list(percentuais.keys())
    valores = list(percentuais.values())
    cores = [CORES_EMOCOES.get(e, "#95a5a6") for e in emocoes]

    plt.figure(figsize=(8, 6))
    plt.bar(emocoes, valores, color=cores)
    plt.ylabel("% de tweets")
    plt.title(titulo)

    for i, v in enumerate(valores):
        plt.text(i, v + 1, f"{v:.1f}%", ha="center")

    plt.tight_layout()

    # Salva o gráfico com identificador do jogo para evitar sobrescrita
    caminho = os.path.join(pasta_resultados, f"grafico_emocoes_{identificador_jogo}.png")
    plt.savefig(caminho)
    plt.close()  # Não abre janela, fecha a figura

def gerar_tabela_resumo(percentuais_etapas, pasta_resultados, identificador_jogo):
    tabela = []
    for etapa, perc in percentuais_etapas.items():
        pred = max(perc, key=perc.get) if perc else None
        linha = [etapa]
        for emo in ["alegria", "raiva", "tristeza", "surpresa", "medo"]:
            linha.append(f"{perc.get(emo, 0):.1f}%")
        linha.append(pred)
        tabela.append(linha)

    headers = ["Etapa", "Alegria", "Raiva", "Tristeza", "Surpresa", "Medo", "Predominante"]
    tabela_formatada = tabulate(tabela, headers=headers, tablefmt="grid")

    print(tabela_formatada)

    # Salva a tabela com identificador do jogo para evitar sobrescrita
    caminho = os.path.join(pasta_resultados, f"tabela_resumo_{identificador_jogo}.txt")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(tabela_formatada)