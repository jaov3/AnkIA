AnkIA - Agente de Análise de Feedback com IA

O AnkIA é um agente inteligente desenvolvido para automatizar a triagem e análise de feedbacks de clientes. Utilizando Large Language Models (LLMs), o sistema interpreta comentários em linguagem natural, classifica sentimentos e categorias, e armazena dados estruturados para inteligência de negócios.

Funcionalidades

Análise de Sentimento com IA: Classifica automaticamente o feedback como Positivo, Neutro ou Negativo usando o modelo Gemini 2.5 Flash.

Categorização Inteligente: Identifica o tópico principal (Logística, Bug no App, Sugestão, Atendimento, etc.).

Geração de Resumo: Cria um resumo acionável sobre o problema ou elogio.

Saída Estruturada (JSON): Garante integridade de dados forçando o LLM a seguir um esquema rígido.

Persistência de Dados: Salva todo o histórico de análises no Google Firebase Firestore.

Interface Web: Frontend leve para testes e envio de feedback em tempo real.

Modo Fallback: Sistema de segurança que utiliza análise de palavras-chave caso a API de IA esteja indisponível.

Tecnologias Utilizadas

Linguagem: Python

Backend: FastAPI (Alta performance e validação via Pydantic)

IA Generativa: Google Gemini API (SDK google-genai)

Banco de Dados: Google Firestore (NoSQL)

Frontend: HTML5, CSS3, JavaScript (Vanilla)

Gerenciamento de Ambiente: python-dotenv

Instalação e Configuração

Siga os passos abaixo para rodar o projeto localmente.

1. Pré-requisitos

Python instalado.

Conta no Google Cloud (para Firebase).

Chave de API do Google AI Studio (Gemini).

2. Clonar o Repositório

git clone [https://github.com/seu-usuario/AnkIA.git](https://github.com/seu-usuario/AnkIA.git)
cd AnkIA


3. Configurar Ambiente Virtual

# Criar o ambiente
python -m venv .venv

# Ativar (Windows/Git Bash)
source .venv/Scripts/activate
# Ativar (Linux/Mac)
source .venv/bin/activate


4. Instalar Dependências

pip install -r requirements.txt


5. Configurar Variáveis de Ambiente (.env)

Crie um arquivo chamado .env na raiz do projeto e adicione suas credenciais:

GEMINI_API_KEY="SUA_CHAVE_API_DO_GOOGLE_AI_STUDIO"
GOOGLE_CLOUD_PROJECT="SEU_ID_DO_PROJETO_FIREBASE"


6. Autenticação Google Cloud (Para o Firestore)

O projeto utiliza as credenciais padrão da aplicação (ADC).

gcloud auth application-default login


Como Rodar

Com o ambiente configurado, inicie o servidor FastAPI:

uvicorn agente_service.api:app --reload


Acesse a interface web no seu navegador:
https://www.google.com/search?q=http://127.0.0.1:8000/

Para documentação da API (Swagger UI):
https://www.google.com/search?q=http://127.0.0.1:8000/docs

Detalhes da Implementação

Estrutura de Pastas

AnkIA/
├── agente_service/
│   └── api.py          # Lógica do Backend, Rotas e Integração LLM
├── static/
│   └── index.html      # Frontend da aplicação
├── .env                # Variáveis de ambiente (não rastreado pelo git)
├── requirements.txt    # Dependências do projeto
└── README.md           # Documentação


Desafios de Engenharia

Durante o desenvolvimento, foi necessário resolver incompatibilidades entre o validador do Pydantic V2 e o SDK do Google Gemini. A solução adotada foi a definição manual do esquema (Schema) dentro do código, garantindo que a estrutura enviada ao modelo seja limpa e livre de metadados extras que causavam erros de validação automáticos.

Licença

Este projeto foi desenvolvido para fins de avaliação técnica.
