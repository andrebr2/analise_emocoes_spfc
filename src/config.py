# /src/config.py

from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

# Token da API do X
API_BEARER_TOKEN = os.getenv("X_API_TOKEN")
if API_BEARER_TOKEN is None:
    raise RuntimeError("X_API_TOKEN não encontrado no arquivo .env")

# Perfil do clube
PERFIL_SPFC = "SaoPauloFC"

# Limite de tweets por janela
LIMITE_PRE_JOGO = 75
LIMITE_DURANTE_POS = 100

# Categorias do TCC
EMOCOES = ["alegria", "raiva", "tristeza", "surpresa", "medo"]

# Duração das janelas em minutos
DURACAO_JANELA = 15

# Hashtags associada ao clube
HASHTAGS_SPFC = [
    "#SPFC",
    "#SãoPauloFC",
    "#VamosSãoPaulo",
    "#Tricolores",
    "#saopaulofc",
    "#spfc",
    "#tricolores"
]
