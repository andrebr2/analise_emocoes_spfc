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

# Categorias do TCC (ATUALIZADO)
EMOCOES = ["raiva", "alegria", "frustracao", "ironia", "neutro"]

# Duração das janelas em minutos
DURACAO_JANELA = 15

# Hashtags associada ao clube
HASHTAGS_SPFC = [
    "#SPFC",
    "#spfc",
    "#SãoPauloFC",
    "#SãoPauloFutebolClube",
    "#saopaulofc",
    "#VamosSãoPaulo",
    "#TricolorDoMorumbi",
    "#TricolorPaulista",
    "#DiaDeTricolor",
    "#MadeInCotia"
]

# ==================================================
# CONFIGURAÇÕES PARA O BERTimbau
# ==================================================

# Mapeamento das emoções para índices (usado no fine-tuning)
EMOCAO_TO_ID = {
    "raiva": 0,
    "alegria": 1,
    "frustracao": 2,
    "ironia": 3,
    "neutro": 4
}

# Mapeamento reverso (ID para emoção)
ID_TO_EMOCAO = {v: k for k, v in EMOCAO_TO_ID.items()}

# Cores para os gráficos (uma para cada emoção)
CORES_EMOCOES = {
    "raiva": "#e74c3c",      # vermelho
    "alegria": "#2ecc71",     # verde
    "frustracao": "#f39c12",  # laranja
    "ironia": "#9b59b6",      # roxo
    "neutro": "#95a5a6"       # cinza
}

# Modelo BERTimbau
MODELO_NOME = "neuralmind/bert-base-portuguese-cased"
MODELO_PATH = "./modelo_torcedor_spfc"

# Hiperparâmetros para fine-tuning
MAX_LEN = 128          # tamanho máximo dos tweets após tokenização
BATCH_SIZE = 16        # tamanho do batch para treinamento
EPOCHS = 5             # número de épocas de treinamento
LEARNING_RATE = 2e-5   # taxa de aprendizado
WARMUP_RATIO = 0.1     # proporção de warmup steps
WEIGHT_DECAY = 0.01    # decay de peso para regularização

# Divisão dos dados
TEST_SIZE = 0.15       # 15% dos dados para teste
VAL_SIZE = 0.15        # 15% dos dados para validação

# Seed para reprodutibilidade
RANDOM_SEED = 42