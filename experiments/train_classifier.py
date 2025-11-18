#experiments/train_classifier.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score
import mlflow
import json

mlflow.set_experiment("feedback_triagem_classifier")

def train_and_long():
    with mlflow.start_run():
        try:
            df = pd.read_csv("data/raw_feedback.csv")
        except FileNotFoundError:
            print("Erro: Arquivo 'data/raw_feedback.csv' não encontrado. Certifique-se de tê-lo adicionado e executado 'dvc pull' se necessário.")
            return

        df = df.dropna()

        X_train, X_test, y_train, y_test = train_test_split(
            df['review_text'], df['category'], test_size=0.2, random_state=42
        )
        vectorizer = TfidfVectorizer(max_features=5000)
        X_train_vectorized = vectorizer.fit_transform(X_train)
        X_test_vectorized = vectorizer.transform(X_test)

        model = LogisticRegression(max_iter=1000)
        model.fit(X_train_vectorized, y_train)

        y_pred = model.predict(X_test_vectorized)

        f1 = f1_score(y_test, y_pred, average='weighted')
        accuracy = accuracy_score(y_test, y_pred)
        
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_param("model_type", "LogisticRegression_TFIDF")
        mlflow.log_param("max_features", 5000)

        mlflow.sklearn.log_model(model, "classfication_model")

        print(f"Treinamento concluído. F1 Score: {f1:.4f}")

if __name__ == "__main__":
    train_and_long()
