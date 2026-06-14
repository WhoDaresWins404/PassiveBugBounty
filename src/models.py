import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


MODEL_BASE = "./models/"


ANALYZER_MAP = {
    "SQLi": "pt_bert",  # Path Traversal/SQLi share the pt model
    "XSS": "xss_bert",
    "SSRF": "ssrf_bert",
    "Path Traversal": "pt_bert",
    "CMDi": "cmdi_bert",
}


class BERTAnalyzer:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}

    def _get_model(self, model_key):
        if model_key not in self.models:
            path = os.path.join(MODEL_BASE, ANALYZER_MAP[model_key])
            self.tokenizers[model_key] = AutoTokenizer.from_pretrained(path)
            self.models[model_key] = AutoModelForSequenceClassification.from_pretrained(path).to("cpu")
        return self.models[model_key], self.tokenizers[model_key]

    def analyze(self, method, url, body):
        findings = []
        for vuln_type in ANALYZER_MAP:
            model, tokenizer = self._get_model(vuln_type)
            inputs = tokenizer(f"{method} {url} | {body}", return_tensors="pt").to("cpu")
            with torch.no_grad():
                logits = model(**inputs).logits

        probs = torch.softmax(logits, dim=-1)[0].tolist()

        types = ["SQLi", "XSS", "SSRF", "Path Traversal", "CMDi"]
        for i, prob in enumerate(probs):
            if prob > 0.8:
                findings.append({
                    "type": types[i],
                    "severity": "high" if prob > 0.9 else "medium",
                    "confidence": round(prob, 2),
                    "description": f"{types[i]} detected by BERT with high confidence."
                })
        return findings


def get_all_analyzers():
    return [BERTAnalyzer()]
