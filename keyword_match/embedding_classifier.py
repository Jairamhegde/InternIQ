"""
Job field classifier built on sentence embeddings.

How it works:
  1. Every job (title + skills) is turned into a 384-number vector by a small
     embedding model. Jobs with similar meaning get similar vectors.
  2. Jobs with an obvious title ("react developer", "data engineer") are
     labelled automatically using TITLE_KEYWORDS.
  3. A Logistic Regression model learns from those labelled jobs, so it can
     also classify unclear titles ("software developer") by their skills.

Train:    python -m keyword_match.embedding_classifier
Predict:  predict_field("software developer", ["react", "css", "html"])
"""

import json
import re
from pathlib import Path

import joblib
from fastembed import TextEmbedding
from sklearn.linear_model import LogisticRegression

RAW_DATA_FILE = Path("rawdata.json")
MODEL_FILE = Path(__file__).parent / "models" / "field_classifier.joblib"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Order matters: the first field whose keyword appears in the title wins,
# e.g. "react native developer" must be mobile, not frontend.
TITLE_KEYWORDS = {
    "mobile": ["android", "ios", "flutter", "react native", "mobile", "kotlin", "swift"],
    "fullstack": ["full stack", "fullstack", "mern", "mean stack"],
    "devops": ["devops", "sre", "site reliability", "cloud engineer", "platform engineer"],
    "big data": ["big data", "data engineer", "etl", "spark", "hadoop", "data pipeline"],
    "data science": ["data scientist", "data science", "data analyst", "data analytics"],
    "machine learning": ["machine learning", "ml", "ai", "artificial intelligence",
                         "llm", "generative", "deep learning", "nlp", "computer vision"],
    "frontend": ["front end", "frontend", "react", "angular", "vue", "ui developer"],
    "backend": ["backend", "back end", "django", "flask", "fastapi", "node", "php",
                "laravel", "java developer", "python developer", "net developer", "golang"],
}

_embedder = None


def get_embedder():
    """Load the embedding model once and reuse it."""
    global _embedder
    if _embedder is None:
        _embedder = TextEmbedding(EMBEDDING_MODEL)
    return _embedder


def embed(texts):
    """Turn a list of texts into a list of vectors."""
    return list(get_embedder().embed(texts))


def job_to_text(title, skills):
    """Combine title and skills into one sentence for the embedding model."""
    return f"{title}. Skills: {', '.join(skills)}"


def clean_title(title):
    """Lowercase, remove symbols, and pad with spaces for whole-word matching."""
    title = re.sub(r"[^a-z0-9]+", " ", title.lower())
    return f" {title.strip()} "


def label_from_title(title):
    """Return a field if the title clearly names one, otherwise None."""
    title = clean_title(title)
    for field, keywords in TITLE_KEYWORDS.items():
        for keyword in keywords:
            if f" {keyword} " in title:
                return field
    return None


def load_jobs():
    """Read jobs from rawdata.json as a list of (title, skills)."""
    data = json.loads(RAW_DATA_FILE.read_text(encoding="utf-8"))

    skill_names = {s["skill_id"]: s["name"] for s in data["Skills"]}
    skills_by_job = {}
    for link in data["JobSkills"]:
        skills_by_job.setdefault(link["job_id"], []).append(skill_names[link["skill_id"]])

    return [(job["title"], skills_by_job.get(job["id"], [])) for job in data["JobData"]]


def build_training_data():
    """Keep only jobs whose title gives a clear label; drop duplicates."""
    texts, labels = [], []
    seen = set()
    for title, skills in load_jobs():
        field = label_from_title(title)
        text = job_to_text(title, skills)
        if field and text not in seen:
            seen.add(text)
            texts.append(text)
            labels.append(field)
    return texts, labels

def train():
    texts, labels = build_training_data()
    print(f"Training on {len(texts)} labelled jobs")
    for field in TITLE_KEYWORDS:
        print(f"  {field:<17} {labels.count(field)}")

    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(embed(texts), labels)

    MODEL_FILE.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    print(f"Saved model to {MODEL_FILE}")


_model = None


def predict_field(title, skills):
    """Return (field, confidence) for one job."""
    global _model
    if _model is None:
        _model = joblib.load(MODEL_FILE)

    vector = embed([job_to_text(title, skills)])
    probabilities = _model.predict_proba(vector)[0]
    best = probabilities.argmax()
    return _model.classes_[best], round(float(probabilities[best]), 3)


if __name__ == "__main__":
    train()
