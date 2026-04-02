import os
import sys

#CONFIGURAÇÃO
PORT = 8501  # ← altere aqui quando quiser

# entra na pasta frontend
os.chdir("frontend")

# executa o streamlit com porta
os.system(f"{sys.executable} -m streamlit run streamlit_app.py --server.port {PORT}")