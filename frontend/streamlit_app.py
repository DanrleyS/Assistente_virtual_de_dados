import sys
import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(base_dir, ".env"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.graph.workflow import build_graph

MAX_ROWS = 50  # limite seguro

def safe_chart(df: pd.DataFrame):
    try:
        #Mantém apenas colunas numéricas
        numeric_df = df.select_dtypes(include=["number"])

        #Sem dados numéricos → não faz gráfico
        if numeric_df.empty:
            st.info("📊 Não foi possível gerar gráfico para esses dados.")
            st.dataframe(df)
            return

        #Muitos dados → corta
        if len(df) > MAX_ROWS:
            st.warning(f"⚠️ Muitos dados ({len(df)} linhas). Exibindo apenas os primeiros {MAX_ROWS}.")
            df = df.head(MAX_ROWS)
            numeric_df = numeric_df.head(MAX_ROWS)

        #Define índice
        index_col = df.columns[0]

        chart_df = numeric_df.copy()
        chart_df.index = df[index_col]

        st.line_chart(chart_df)

    except Exception as e:
        st.warning("⚠️ Não foi possível gerar gráfico automaticamente.")
        st.info("📄 Exibindo dados completos abaixo:")
        st.dataframe(df)

# CONFIG
st.set_page_config(
    page_title="Assistente de Dados",
    page_icon="📊",
    layout="wide"
)


# INIT GRAPH
@st.cache_resource
def get_graph():
    return build_graph()

graph = get_graph()

# STATE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

# UI
st.title("📊 Assistente de Dados")
st.caption("Faça perguntas sobre seus dados")

# HISTÓRICO
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and "steps" in msg:
            with st.expander("🔍 Ver etapas"):
                for step in msg["steps"]:
                    st.json(step)

# INPUT
user_input = st.chat_input("Digite sua pergunta...")

if user_input:
    # salva pergunta
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # resposta
    with st.chat_message("assistant"):
        with st.spinner("Consultando dados..."):

            try:
                db_path = os.path.join(base_dir, "db", "clientes_completo.db")
                state = {
                    "question": user_input,
                    "attempts": 0,
                    "max_attempts": 3,
                    "error": None,
                    "empty_result": False,
                    "steps": [],
                    "db_path": db_path
                }

                result = graph.invoke(state)

                answer = result.get("final_answer", "Sem resposta.")

                #pegar também dados do analyzer
                chart_type = result.get("chart_type")
                chart_data = result.get("chart_data")

                steps = result.get("steps", [])

            except Exception as e:
                answer = f"Erro: {e}"
                chart_type = None
                chart_data = None
                steps = []


        # resposta textual
        st.markdown(answer)

        #GRÁFICOS AUTOMÁTICOS (alinhado com analyzer.py)
        if chart_type and chart_data:

            import pandas as pd
            df = pd.DataFrame(chart_data)

            if chart_type == "bar":
                st.bar_chart(df.set_index(df.columns[0]))

            elif chart_type == "line":
                safe_chart(df)

            elif chart_type == "table":
                st.dataframe(df)

        #debug steps
        if steps:
            with st.expander("🔍 Ver etapas"):
                for step in steps:
                    st.json(step)

    #salva resposta
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "steps": steps
    })