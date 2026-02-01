# /src/janelas.py

from datetime import timedelta

def calcular_janelas(hora_inicio_jogo):
    janelas = {"pre_jogo": [], "durante_jogo": [], "pos_jogo": []}

    # Pré-jogo: 1 hora antes, 4 janelas de 15 min
    for i in range(4, 0, -1):
        fim = hora_inicio_jogo - timedelta(minutes=(i - 1) * 15)
        inicio = fim - timedelta(minutes=15)
        janelas["pre_jogo"].append((inicio, fim))

    # Durante o jogo: 2 horas, 8 janelas de 15 min
    for i in range(8):
        inicio = hora_inicio_jogo + timedelta(minutes=i * 15)
        fim = inicio + timedelta(minutes=15)
        janelas["durante_jogo"].append((inicio, fim))

    # Pós-jogo: após 120 minutos (jogo + intervalo + acréscimos)
    hora_fim_jogo = hora_inicio_jogo + timedelta(minutes=120)
    for i in range(8):
        inicio = hora_fim_jogo + timedelta(minutes=i * 15)
        fim = inicio + timedelta(minutes=15)
        janelas["pos_jogo"].append((inicio, fim))

    return janelas