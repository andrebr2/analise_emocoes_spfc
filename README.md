# Análise de Emoções dos Torcedores do SPFC no X

## Descrição do Projeto

Este projeto realiza uma **análise de emoções em tweets de torcedores do São Paulo Futebol Clube (SPFC)** coletados na plataforma X (antigo Twitter).  
O objetivo é avaliar o **sentimento da torcida** antes, durante e após os jogos, gerando gráficos de distribuição de emoções e uma tabela resumo das emoções predominantes em cada etapa.

O protótipo coleta tweets:
- Que interagem com o perfil oficial do SPFC (`@SaoPauloFC`)  
- Em janelas de tempo definidas:
  - **Pré-jogo:** 1 hora antes, 4 janelas de 15 minutos  
  - **Durante o jogo:** 2 horas, 8 janelas de 15 minutos  
  - **Pós-jogo:** 2 horas, 8 janelas de 15 minutos  
- Limite de tweets por janela:
  - Pré-jogo: 75 tweets  
  - Durante e pós-jogo: 100 tweets  

A classificação de emoções é feita usando o modelo **multilingual_go_emotions_V1.2**, mapeado para 5 categorias relevantes para o TCC:
- Alegria
- Raiva
- Tristeza
- Surpresa
- Medo

---

## Estrutura do Projeto

analise_emocoes/                  # Raiz do projeto  
│  
├── main.py                        # Script principal para rodar todo o fluxo  
├── .env                           # Variáveis de ambiente (ex.: token da API do X)  
├── requirements.txt               # Dependências do projeto  
├── README.md                       # Documentação do projeto  
│  
├── data/                           # Pasta para armazenar dados brutos coletados  
│   └── SPFC_vs_<adversario>_<data_hora>/  
│       ├── pre_jogo_YYYYMMDD_HHMM.csv  
│       ├── pre_jogo_YYYYMMDD_HHMM.json  
│       ├── durante_jogo_YYYYMMDD_HHMM.csv  
│       ├── durante_jogo_YYYYMMDD_HHMM.json  
│       ├── pos_jogo_YYYYMMDD_HHMM.csv  
│       └── pos_jogo_YYYYMMDD_HHMM.json  
│
├── resultados/                     # Pasta opcional para análises ou gráficos finais  
│   └── SPFC_vs_<adversario>_<data_hora>/  
│       ├── grafico_emocoes.png  
│       └── tabela_resumo.txt  
│  
├── src/                            # Código-fonte  
│   ├── __init__.py                 # Torna src um pacote Python  
│   ├── config.py                   # Carrega o token do .env e outras configurações  
│   ├── coleta.py                   # Funções de coleta de tweets  
│   ├── janelas.py                  # Funções para calcular janelas pré/durante/pós-jogo  
│   ├── analise_emocoes.py          # Funções de classificação de emoções  
│   ├── agregacao.py                # Funções de agregação e cálculo de percentuais  
│   ├── visualizacao.py             # Funções para gráficos e tabelas resumo  
│   └── utils.py                    # Funções utilitárias para salvar arquivos, criar pastas, etc.  
│  
└── .gitignore                       # Ignora .venv, .env, __pycache__, data/, resultados/, etc.  
  

---

## Requisitos

- Python 3.10 ou superior
- Virtual environment (venv) recomendado
- Dependências listadas em `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Pacotes principais:

- transformers

- torch

- pandas

- matplotlib

- tabulate

- requests  

---

## Configuração

Insira seu Bearer Token da API X no arquivo .env:

```
AX_API_TOKEN= = "SEU_TOKEN_AQUI"
```

Ajuste limites de tweets e duração das janelas se desejar no arquivo config.py:

```
LIMITE_PRE_JOGO = 75
LIMITE_DURANTE_POS = 100
DURACAO_JANELA = 15  # em minutos
```

---

## Execução

Ative o ambiente virtual:
```
source .venv/bin/activate
```

Rode o script principal:
```
python main.py
```

Você será solicitado a inserir:

Nome do adversário

Data do jogo (DD-MM-AAAA)

Hora do jogo (HH:MM)

O programa criará automaticamente uma pasta em resultados/ para armazenar todos os arquivos CSV e JSON das janelas de coleta, sem sobrescrever resultados antigos.  

---


## Resultados

1. Arquivos CSV e JSON  
Cada janela de coleta gera arquivos separados contendo:

- **id**: identificador único do tweet  
- **texto**: conteúdo textual do tweet 
- **texto_limpo**: versão processada do texto para remover elementos que não ajudam na análise de emoções 
- **timestamp**: data e hora de publicação do tweet  
- **retweets**: número de retweets  
- **likes**: número de curtidas  
- **emocao**: emoção predominante detectada pelo modelo  
- **confianca**: grau de confiança da classificação da emoção  

2. Gráfico de barras

Mostra a distribuição percentual de cada emoção em toda a janela de coleta (pré + durante + pós-jogo).

3. Tabela resumo  

Mostra a emoção predominante em cada etapa do jogo (pré, durante e pós).  

---

## Observações

- Tweets coletados incluem respostas ou menções ao perfil oficial do SPFC e tweets que utilizam hashtags relevantes relacionadas ao clube, como:
#SPFC, #SãoPauloFC, #VamosSãoPaulo, #Tricolores, #saopaulofc, #spfc, #tricolores.

- A query de coleta pode ser ajustada em coleta.py caso queira adicionar ou remover hashtags.

- A coleta de tweets diretamente do perfil oficial também é contemplada através de menções (to:@SaoPauloFC).

---

## Licença

Projeto desenvolvido para fins acadêmicos (TCC).