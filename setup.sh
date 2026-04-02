#!/bin/bash

# Nome da pasta raiz
PROJECT_NAME="project"

# Criar diretórios
mkdir -p $PROJECT_NAME/app/graph/nodes
mkdir -p $PROJECT_NAME/tools
mkdir -p $PROJECT_NAME/db
mkdir -p $PROJECT_NAME/frontend

# Criar arquivos
touch $PROJECT_NAME/app/graph/workflow.py
touch $PROJECT_NAME/app/graph/schema_reader.py

touch $PROJECT_NAME/app/graph/nodes/planner.py
touch $PROJECT_NAME/app/graph/nodes/sql_generator.py
touch $PROJECT_NAME/app/graph/nodes/executor.py
touch $PROJECT_NAME/app/graph/nodes/error_handler.py
touch $PROJECT_NAME/app/graph/nodes/analyzer.py
touch $PROJECT_NAME/app/graph/nodes/responder.py

touch $PROJECT_NAME/tools/sql_tool.py

touch $PROJECT_NAME/db/clientes_completo.db

touch $PROJECT_NAME/frontend/streamlit_app.py

touch $PROJECT_NAME/README.md

echo "Estrutura do projeto criada com sucesso!"