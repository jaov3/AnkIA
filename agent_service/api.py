import os
import json
import datetime
from typing import Dict, Any

# --- Adições para Automação e Frontend ---
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse 
from fastapi.responses import HTMLResponse
# ----------------------------------------

# --- Carregar Variáveis de Ambiente ---
load_dotenv() 

# --- Importações do FastAPI e Pydantic ---
from fastapi import FastAPI
from pydantic import BaseModel, Field

# --- Importações do Firebase ---
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# --- Importações do Gemini API ---
from google import genai
from google.genai import types


# --- Configuração do LLM ---
try:
    if os.environ.get("GEMINI_API_KEY"):
        LLM_CLIENT = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        print("🤖 Cliente Gemini API inicializado.")
    else:
        LLM_CLIENT = None
        print("⚠️ Variável GEMINI_API_KEY não encontrada. Usando simulação antiga.")
except Exception as e:
    print(f"❌ Erro ao inicializar o Cliente Gemini: {e}")
    LLM_CLIENT = None

# --- Configuração do Firebase ---
try:
    # Verifica se já existe um app inicializado para evitar erro de duplicidade no reload
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("🚀 Firebase e Firestore inicializados com sucesso.")
except Exception as e:
    print(f"⚠️ Erro ao inicializar o Firebase: {e}")
    db = None

app = FastAPI(title="Customer Feedback AI Agent")

# --- BLOCO: MONTAR ARQUIVOS ESTÁTICOS ---
app.mount("/static", StaticFiles(directory="static"), name="static")
# ---------------------------------------------


# --- Modelos Pydantic ---
class FeedbackRequest(BaseModel):
    text: str

class FeedbackResponse(BaseModel):
    category: str = Field(description="Classifique em uma destas opções: 'Logística', 'Bug no App', 'Sugestão', 'Atendimento' ou 'Geral'.")
    sentiment: str = Field(description="Classifique em 'Positivo', 'Neutro' ou 'Negativo'.")
    summary: str = Field(description="Uma breve descrição da ação necessária (se for Negativo) ou o ponto positivo (se for Positivo).")

# --- Função de Fallback (Lógica Antiga de Keywords) ---
def simular_processamento_antigo(text: str) -> FeedbackResponse:
    """ Usa a lógica de keywords como fallback. """
    text_lower = text.lower()
    
    if "atrasou" in text_lower or "chegou tarde" in text_lower or "logística" in text_lower:
        ml_category = "Logística"
    elif "travou" in text_lower or "bug" in text_lower or "pix" in text_lower:
        ml_category = "Bug no App"
    elif "sugestão" in text_lower or "adicionar" in text_lower:
        ml_category = "Sugestão"
    else:
        ml_category = "Geral / Outros"

    if "rude" in text_lower or "atrasou" in text_lower or "fria" in text_lower or "errada" in text_lower or "sumiu" in text_lower:
        sentiment = "Negativo"
        summary = "Cliente insatisfeito. Problemas identificados: " + ml_category + ". Requer atenção imediata da equipe responsável."
    
    elif "gentil" in text_lower or "quente" in text_lower or "5 estrelas" in text_lower or "impecável" in text_lower or "adorei" in text_lower:
        sentiment = "Positivo"
        summary = "Cliente muito satisfeito! Feedback positivo sobre " + ml_category + ". Oportunidade para incentivar boas práticas."
    
    else:
        sentiment = "Neutro"
        summary = "O feedback não contém palavras-chave críticas. Classificado como " + ml_category + " para análise de produto."
        
    return FeedbackResponse(
        category=ml_category,
        sentiment=sentiment,
        summary=summary
    )

# --- Função para Salvar no Firestore ---
def save_to_firestore(data: Dict[str, Any]):
    """ Salva os dados de feedback processados na coleção 'feedback_history' do Firestore. """
    if db:
        try:
            data['timestamp'] = datetime.datetime.now(tz=datetime.timezone.utc)
            db.collection('feedback_history').add(data)
            print(f"✅ Feedback salvo no Firestore: {data.get('category')} / {data.get('sentiment')}")
        except Exception as e:
            print(f"❌ Erro ao salvar no Firestore: {e}")
    else:
        print("❌ Firestore não inicializado. Não foi possível salvar o feedback.")

# --- Endpoint Principal (com LLM) ---
@app.post("/process", response_model=FeedbackResponse)
def process_feedback(request: FeedbackRequest):
    """
    Endpoint que envia o feedback para o LLM (Gemini 2.5 Flash)
    para classificação estruturada e salva no Firestore.
    """
    text = request.text
    
    if LLM_CLIENT is None:
        print("⚠️ Usando Fallback. LLM_CLIENT é None.")
        return simular_processamento_antigo(text)

    # --- 1. PROMPT ENGINEERING e CONFIGURAÇÃO ---
    prompt = f"Analise o texto do cliente e retorne o objeto JSON com base no esquema fornecido. TEXTO: '{text}'"

    # --- CORREÇÃO APLICADA AQUI ---
    # Removemos a conversão manual para types.Schema e passamos a classe Pydantic direto.
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=FeedbackResponse # O SDK lida com a conversão automaticamente
    )

    # --- 2. CHAMADA AO LLM ---
    try:
        response = LLM_CLIENT.models.generate_content(
            model='gemini-2.0-flash', # Ajuste para o modelo correto disponivel (2.0 flash é o padrão atual)
            contents=prompt,
            config=config
        )
        
        # Parsing da resposta
        # O modelo pode retornar o objeto já parseado em response.parsed se suportado,
        # mas manteremos a lógica de json.loads para garantir compatibilidade com o texto cru.
        llm_json_string = response.text.strip()
        
        try:
            llm_output_data = json.loads(llm_json_string)
        except json.JSONDecodeError:
            print(f"❌ ERRO DE PARSING: O LLM retornou JSON inválido.")
            print(f"❌ TEXTO RETORNADO PELO LLM: {llm_json_string}")
            raise ValueError("Resposta do LLM não é um JSON válido.")

        response_data = FeedbackResponse(**llm_output_data)

    except Exception as e:
        print(f"❌ Erro na chamada do LLM/Processamento: {e}")
        summary_text = str(e)
        if len(summary_text) > 100:
             summary_text = summary_text[:100] + "..."
             
        response_data = FeedbackResponse(
             category="Erro de LLM", 
             sentiment="Neutro", 
             summary=f"Falha na API Gemini: {summary_text}"
        )

    # --- 3. SALVAR NO FIRESTORE ---
    firestore_data = response_data.model_dump()
    firestore_data["raw_text"] = text
    save_to_firestore(firestore_data)
        
    return response_data


# --- ENDPOINT PARA SERVIR O FRONTEND ---
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend():
    """Serve a página HTML principal do frontend (index.html)."""
    # Verifica se o arquivo existe antes de tentar servir
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return HTMLResponse(content="<h1>Frontend não encontrado em /static/index.html</h1>", status_code=404)

# --- Endpoint health_check ---
@app.get("/health_check")
def health_check():
    return {"status": "Agente Ativo 🚀"}