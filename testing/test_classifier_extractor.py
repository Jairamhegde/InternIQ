import pandas as pd
import pytest
from keyword_match.field_trend import similarity_check
from dbconnection.dbconnect import connect_database

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def test_similarity_check():
    job_title = "AI Engineer"
    description = "Design, build, and deploy machine learning and deep learning models into production. Build pipelines for large language models and NLP tasks."
    skills = ["Python", "Machine Learning", "Deep Learning", "NLP", "PyTorch", "TensorFlow", "LLMs"]
    
    label, score = similarity_check(job_title, description, skills)
    assert label == "machine learning"

def export_data():
    engine = connect_database("clean_data")
    query = """
        SELECT job_id, title, primary_field, field_confidence
        FROM job_data
        ORDER BY RANDOM() LIMIT 100;
    """
    df = pd.read_sql_query(query, engine)
    df['true_col'] = df['primary_field']
    df.to_csv('testing/test.csv', index=False)
    return df


def check_accuracy():

    df = pd.read_csv('testing/test.csv')

    df = df.dropna(subset=['true_col', 'primary_field'])
    
    acc = accuracy_score(df['true_col'], df['primary_field']) * 100
    print(f"  Overall Accuracy: {acc:.2f}%" ,f"total records : {len(df)}") 
    
    print(classification_report(df['true_col'], df['primary_field'], zero_division=0))
    
    print(pd.crosstab(df['true_col'], df['primary_field'], rownames=['Actual'], colnames=['Predicted']))


if __name__ == "__main__":
    check_accuracy()

    

