# 📊 Assistente de Dados com IA (SQL + LangGraph)

Este projeto é um **assistente inteligente de análise de dados**, capaz de interpretar perguntas em linguagem natural, gerar queries SQL automaticamente, executar no banco de dados e retornar respostas estruturadas com possibilidade de visualização gráfica.

---

# 🚀 Como Executar

## 1. Clonar o projeto
```bash
git clone <http://github.com/DanrleyS/Assistente_virtual_de_dados>
cd <Assistente_virtual_de_dados>
2. Criar ambiente virtual (opcional, recomendado)
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
3. Instalar dependências
pip install -r requirements.txt
4. Configurar variáveis de ambiente

Crie um arquivo .env na raiz do projeto com:

OPENAI_API_KEY=sua_chave_aqui

⚠️ Importante:
Você precisa de uma chave da OpenAI para que o sistema funcione corretamente.

5. Executar o projeto
python execute.py

✅ Isso automaticamente:
entra na pasta frontend
inicia o Streamlit
abre a interface do assistente

🧠 Arquitetura do Sistema

O projeto utiliza uma arquitetura baseada em agentes encadeados (LangGraph), onde cada etapa do processamento é um nó independente.

🔄 Fluxo de execução
Usuário → Planner → SQL Generator → Executor
                         ↓
                 Error Handler (loop)
                         ↓
                    Analyzer → Responder → Final

📌 Descrição dos agentes
1. Planner
Interpreta a pergunta do usuário
Define estratégia (tabelas, filtros, agregações)
NÃO gera SQL ainda

2. SQL Generator
Converte o plano em SQL válida
Usa o schema real do banco
Evita invenções (tabelas/colunas inexistentes)

3. Executor
Executa a query no SQLite
Retorna:
DataFrame
erro (se houver)
flag de resultado vazio

4. Error Handler
Atua em dois cenários:
🔹 Erro de execução:
Usa LLM para corrigir SQL
🔹 Resultado vazio:
Relaxa filtros automaticamente:
remove filtros de data
remove WHERE completamente

5. Analyzer
Analisa o resultado
Define tipo de saída:
gráfico de linha
gráfico de barras
tabela

6. Responder
Gera resposta em linguagem natural
Baseado exclusivamente nos dados retornados
Sem inventar informações


📊 Interface

A interface foi construída com Streamlit e permite:

Chat interativo
Visualização de gráficos automática
Debug completo das etapas (steps)
Histórico de conversas

🧪 Exemplos de Consultas

Aqui estão alguns exemplos testados:

📌 Consultas simples
"Quantos clientes existem?"
"Liste todos os estados dos clientes"

📌 Consultas com filtro
"Quantos clientes compraram em maio?"
"Clientes cadastrados em 2024"

📌 Consultas analíticas
"Liste os 5 estados com maior número de clientes"
"Qual estado tem mais compras?"

📌 Consultas com agregação
"Total de compras por estado"
"Média de compras por cliente"

📌 Consultas temporais
"Compras no último ano"
"Clientes por mês"

⚙️ Tecnologias Utilizadas
Python
LangGraph
LangChain
OpenAI API
SQLite
Pandas
Streamlit

📁 Estrutura do Projeto
app/
 ├── graph/
 │   ├── nodes/
 │   ├── workflow.py
 │   └── schema_reader.py
frontend/
 └── streamlit_app.py
db/
 └── clientes_completo.db
tools/
 └── sql_tool.py
execute.py
main.py

🔧 Sugestões de Melhorias

🔥 Curto prazo
Cache de queries para reduzir custo de LLM
Melhor tratamento de erros SQL
Logs estruturados
camada semântica
dicionário de métricas
ou feature store

🚀 Médio prazo
Upload de CSV pelo usuário
Suporte a múltiplos bancos
Autenticação de usuários

🧠 Avançado
Fine-tuning do planner
RAG com documentação do banco
Memória de contexto entre perguntas
Suporte a múltiplos usuários (multi-tenant)

📊 Visualização
Gráficos interativos (Plotly)
Exportação de resultados (CSV/Excel)
Dashboard automático

🏁 Conclusão
Este projeto demonstra uma abordagem moderna para análise de dados usando IA, combinando:

geração automática de SQL
execução segura
tratamento inteligente de erros
interface amigável

Tudo isso com uma arquitetura modular e escalável.

👨‍💻 Autor

Desenvolvido por Danrley Silva
