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

A classificação de emoções é feita usando o modelo **BERTimbau (neuralmind/bert-base-portuguese-cased)** fine-tuning com um dataset manual de 1.412 tweets rotulados.

As 5 categorias de emoção analisadas são:
- Raiva
- Alegria
- Frustração
- Ironia
- Neutro

---

## Estrutura do Projeto

analise_emocoes/                  # Raiz do projeto  
│  
├── main.py                        # Script principal para rodar todo o fluxo  
├── .env                           # Variáveis de ambiente (ex.: token da API do X)  
├── requirements.txt               # Dependências do projeto  
├── README.md                      # Documentação do projeto  
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
├── modelo_torcedor_spfc/          # Modelo BERTimbau fine-tuning (criado após treinamento)
│   └── final/                      # Versão final do modelo
│       ├── config.json
│       ├── model.safetensors
│       └── tokenizer_config.json
│
├── resultados/                     # Pasta para gráficos e tabelas finais  
│   └── SPFC_vs_<adversario>_<data_hora>/  
│       ├── grafico_emocoes.png  
│       └── tabela_resumo.txt  
│  
├── src/                            # Código-fonte  
│   ├── __init__.py                 # Torna src um pacote Python  
│   ├── config.py                   # Carrega o token do .env e outras configurações  
│   ├── coleta.py                   # Funções de coleta de tweets  
│   ├── janelas.py                  # Funções para calcular janelas pré/durante/pós-jogo  
│   ├── fine_tuning.py              # Script para treinar o BERTimbau (NOVO)
│   ├── analise_emocoes.py          # Funções de classificação de emoções  
│   ├── agregacao.py                # Funções de agregação e cálculo de percentuais  
│   ├── visualizacao.py             # Funções para gráficos e tabelas resumo  
│   └── utils.py                    # Funções utilitárias para salvar arquivos, criar pastas, etc.  
│  
└── .gitignore                      # Ignora .venv, .env, __pycache__, data/, resultados/, etc.
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
- scikit-learn
- datasets
- accelerate
- evaluate
- python-dotenv
- emoji

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

## Fine-tuning do Modelo

Antes da primeira execução, é necessário fazer o fine-tuning no BERTimbau com o dataset manual de tweets:  
```
python -m src.fine_tuning
```

O script:

- Carrega o arquivo data/texto_bruto.csv com os 1.412 tweets rotulados

- Divide os dados em treino (70%), validação (15%) e teste (15%)

- Treina o modelo por 5 épocas

- Salva o modelo em modelo_torcedor_spfc/final/

- Gera métricas e matriz de confusão em modelo_torcedor_spfc/

- Após o fine-tuning, o modelo estará pronto para ser usado na classificação.

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

- O modelo fine-tuning não é incluído no repositório devido ao tamanho. Após o fine-tuning, ele será gerado localmente.

---

## Licença

Projeto desenvolvido para fins acadêmicos (TCC).