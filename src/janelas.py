# /src/janelas.py

from datetime import timedelta

def calcular_janelas(hora_inicio_jogo):
    """
    Calcula janelas de coleta de tweets para pré-jogo, durante o jogo e pós-jogo.

    Pré-jogo: 1 hora antes do início do jogo (4 janelas de 15 min)
    Durante o jogo: 120 minutos a partir do início (8 janelas de 15 min)
    Pós-jogo: 120 minutos após o término estimado (8 janelas de 15 min)

    Retorna:
        dict: {"pre_jogo": [...], "durante_jogo": [...], "pos_jogo": [...]}
              Cada item é uma tupla (inicio, fim) em datetime
    """

    janelas = {
        "pre_jogo": [],
        "durante_jogo": [],
        "pos_jogo": []
    }

    intervalo = timedelta(minutes=15)

    # =========================
    # PRÉ-JOGO (1h antes)
    # =========================
    inicio_pre = hora_inicio_jogo - timedelta(hours=1)

    for i in range(4):
        inicio = inicio_pre + i * intervalo
        fim = inicio + intervalo
        janelas["pre_jogo"].append((inicio, fim))

    # =========================
    # DURANTE O JOGO (0 → 120 min)
    # =========================
    for i in range(8):
        inicio = hora_inicio_jogo + i * intervalo
        fim = inicio + intervalo
        janelas["durante_jogo"].append((inicio, fim))

    # =========================
    # PÓS-JOGO (120 → 240 min)
    # =========================
    inicio_pos = hora_inicio_jogo + timedelta(hours=2)

    for i in range(8):
        inicio = inicio_pos + i * intervalo
        fim = inicio + intervalo
        janelas["pos_jogo"].append((inicio, fim))

    return janelas