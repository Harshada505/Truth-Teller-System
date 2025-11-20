import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import RobertaTokenizer, RobertaForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import numpy as np

# Load Excel dataset
df = pd.read_csv("truthteller_dataset.csv")

# Drop rows with missing labels
df = df.dropna(subset=["result", "text"])

# Map labels
label_mapping = {"TRUE": 0, "FALSE": 1, "Neutral": 2}
df["label"] = df["result"].map(label_mapping)

# Drop rows with invalid labels
df = df[df["label"].isin([0, 1, 2])]

# Combine speaker metadata and main text
df["combined_text"] = (
    df["speaker_name"].fillna('') + " " +
    df["speaker_role"].fillna('') + " " +
    df["speech_title"].fillna('') + " " +
    df["text"]
)

# Train-validation split
train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["combined_text"].tolist(),
    df["label"].tolist(),
    test_size=0.2,
    stratify=df["label"],
    random_state=42
)

# Custom Dataset
class TruthDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            padding="max_length",
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        item = {key: val.squeeze(0) for key, val in encoding.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

# Load tokenizer and model
tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
model = RobertaForSequenceClassification.from_pretrained("roberta-base", num_labels=3)

# Create datasets
train_dataset = TruthDataset(train_texts, train_labels, tokenizer)
val_dataset = TruthDataset(val_texts, val_labels, tokenizer)

# Training arguments
training_args = TrainingArguments(
    output_dir="./saved_model",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=5,
    weight_decay=0.01,
    logging_dir="./logs",
    load_best_model_at_end=True,
    metric_for_best_model="f1"
)

# Metric function
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average="weighted")
    print(f"\n📊 Accuracy: {acc * 100:.2f}% | F1 Score: {f1 * 100:.2f}%\n")
    return {"accuracy": acc, "f1": f1}

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

# Train
trainer.train()

# Save final model and tokenizer
model.save_pretrained("./saved_model")
tokenizer.save_pretrained("./saved_model")
