import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import sys
import io
import os
import json
from datetime import datetime

# ================================
# CONFIGURAÇÃO DA PÁGINA
# ================================
st.set_page_config(
    page_title="DataAgent EDA",
    page_icon="🕵️",
    layout="wide",
    menu_items={
        'Get Help': 'https://docs.streamlit.io/',
        'Report a bug': "mailto:warioabox-suporte@yahoo.com",
        'About': """
        # 🕵️ DataAgent EDA

        ## Agente Inteligente de Análise de Dados

        Faça perguntas em português sobre seus arquivos CSV, Excel ou JSON e receba respostas com gráficos, estatísticas e código gerado por IA.

        **Versão:** 1.0.9

        **©︎ MAO 2025**
        """
    }
)

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
st.session_state.setdefault("db_ready", False)

if "database" not in st.session_state:
    if os.path.exists("database.py"):
        try:
            import database
            database.init_db()
            st.session_state.database = database
            st.session_state.db_ready = True
        except Exception as e:
            st.error("❌ Erro ao carregar módulo 'database.py'")
            st.exception(e)
    else:
        st.warning("⚠️ Arquivo `database.py` não encontrado. O histórico não será salvo.")
        st.session_state.db_ready = False

# --- CONFIGURAÇÃO DO GEMINI ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error("❌ Erro na API Gemini. Confira `secrets.toml`.")
    st.stop()

# --- EXECUÇÃO SEGURA DE CÓDIGO ---
def execute_safe_code(code, df):
    SAFE_GLOBALS = {
        "__builtins__": {k: __builtins__[k] for k in ["print", "len", "sum", "min", "max", "abs", "round", "int", "float"] if k in __builtins__},
        "pd": pd,
        "df": df,
        "plt": plt,
        "sns": sns
    }
    local_vars = {"fig": None, "ax": None}
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()
    fig, ax = plt.subplots(figsize=(8, 5))
    local_vars["fig"], local_vars["ax"] = fig, ax

    prohibited = ["import", "open(", "exec(", "eval(", "os.", "sys."]
    if any(cmd in code.lower() for cmd in prohibited):
        sys.stdout = old_stdout
        plt.close(fig)
        return None, "🚫 Comando proibido detectado."

    try:
        exec(code, SAFE_GLOBALS, local_vars)
        output = captured.getvalue()
        if ax.has_data():
            return fig, output
        else:
            plt.close(fig)
            return None, output
    except Exception as e:
        plt.close(fig)
        return None, f"❌ Erro: {e}"
    finally:
        sys.stdout = old_stdout

# --- INICIALIZAÇÃO DA SESSÃO ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "df" not in st.session_state:
    st.session_state.df = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None

# ================================
# SIDEBAR: PAINEL DE INFORMAÇÕES
# ================================
st.sidebar.markdown(
    """
    <div style='
        font-size:24px;
        color:#1abc9c;
        font-weight:bold;
        text-shadow: 2px 1.7px 0px rgba(0,0,0,0.6);
    '>
        <h2 style='color:#1abc9c; font-size: 30px;'>🕵️ DataAgent</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Estado do Sistema
st.sidebar.markdown("### 🧩 Estado do Sistema")
if st.session_state.get("db_ready"):
    st.sidebar.success("✅ Banco: Ativo")
    st.sidebar.caption("Auto-salvamento habilitado")
else:
    st.sidebar.warning("⚠️ Banco: Inativo")
    st.sidebar.caption("Verifique database.py")

st.sidebar.divider()

# Histórico de Análises
st.sidebar.markdown("### ⏳ Histórico de Análises")
if st.session_state.get("db_ready"):
    try:
        sessions = st.session_state.database.list_all_sessions()
        if sessions:
            for item in sessions[:5]:
                if len(item) == 4:
                    session_id, file_name, start_time, last_update = item
                    date = last_update.split("T")[0]
                    if st.sidebar.button(f"📂 {file_name} ({date})", key=f"load_{session_id}"):
                        saved_msgs = st.session_state.database.load_session_by_filename(file_name)
                        if saved_msgs:
                            st.session_state.messages = saved_msgs
                            st.session_state.file_name = file_name
                            st.success(f"Histórico carregado: {file_name}")
                            st.sidebar.caption(f"💬 {len(saved_msgs)} interações")
                else:
                    st.sidebar.warning("⚠️ Dados inconsistentes no histórico")
        else:
            st.sidebar.caption("Nenhum histórico ainda.")
    except Exception as e:
        st.sidebar.error("❌ Falha ao carregar histórico")
        st.sidebar.exception(e)
else:
    st.sidebar.info("Sem histórico disponível")

if st.session_state.get("db_ready"):
    try:
        sessions = st.session_state.database.list_all_sessions()
        if len(sessions) > 0:
            if st.sidebar.button("🧹 Limpar Histórico", key="clear_history"):
                os.remove("mydatabase.db")
                st.session_state.messages = []
                st.success("✅ Histórico limpo!")
                st.rerun()
        else:
            st.sidebar.button("🧹 Limpar Histórico", disabled=True, help="Nada para limpar")
    except:
        pass

# ================================
# TÍTULO PRINCIPAL
# ================================
st.markdown(
    """
    <div style='
        font-size:24px;
        color:#1abc9c;
        font-weight:bold;
        text-shadow: 2px 2px 0px rgba(0,0,0,0.7);
    '>
        <h1 style='color:#1abc9c'>🕵️ DataAgent</h1>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("<p><i>Análise de dados com inteligência artificial</i></p>", unsafe_allow_html=True)

# ================================
# UPLOAD DO ARQUIVO
# ================================
uploaded_file = st.file_uploader("Carregue um arquivo", type=["csv", "xlsx", "json"])

if uploaded_file is not None and uploaded_file.name != st.session_state.file_name:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            df = pd.read_json(uploaded_file)

        st.session_state.df = df
        st.session_state.file_name = uploaded_file.name

        # Carrega histórico do banco se disponível
        if st.session_state.db_ready:
            saved_messages = st.session_state.database.load_session_by_filename(uploaded_file.name)
            if saved_messages:
                st.session_state.messages = saved_messages
                st.info("🧠 Histórico anterior restaurado!")
            else:
                st.session_state.messages = []
        else:
            st.session_state.messages = []

        st.rerun()

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")

# ================================
# MOSTRA DADOS E PERGUNTA
# ================================
if st.session_state.df is not None:
    df = st.session_state.df
    st.subheader("📋 Amostra dos Dados")
    st.dataframe(df.head(5))
    st.caption(f"🔢 {df.shape[0]} linhas × {df.shape[1]} colunas")

    user_question = st.text_input("Pergunte algo sobre os dados:", key="user_input")

    if st.button("🔍 Analisar") and user_question.strip():
        column_names = ", ".join(df.columns)

        # Limita o histórico às últimas 6 mensagens
        últimas_mensagens = st.session_state.messages[-6:]
        history = "\n".join([f"{m['role']}: {m['content']}" for m in últimas_mensagens])

        prompt = f"""
        Você é um assistente especialista em análise de dados com Python criado por MAO, mas também pode conversar de forma amigável. O DataFrame 'df' tem colunas: {column_names}.
        RESPONDA SEMPRE EM PORTUGUÊS DO BRASIL.

        REGRAS:
         1. Não use 'import', 'open(', 'exec(', 'eval('.
         2. Use diretamente 'df'.
         3. As bibliotecas 'pandas', 'matplotlib.pyplot', 'seaborn' já estão importadas e prontas para uso.
         4. Para gráficos, use o eixo 'ax': sns.histplot(data=df, x='col', ax=ax) ou df.plot(ax=ax).
         5. Configure títulos com ax.set_title(), xlabel, ylabel.
         6. Coloque TODO o código em um único bloco ```python.
         7. Seja claro e direto. Evite rodeios.
         8. Se for uma saudação (olá, oi, bom dia, boa tarde, etc.), responda de forma calorosa e amigável
         9. Se for uma pergunta geral, responda brevemente mas sempre mencione seu propósito principal
        10. Se for sobre análise de dados mas sem arquivo carregado, explique que ele precisa fazer upload primeiro
        11. Se não souber responder, diga que não é possível.

        Histórico:
        {history}

        Pergunta:
        {user_question}
        """

        with st.spinner("Processando..."):
            try:
                response = model.generate_content(prompt)
                answer = response.text or "Sem resposta."
            except Exception as e:
                st.error("❌ Falha ao conectar ao Gemini. Tente novamente.")
                st.stop()

            st.session_state.messages.append({"role": "assistant", "content": answer})

            # Salva automaticamente no SQLite
            if st.session_state.db_ready and st.session_state.file_name:
                st.session_state.database.save_session(
                    file_name=st.session_state.file_name,
                    messages=st.session_state.messages
                )

            with st.chat_message("assistant"):
                st.markdown(answer)
                code_match = re.search(r"```python\n(.*?)```", answer, re.DOTALL)
                if code_match:
                    code = code_match.group(1).strip()
                    with st.expander("Ver código"):
                        st.code(code, language="python")
                    fig, text_result = execute_safe_code(code, df)
                    st.subheader("Resultado:")
                    if text_result:
                        st.text(text_result)
                    if fig:
                        st.pyplot(fig)
                        buf = io.BytesIO()
                        fig.savefig(buf, format="png", bbox_inches="tight")
                        buf.seek(0)
                        st.download_button("⬇️ Baixar Gráfico", buf, "grafico.png", "image/png")
                else:
                    st.info("Nenhum código foi gerado.")

else:
    st.info("⬆️ Carregue um arquivo para começar.")