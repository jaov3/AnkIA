import mlflow.sklearn
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, Any

app = FastAPI(title="Customer Feedback AI Agent")

# --- Carregamento do Modelo (MLOps) ---
# Tenta carregar o modelo salvo na pasta mlruns. 
# Em produção real, usaríamos o MLflow Model Registry, mas aqui carregamos um placeholder.
try:
    # Em produção, você carregaria o modelo com:
    # model = mlflow.sklearn.load_model("runs:/<RUN_ID>/classification_model")
    model = None 
    print("Modelo inicializado (placeholder).")
except Exception as e:
    print(f"Erro ao carregar modelo: {e}")

# --- Estruturas de Dados ---
class FeedbackRequest(BaseModel):
    text: str

class FeedbackResponse(BaseModel):
    category: str
    sentiment: str
    summary: str

@app.post("/process", response_model=FeedbackResponse)
def process_feedback(request: FeedbackRequest):
    """
    Endpoint que recebe o feedback, classifica (ML) e resume (LLM - Simulado).
    """
    text = request.text
    text_lower = text.lower()
    
    # 1. CLASSIFICAÇÃO (ML TRADICIONAL) - Simulação
    # Esta é a parte que seria feita pelo modelo que você treinou na Fase 2.
    if "atrasou" in text_lower or "chegou tarde" in text_lower or "logística" in text_lower:
        ml_category = "Logística"
    elif "travou" in text_lower or "bug" in text_lower or "pix" in text_lower:
        ml_category = "Bug no App"
    elif "sugestão" in text_lower or "adicionar" in text_lower:
        ml_category = "Sugestão"
    else:
        ml_category = "Geral / Outros"

    # 2. AGENTE LLM (LLMOps/Prompt Engineering) - Lógica de Simulação Aprimorada
    # Aqui entraria a chamada real à API LLM (ex: LangChain), mas usamos lógica 
    # para simular a extração de SENTIMENTO e RESUMO de forma coerente.

    # Simulação da extração de SENTIMENTO:
    if "rude" in text_lower or "atrasou" in text_lower or "fria" in text_lower or "errada" in text_lower or "sumiu" in text_lower:
        sentiment = "Negativo"
        summary = "Cliente insatisfeito. Problemas identificados: " + ml_category + ". Requer atenção imediata da equipe responsável."
    
    elif "gentil" in text_lower or "quente" in text_lower or "5 estrelas" in text_lower or "impecável" in text_lower or "adorei" in text_lower:
        sentiment = "Positivo"
        summary = "Cliente muito satisfeito! Feedback positivo sobre " + ml_category + ". Oportunidade para incentivar boas práticas."
    
    else:
        sentiment = "Neutro"
        summary = "O feedback não contém palavras-chave críticas. Classificado como " + ml_category + " para análise de produto."
        
    # 3. Retorno da API
    return FeedbackResponse(
        category=ml_category,
        sentiment=sentiment,
        summary=summary
    )

@app.get("/")
def health_check():
    # Health check para confirmar que a API está rodando
    return {"status": "Agente Ativo 🚀"}