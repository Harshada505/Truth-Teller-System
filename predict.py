import os
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from sklearn.metrics import accuracy_score, f1_score

# Define label mapping
label_mapping = {0: "TRUE", 1: "FALSE", 2: "Neutral"}

def predict_sentences(test_records, model_path='./saved_model', true_labels=None):
    # Validate model path
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model path '{model_path}' not found")

    # Load tokenizer and model
    tokenizer = RobertaTokenizer.from_pretrained(model_path)
    model = RobertaForSequenceClassification.from_pretrained(model_path)
    model.eval()

    # Prepare input text
    combined_texts = [
        (
            record.get('speaker_name', '') + " " +
            record.get('speaker_role', '') + " " +
            record.get('speech_title', '') + " " +
            record.get('text', '')
        ).strip()
        for record in test_records
    ]

    inputs = tokenizer(combined_texts, padding=True, truncation=True, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)

    results = []
    pred_labels = []

    for record, pred in zip(test_records, predictions):
        label = label_mapping[pred.item()]
        pred_labels.append(label)
        results.append({
            "sentence_id": record.get("sentence_id"),
            "combined_text": record.get("combined_text", ""),
            "predicted_label": label,
            "original_text": record.get("text"),
            "speaker_name": record.get("speaker_name"),
            "speaker_role": record.get("speaker_role"),
            "speech_title": record.get("speech_title"),
            "url": record.get("url")
        })

    # Print metrics if ground truth is provided
    if true_labels:
        true_numeric = [label_mapping.index(lbl) if lbl in label_mapping else -1 for lbl in true_labels]
        pred_numeric = [list(label_mapping.keys())[list(label_mapping.values()).index(lbl)] for lbl in pred_labels]
        acc = accuracy_score(true_numeric, pred_numeric)
        f1 = f1_score(true_numeric, pred_numeric, average='weighted')
        print(f"Prediction Accuracy: {acc * 100:.2f}%")
        print(f"Prediction F1 Score: {f1 * 100:.2f}%")

    return results
