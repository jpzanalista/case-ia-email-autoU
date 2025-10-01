"""
Aplicação para Hugging Face Spaces
Versão simplificada do AutoU Classificador
"""

import gradio as gr
import google.generativeai as genai
import os
import PyPDF2
import tempfile

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
            tmp_file.write(file)
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

def classify_email_with_ai(text):
    """Classifica o email usando Gemini"""
    try:
        prompt = f"""
        Classifique o seguinte email em uma das categorias:
        - "Produtivo": Emails que requerem uma ação ou resposta específica
        - "Improdutivo": Emails que não necessitam de uma ação imediata

        Email:
        {text}

        Responda APENAS com uma das palavras: "Produtivo" ou "Improdutivo"
        """

        if not gemini_client:
            return "MODO_TESTE"
            
        response = gemini_client.generate_content(prompt)
        classification = response.text.strip()
        
        # Garantir que a resposta seja válida
        if classification.lower() in ["produtivo", "improdutivo"]:
            return classification.capitalize()
        else:
            return "MODO_TESTE"
    except Exception as e:
        return f"Erro na classificação: {str(e)}"

def generate_response_with_ai(text, classification):
    """Gera resposta automática baseada na classificação"""
    try:
        if classification == "Produtivo":
            prompt = f"""
            O email abaixo foi classificado como PRODUTIVO.
            Gere uma resposta profissional para um cliente do setor financeiro.
            A resposta deve ser cordial, demonstrar que a solicitação foi recebida,
            indicar que o time irá analisar o caso e assinar como "Equipe de Suporte AutoU".

            Email original:
            {text}

            Resposta sugerida:
            """
        else:
            prompt = f"""
            O email abaixo foi classificado como IMPRODUTIVO.
            Gere uma resposta curta, cordial e profissional.
            A resposta deve ser breve, agradecer e assinar como "Equipe AutoU".

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

def process_email(email_text, uploaded_file):
    """Processa o email e retorna classificação e resposta"""
    if not email_text and not uploaded_file:
        return "❌ Por favor, insira um texto ou faça upload de um arquivo.", "", ""
    
    # Determinar o texto a processar
    if uploaded_file:
        if uploaded_file.name.endswith('.pdf'):
            text = extract_text_from_pdf(uploaded_file)
        else:
            text = uploaded_file.decode('utf-8')
    else:
        text = email_text
    
    if not text.strip():
        return "❌ Texto vazio após processamento.", "", ""
    
    try:
        # Classificar
        classification = classify_email_with_ai(text)
        
        # Gerar resposta
        response = generate_response_with_ai(text, classification)
        
        # Formatar resultado
        if classification == "Produtivo":
            result = f"🏆 **{classification}** - Este email requer ação/resposta"
        else:
            result = f"ℹ️ **{classification}** - Este email não requer ação imediata"
        
        return result, response, text[:200] + "..." if len(text) > 200 else text
        
    except Exception as e:
        return f"❌ Erro no processamento: {str(e)}", "", ""

# Interface Gradio
with gr.Blocks(
    title="AutoU - Classificador de Emails",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1200px !important;
    }
    """
) as demo:
    
    gr.Markdown("""
    # 📧 AutoU - Classificador de Emails com IA
    
    **Classificação inteligente de emails e geração de respostas automáticas**
    
    Esta aplicação utiliza IA para classificar emails em **Produtivo** (requer ação) ou **Improdutivo** (não requer ação) e sugerir respostas automáticas adequadas.
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 📨 Enviar Email para Análise")
            
            email_text = gr.Textbox(
                label="Texto do Email",
                placeholder="Cole aqui o conteúdo do email que deseja classificar...",
                lines=6,
                max_lines=10
            )
            
            uploaded_file = gr.File(
                label="Ou faça upload de um arquivo",
                file_types=[".txt", ".pdf"],
                file_count="single"
            )
            
            process_btn = gr.Button("🧠 Classificar Email", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            gr.Markdown("### ℹ️ Sobre a Classificação")
            
            gr.Markdown("""
            **🏆 Produtivo**: Emails que requerem ação
            - Solicitações de suporte
            - Dúvidas técnicas  
            - Problemas com sistema
            - Solicitações de informações
            
            **ℹ️ Improdutivo**: Emails que não requerem ação
            - Felicitações
            - Agradecimentos
            - Mensagens informativas
            - Spam ou irrelevantes
            """)
    
    with gr.Row():
        with gr.Column():
            result = gr.Markdown(label="📊 Resultado da Classificação")
            
            response = gr.Textbox(
                label="💬 Resposta Sugerida",
                lines=6,
                interactive=False
            )
            
            original_text = gr.Textbox(
                label="📄 Texto Analisado",
                lines=3,
                interactive=False
            )
    
    # Exemplos
    gr.Markdown("### 📝 Exemplos de Teste")
    
    with gr.Row():
        gr.Examples(
            examples=[
                ["Olá, estou com problema para acessar minha conta. Podem me ajudar?", "Produtivo"],
                ["Feliz Natal para toda a equipe! Obrigado pelo excelente trabalho.", "Improdutivo"],
                ["Preciso de informações sobre os novos produtos financeiros disponíveis.", "Produtivo"],
                ["Obrigado pelo atendimento excelente de hoje!", "Improdutivo"]
            ],
            inputs=[email_text],
            label="Clique em um exemplo para testar"
        )
    
    # Event handlers
    process_btn.click(
        fn=process_email,
        inputs=[email_text, uploaded_file],
        outputs=[result, response, original_text]
    )
    
    gr.Markdown("---")
    gr.Markdown("**Desenvolvido para o Case Prático da AutoU** 🚀")

if __name__ == "__main__":
    demo.launch()

