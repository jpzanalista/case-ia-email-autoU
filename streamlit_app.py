import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2
import tempfile

# Configuração da página
st.set_page_config(
    page_title="AutoU - Classificador de Emails",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Gemini
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key and gemini_api_key != 'SUA_CHAVE_GEMINI_AQUI':
    genai.configure(api_key=gemini_api_key)
    gemini_client = genai.GenerativeModel('gemini-2.0-flash')
else:
    gemini_client = None

def extract_text_from_pdf(file):
    """Extrai texto de arquivo PDF"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_file_path = tmp_file.name
        
        with open(tmp_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        os.unlink(tmp_file_path)
        return text
    except Exception as e:
        return f"Erro ao ler PDF: {str(e)}"

def preprocess_text(text):
    """Pré-processa o texto do email"""
    text = text.strip()
    text = ' '.join(text.split())
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
        return f"Erro na classificação: {str(e)}"

def generate_response_with_ai(text, classification):
    """Gera resposta automática baseada na classificação"""
    try:
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

        if not gemini_client:
            return """Olá!

Obrigado pelo seu contato. Recebemos sua mensagem e nossa equipe irá analisá-la em breve.

Devido a limitações temporárias da API, estamos processando emails em modo de demonstração. Em breve retornaremos ao funcionamento normal.

Atenciosamente,
Equipe AutoU"""

        response = gemini_client.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Erro na geração de resposta: {str(e)}"

def main():
    """Função principal da aplicação Streamlit"""
    
    # Header
    st.title("📧 AutoU - Classificador de Emails com IA")
    st.markdown("**Classificação inteligente de emails e geração de respostas automáticas**")
    
    # Sidebar
    st.sidebar.header("⚙️ Configurações")
    
    # Verificar se a chave da API está configurada
    if not gemini_api_key or gemini_api_key == "SUA_CHAVE_GEMINI_AQUI":
        st.error("⚠️ Chave da API Gemini não configurada!")
        st.info("Configure a variável de ambiente GEMINI_API_KEY")
        return
    
    # Opções de entrada
    st.sidebar.subheader("📝 Forma de Entrada")
    input_method = st.sidebar.radio(
        "Como deseja enviar o email?",
        ["Texto Direto", "Upload de Arquivo"]
    )
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📨 Email para Análise")
        
        email_text = ""
        
        if input_method == "Texto Direto":
            email_text = st.text_area(
                "Cole o conteúdo do email aqui:",
                height=200,
                placeholder="Digite ou cole o conteúdo do email que deseja classificar..."
            )
        else:
            uploaded_file = st.file_uploader(
                "Faça upload de um arquivo (.txt ou .pdf)",
                type=['txt', 'pdf']
            )
            
            if uploaded_file is not None:
                if uploaded_file.type == "text/plain":
                    email_text = str(uploaded_file.read(), "utf-8")
                elif uploaded_file.type == "application/pdf":
                    email_text = extract_text_from_pdf(uploaded_file)
                else:
                    st.error("Tipo de arquivo não suportado!")
                    return
        
        # Botão de processamento
        if st.button("🧠 Classificar Email", type="primary", disabled=not email_text.strip()):
            if email_text.strip():
                with st.spinner("Processando email com IA..."):
                    # Pré-processar texto
                    processed_text = preprocess_text(email_text)
                    
                    # Classificar
                    classification = classify_email_with_ai(processed_text)
                    
                    # Gerar resposta
                    response = generate_response_with_ai(processed_text, classification)
                    
                    # Exibir resultados
                    st.success("✅ Email processado com sucesso!")
                    
                    # Classificação
                    st.subheader("📊 Resultado da Classificação")
                    if classification == "Produtivo":
                        st.success(f"🏆 **{classification}** - Este email requer ação/resposta")
                    else:
                        st.info(f"ℹ️ **{classification}** - Este email não requer ação imediata")
                    
                    # Resposta sugerida
                    st.subheader("💬 Resposta Sugerida")
                    st.text_area(
                        "Resposta automática gerada:",
                        value=response,
                        height=150,
                        disabled=True
                    )
                    
                    # Botão para copiar
                    if st.button("📋 Copiar Resposta"):
                        st.write("Resposta copiada para a área de transferência!")
    
    with col2:
        st.subheader("ℹ️ Sobre a Classificação")
        
        st.info("""
        **Produtivo**: Emails que requerem ação
        - Solicitações de suporte
        - Dúvidas técnicas
        - Problemas com sistema
        - Solicitações de informações
        """)
        
        st.warning("""
        **Improdutivo**: Emails que não requerem ação
        - Felicitações
        - Agradecimentos
        - Mensagens informativas
        - Spam ou irrelevantes
        """)
        
        st.subheader("🔧 Tecnologias")
        st.markdown("""
        - **IA**: Google Gemini 1.5 Flash
        - **Backend**: Python Streamlit
        - **Processamento**: NLP avançado
        - **Interface**: Responsiva e intuitiva
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("**Desenvolvido para o Case Prático da AutoU** 🚀")

if __name__ == "__main__":
    main()
