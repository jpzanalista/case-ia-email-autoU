import os
import json
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configurar Gemini
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key and gemini_api_key != 'SUA_CHAVE_GEMINI_AQUI':
    genai.configure(api_key=gemini_api_key)
    gemini_client = genai.GenerativeModel('gemini-2.0-flash')
else:
    gemini_client = None

# Configurações para upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extrai texto de arquivo PDF"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return f"Erro ao ler PDF: {str(e)}"

def preprocess_text(text):
    """Pré-processa o texto do email"""
    # Limpeza básica
    text = text.strip()
    text = ' '.join(text.split())  # Remove espaços extras
    return text

def classify_email_with_ai(text):
    """Classifica o email usando Gemini"""
    try:
        if not gemini_client:
            return "MODO_TESTE"
            
        prompt = f"""
        Classifique o seguinte email em uma das categorias:
        - "Produtivo": Emails que requerem uma ação ou resposta específica (ex.: solicitações de suporte técnico, atualização sobre casos em aberto, dúvidas sobre o sistema)
        - "Improdutivo": Emails que não necessitam de uma ação imediata (ex.: mensagens de felicitações, agradecimentos)

        Email:
        {text}

        Responda APENAS com uma das palavras: "Produtivo" ou "Improdutivo"
        """

        response = gemini_client.generate_content(prompt)
        classification = response.text.strip()
        
        # Garantir que a resposta seja válida
        if classification.lower() in ["produtivo", "improdutivo"]:
            return classification.capitalize()
        else:
            return "MODO_TESTE"
            
    except Exception as e:
        return "MODO_TESTE"
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
            return "MODO_TESTE"
        else:
            return f"Erro na classificação: {error_msg}"

def generate_response_with_ai(text, classification):
    """Gera resposta automática baseada na classificação"""
    try:
        # Modo teste quando a API não está disponível
        if classification == "MODO_TESTE" or not gemini_client:
            return """Olá!

Obrigado pelo seu contato. Recebemos sua mensagem e nossa equipe irá analisá-la em breve.

Devido a limitações temporárias da API, estamos processando emails em modo de demonstração. Em breve retornaremos ao funcionamento normal.

Atenciosamente,
Equipe AutoU"""
        
        if classification == "Produtivo":
            prompt = f"""
            O email abaixo foi classificado como PRODUTIVO (requer ação/resposta).
            Gere uma resposta profissional e proativa para um cliente do setor financeiro.
            A resposta deve:
            - Ser cordial e profissional
            - Demonstrar que a solicitação foi recebida
            - Indicar que o time irá analisar o caso
            - Solicitar mais informações se necessário
            - Assinar como "Equipe de Suporte AutoU"

            Email original:
            {text}

            Resposta sugerida:
            """
        else:  # Improdutivo
            prompt = f"""
            O email abaixo foi classificado como IMPRODUTIVO (não requer ação imediata).
            Gere uma resposta curta, cordial e profissional para um cliente do setor financeiro.
            A resposta deve:
            - Ser breve e agradecer
            - Manter tom profissional
            - Assinar como "Equipe AutoU"

            Email original:
            {text}

            Resposta sugerida:
            """

        response = gemini_client.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return """Olá!

Obrigado pelo seu contato. Recebemos sua mensagem e nossa equipe irá analisá-la em breve.

Devido a limitações temporárias da API, estamos processando emails em modo de demonstração. Em breve retornaremos ao funcionamento normal.

Atenciosamente,
Equipe AutoU"""
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
            return """Olá!

Obrigado pelo seu contato. Recebemos sua mensagem e nossa equipe irá analisá-la em breve.

Devido a limitações temporárias da API, estamos processando emails em modo de demonstração. Em breve retornaremos ao funcionamento normal.

Atenciosamente,
Equipe AutoU"""
        else:
            return f"Erro na geração de resposta: {error_msg}"

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_email():
    """Processa o email e retorna classificação e resposta"""
    try:
        # Verificar se há texto direto ou arquivo
        if 'email_text' in request.form and request.form['email_text'].strip():
            # Texto direto
            email_text = request.form['email_text']
        elif 'email_file' in request.files:
            # Arquivo enviado
            file = request.files['email_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Extrair texto baseado no tipo de arquivo
                if filename.lower().endswith('.pdf'):
                    email_text = extract_text_from_pdf(file_path)
                else:  # .txt
                    with open(file_path, 'r', encoding='utf-8') as f:
                        email_text = f.read()
                
                # Limpar arquivo temporário
                os.remove(file_path)
            else:
                return jsonify({'error': 'Arquivo não permitido ou vazio'}), 400
        else:
            return jsonify({'error': 'Nenhum texto ou arquivo fornecido'}), 400

        # Pré-processar texto
        processed_text = preprocess_text(email_text)
        
        if not processed_text:
            return jsonify({'error': 'Texto vazio após processamento'}), 400

        # Classificar email
        classification = classify_email_with_ai(processed_text)
        
        # Gerar resposta
        response_text = generate_response_with_ai(processed_text, classification)
        
        return jsonify({
            'success': True,
            'classification': classification,
            'response': response_text,
            'original_text': processed_text[:500] + '...' if len(processed_text) > 500 else processed_text
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro no processamento: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
