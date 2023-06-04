import os
import pandas as pd
from dataclasses import dataclass, field
from datasets import Dataset, load_dataset
from typing import Dict, List, Optional
import wandb

from transformers import (
    T5TokenizerFast,
    T5ForConditionalGeneration,
    TrainingArguments,
    Trainer,
    DataCollator,
    EarlyStoppingCallback,
    DataCollatorWithPadding
)

import torch
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dataset", type=str, required=True)
parser.add_argument("--model_dir", type=str, required=True)
args = parser.parse_args()


def add_eos_to_examples(example):
    example["input_text"] = "lore: %s question: %s </s>" % (example["lore"], example["question"])
    example["target_text"] = "%s </s>" % example["target_text"]
    return example


tokenizer = T5TokenizerFast.from_pretrained("t5-base")
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

def convert_to_features(example_batch):
    input_encodings = tokenizer.batch_encode_plus(example_batch["input_text"], pad_to_max_length=True, max_length=512)
    target_encodings = tokenizer.batch_encode_plus(example_batch["target_text"], pad_to_max_length=True, max_length=16)

    encodings = {
        "input_ids": input_encodings["input_ids"], 
        "attention_mask": input_encodings["attention_mask"],
        "target_ids": target_encodings["input_ids"],
        "target_attention_mask": target_encodings["attention_mask"]
    }

    return encodings


def compute_metrics(pred):
    """
    Helper function to compute aggregated metrics from predictions.
    """
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="weighted"
    )
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}


def load_data(path):
    raw_dataset_df = pd.read_csv(path)
    raw_dataset = Dataset.from_pandas(raw_dataset_df)
    train_valid = raw_dataset.train_test_split(test_size=0.07)

    train_dataset = train_valid["train"]
    valid_dataset = train_valid["test"]

    train_dataset = train_dataset.map(add_eos_to_examples)
    train_dataset = train_dataset.map(convert_to_features, batched=True)

    valid_dataset = valid_dataset.map(add_eos_to_examples, load_from_cache_file=False)
    valid_dataset = valid_dataset.map(convert_to_features, batched=True, load_from_cache_file=False)

    columns = ["input_ids", "target_ids", "attention_mask", "target_attention_mask"]
    train_dataset.set_format(type="torch", columns=columns)
    valid_dataset.set_format(type="torch", columns=columns)

    torch.save(train_dataset, "train_data.pt")
    torch.save(valid_dataset, "valid_data.pt")

    return (train_dataset, valid_dataset)


model = T5ForConditionalGeneration.from_pretrained("t5-base")

train_dataset, valid_dataset = load_data(os.path.join("/app/datasets", args.dataset, "dataset.csv"))

wandb.init(project="T5-testcase")
training_args = TrainingArguments(
    evaluation_strategy = "epoch",
    output_dir=os.path.join("./models/",args.model_dir),
    overwrite_output_dir=True,
    logging_strategy='steps',
    logging_dir="./logs",
    logging_steps=100,
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=10,
    weight_decay=0.01,
    save_steps = 1000,
    report_to='wandb',
    load_best_model_at_end=True,
    save_strategy="epoch",
    metric_for_best_model="eval_loss",
    greater_is_better=False
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=valid_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=5)]
)

trainer.train()
trainer.save_model(os.path.join("./models",args.model_dir, "trained"))
trainer.evaluate()