from langchain_openai import ChatOpenAI
from app.graph.schema_reader import get_schema

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def planner_node(state):
    question = state["question"]
    db_path = state["db_path"]

    schema = get_schema(db_path)

    prompt = f"""
        Você é um analista de dados especialista em SQL.

        SCHEMA REAL DO BANCO:
        {schema}

        REGRRA CRÍTICA:
        - Use APENAS tabelas e colunas do schema acima
        - Se algo não existir → NÃO INVENTAR

        REGRAS:
        - NÃO invente tabelas
        - NÃO invente colunas
        - NÃO invente joins
        - NÃO invente filtros
        - Se não tiver certeza → deixe vazio

        REGRAS DE INTERPRETAÇÃO CRÍTICAS:
        - "listar todos os estados" → SELECT DISTINCT estado
        - "estado com mais clientes" → COUNT + GROUP BY estado + ORDER BY DESC
        - Se a pergunta combinar listagem + ranking → fazer ambos na mesma query

        INTERPRETAÇÃO:
        - "em maio" → mês = 05
        - "em 2024" → ano = 2024
        - "último ano" → usar MAX(data)

        FORMATO:

        - tabelas:
        - joins:
        - filtros:
        - agregação:
        - ordenação:

        Pergunta:
        {question}
        """

    plan = llm.invoke(prompt).content

    state["plan"] = plan
    state["steps"].append({"step": "planner", "output": plan})

    return state