# /src/fine_tuning.py

"""
Módulo para fine-tuning do BERTimbau com os dados manuais de tweets.
Realiza o treinamento do modelo para classificação das 5 emoções:
raiva, alegria, frustracao, ironia, neutro.
"""

import pandas as pd
import torch
import numpy as np
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import os
import json
from .config import (
    MODELO_NOME,
    MODELO_PATH,
    MAX_LEN,
    BATCH_SIZE,
    EPOCHS,
    LEARNING_RATE,
    WARMUP_RATIO,
    WEIGHT_DECAY,
    TEST_SIZE,
    VAL_SIZE,
    RANDOM_SEED,
    EMOCAO_TO_ID,
    ID_TO_EMOCAO,
    EMOCOES
)


class TweetsDataset(Dataset):
    """
    Dataset personalizado para os tweets.
    Converte textos e labels para o formato esperado pelo transformers.
    """

    def __init__(self, textos, labels, tokenizer, max_len):
        self.textos = textos
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.textos)

    def __getitem__(self, idx):
        texto = str(self.textos[idx])
        label = self.labels[idx]

        # Tokeniza o texto
        encoding = self.tokenizer(
            texto,
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(label, dtype=torch.long)
        }


def compute_metrics(eval_pred):
    """
    Calcula as métricas de avaliação: acurácia e F1-score (macro e weighted).
    """
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)

    # Calcula métricas
    acc = accuracy_score(labels, predictions)
    f1_macro = f1_score(labels, predictions, average="macro")
    f1_weighted = f1_score(labels, predictions, average="weighted")

    return {
        "accuracy": acc,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted
    }


def preparar_dados(csv_path):
    """
    Carrega o CSV com os tweets manuais e prepara para o fine-tuning.

    Args:
        csv_path (str): Caminho para o arquivo CSV com os tweets rotulados

    Returns:
        tuple: (textos, labels) onde labels são os IDs das emoções
    """
    print(f"[INFO] Carregando dados de: {csv_path}")
    df = pd.read_csv(csv_path)

    # Verifica se as colunas necessárias existem
    if "texto_bruto" not in df.columns:
        raise ValueError("CSV não contém coluna 'texto_bruto'")
    if "label" not in df.columns:
        raise ValueError("CSV não contém coluna 'label'")

    # Remove linhas com valores nulos
    df = df.dropna(subset=["texto_bruto", "label"])

    # Converte labels para IDs
    df["label_id"] = df["label"].map(EMOCAO_TO_ID)

    # Remove labels que não estão no mapeamento
    df = df.dropna(subset=["label_id"])

    # Converte label_id para inteiro
    df["label_id"] = df["label_id"].astype(int)

    textos = df["texto_bruto"].tolist()
    labels = df["label_id"].tolist()

    print(f"[INFO] Total de exemplos carregados: {len(textos)}")
    print(f"[INFO] Distribuição das labels:")
    for emocao, idx in EMOCAO_TO_ID.items():
        count = sum(1 for l in labels if l == idx)
        print(f"       {emocao}: {count}")

    return textos, labels


def treinar_modelo(
        csv_path,
        output_dir=MODELO_PATH,
        test_size=TEST_SIZE,
        val_size=VAL_SIZE,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        learning_rate=LEARNING_RATE,
        warmup_ratio=WARMUP_RATIO,
        weight_decay=WEIGHT_DECAY,
        max_len=MAX_LEN,
        seed=RANDOM_SEED
):
    """
    Função principal para fine-tuning do BERTimbau.

    Args:
        csv_path (str): Caminho para o CSV com os tweets rotulados
        output_dir (str): Diretório onde salvar o modelo treinado
        test_size (float): Proporção dos dados para teste
        val_size (float): Proporção dos dados para validação
        batch_size (int): Tamanho do batch para treinamento
        epochs (int): Número de épocas
        learning_rate (float): Taxa de aprendizado
        warmup_ratio (float): Proporção de warmup steps
        weight_decay (float): Weight decay para regularização
        max_len (int): Tamanho máximo dos tweets
        seed (int): Seed para reprodutibilidade

    Returns:
        tuple: (trainer, test_dataset, test_results)
    """

    print("\n" + "=" * 50)
    print("INICIANDO FINE-TUNING DO BERTIMBAU")
    print("=" * 50)

    # 1. Carregar dados
    textos, labels = preparar_dados(csv_path)

    # 2. Dividir dados (treino, validação, teste)
    print("\n[INFO] Dividindo dados...")

    # Primeiro separa treino + validação do teste
    X_temp, X_test, y_temp, y_test = train_test_split(
        textos,
        labels,
        test_size=test_size,
        random_state=seed,
        stratify=labels
    )

    # Depois separa treino da validação
    # Ajusta val_size para ser proporcional ao conjunto temporário
    val_relative = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp,
        y_temp,
        test_size=val_relative,
        random_state=seed,
        stratify=y_temp
    )

    print(f"   Treino: {len(X_train)} exemplos")
    print(f"   Validação: {len(X_val)} exemplos")
    print(f"   Teste: {len(X_test)} exemplos")

    # 3. Carregar tokenizer e modelo BERTimbau
    print("\n[INFO] Carregando BERTimbau...")
    tokenizer = AutoTokenizer.from_pretrained(MODELO_NOME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODELO_NOME,
        num_labels=len(EMOCOES),
        id2label=ID_TO_EMOCAO,
        label2id=EMOCAO_TO_ID
    )

    # 4. Criar datasets
    train_dataset = TweetsDataset(X_train, y_train, tokenizer, max_len)
    val_dataset = TweetsDataset(X_val, y_val, tokenizer, max_len)
    test_dataset = TweetsDataset(X_test, y_test, tokenizer, max_len)

    # 5. Configurar argumentos de treinamento
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        warmup_ratio=warmup_ratio,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        logging_dir="./logs",
        logging_steps=50,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        save_total_limit=2,
        remove_unused_columns=False,
        seed=seed,
        report_to="none"  # Desativa relatórios para wandb/tensorboard
    )

    # 6. Criar trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )

    # 7. Treinar
    print("\n[INFO] Iniciando treinamento...")
    trainer.train()

    # 8. Avaliar no conjunto de teste
    print("\n[INFO] Avaliando no conjunto de teste...")
    test_results = trainer.evaluate(test_dataset)

    print("\nRESULTADOS NO TESTE:")
    for metrica, valor in test_results.items():
        print(f"   {metrica}: {valor:.4f}")

    # 9. Salvar modelo final
    final_model_path = os.path.join(output_dir, "final")
    print(f"\n[INFO] Salvando modelo em: {final_model_path}")
    trainer.save_model(final_model_path)
    tokenizer.save_pretrained(final_model_path)

    # 10. Salvar métricas em arquivo
    metrics_path = os.path.join(output_dir, "metricas_teste.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=4, ensure_ascii=False)
    print(f"[INFO] Métricas salvas em: {metrics_path}")

    # 11. Gerar predições para análise adicional
    print("\n[INFO] Gerando predições para o conjunto de teste...")
    predictions = trainer.predict(test_dataset)
    y_pred = np.argmax(predictions.predictions, axis=1)
    y_true = test_dataset.labels

    # 12. Matriz de confusão (salva em arquivo)
    cm = confusion_matrix(y_true, y_pred)
    cm_path = os.path.join(output_dir, "matriz_confusao.txt")
    with open(cm_path, "w", encoding="utf-8") as f:
        f.write("Matriz de Confusão:\n")
        f.write(str(cm))
        f.write("\n\n")
        f.write("Labels: " + str(list(ID_TO_EMOCAO.values())))
    print(f"[INFO] Matriz de confusão salva em: {cm_path}")

    print("\n" + "=" * 50)
    print("FINE-TUNING CONCLUÍDO COM SUCESSO!")
    print("=" * 50)

    return trainer, test_dataset, test_results


def carregar_modelo_treinado(model_path=None):
    """
    Carrega um modelo fine-tunado salvo.

    Args:
        model_path (str): Caminho para o modelo salvo.
                         Se None, usa o caminho padrão + "/final"

    Returns:
        tuple: (tokenizer, model)
    """
    if model_path is None:
        model_path = os.path.join(MODELO_PATH, "final")

    print(f"[INFO] Carregando modelo de: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    return tokenizer, model


if __name__ == "__main__":
    """
    Exemplo de uso direto (para testes).
    """
    # Caminho para CSV com os 1412 tweets
    ARQUIVO_CSV = "data/texto_bruto.csv"

    if not os.path.exists(ARQUIVO_CSV):
        print(f"[ERRO] Arquivo não encontrado: {ARQUIVO_CSV}")
        print("Por favor, ajuste o caminho para seu CSV com os tweets rotulados.")
    else:
        # Executa fine-tuning
        treinar_modelo(
            csv_path=ARQUIVO_CSV,
            output_dir=MODELO_PATH,
            epochs=5
        )