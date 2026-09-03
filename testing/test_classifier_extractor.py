import pytest
from keyword_match.field_trend import similarity_check


def test_similarity_check():
    job_title = "AI Engineer"
    description = "Design, build, and deploy machine learning and deep learning models into production. Build pipelines for large language models and NLP tasks."
    skills = ["Python", "Machine Learning", "Deep Learning", "NLP", "PyTorch", "TensorFlow", "LLMs"]
    
    label, score = similarity_check(job_title, description, skills)
    
    assert label == "machine learning"



    

