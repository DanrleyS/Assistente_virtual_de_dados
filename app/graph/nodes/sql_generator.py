from langchain_openai import ChatOpenAI
import sqlite3
import re
from app.graph.schema_reader import get_schema

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def enforce_case_insensitive(sql: str) -> str:
    pattern = r"(\b\w+\b)\s*=\s*'([^']+)'"

    def repl(match):
        col = match.group(1)
        val = match.group(2)

        if val.isdigit() or "-" in val:
            return match.group(0)

        return f"LOWER({col}) = '{val.lower()}'"

    return re.sub(pattern, repl, sql)


def clean_sql(sql: str) -> str:
    return sql.replace("```sql", "").replace("```", "").strip()


def fix_count_query(sql: str):
    """
    Corrige queries do tipo:
    SELECT cliente_id, COUNT(*) → SELECT COUNT(DISTINCT cliente_id)
    """

    # tenta encontrar coluna principal
    match = re.search(r"select\s+(.*?)\s*,\s*count", sql.lower())
    if match:
        col = match.group(1).strip()
        # remove coluna e mantém apenas COUNT DISTINCT
        sql_fixed = re.sub(
            r"select\s+.*?,\s*count\(\*\)",
            f"SELECT COUNT(DISTINCT {col})",
            sql,
            flags=re.IGNORECASE
        )

        return sql_fixed

    # fallback seguro
    return re.sub(
        r"select\s+.*?count\(\*\)",
        "SELECT COUNT(*)",
        sql,
        flags=re.IGNORECASE
    )

def validate_sql(sql: str):
    sql_lower = sql.lower()

    has_agg = any(func in sql_lower for func in ["count(", "sum(", "avg("])
    has_group = "group by" in sql_lower

    select_part = sql_lower.split("from")[0]
    select_clean = re.sub(r"(count|sum|avg)\s*\(.*?\)", "", select_part)

    remaining = [
        col.strip()
        for col in select_clean.replace("select", "").split(",")
        if col.strip()
    ]

    has_non_agg_column = len(remaining) > 0

    #Caso inválido
    if has_agg and has_non_agg_column and not has_group:
        #TENTA CORRIGIR AUTOMATICAMENTE
        if "count(" in sql_lower:
            return fix_count_query(sql)

        raise ValueError("SQL inválida: agregação com coluna não agregada sem GROUP BY")

    return sql

def sql_generator_node(state):
    question = state["question"]
    plan = state["plan"]
    db_path = state["db_path"]
    schema = get_schema(db_path)

    previous_error = state.get("error", "")

    prompt = f"""
        Você é um especialista em SQL (SQLite).

        SCHEMA:
        {schema}

        PLANO:
        {plan}

        REGRAS CRÍTICAS:
        - NÃO usar tabelas fora do schema
        - NÃO usar colunas inexistentes
        - VALIDAR tudo contra schema antes de gerar
        - Se algo do plano for inválido → IGNORE essa parte

        - Quando a pergunta envolver "todos", "cada", "por estado", "por categoria":
            → É OBRIGATÓRIO usar GROUP BY
        - Quando a pergunta pedir "qual tem mais":
            → Deve calcular TODOS os grupos primeiro
            → Depois ordenar com ORDER BY DESC
        - NUNCA filtrar um valor específico (WHERE estado = ...) quando a pergunta pede comparação entre múltiplos valores
        - NÃO inventar joins
        - Só usar joins por chave:
            cliente_id

        REGRAS DE DATA:
        - "maio" → STRFTIME('%m', data) = '05'
        - "2024" → STRFTIME('%Y', data) = '2024'
        - "último ano" → DATE('now', '-1 year')

        REGRAS DE AGREGAÇÃO (OBRIGATÓRIO):
        - Se usar COUNT, SUM ou AVG com coluna categórica → usar GROUP BY
        - Nunca usar agregação sem GROUP BY quando houver categoria

        REGRAS DE ORDENAÇÃO:
        - "maior", "top", "mais" → ORDER BY ... DESC
        - "menor" → ORDER BY ... ASC
        - Sempre usar LIMIT quando pedir top N

        ERRO ANTERIOR:
        {previous_error}

        Pergunta:
        {question}

        Retorne apenas SQL válida.
        """

    response = llm.invoke(prompt).content
    sql_query = clean_sql(response)
    sql_query = enforce_case_insensitive(sql_query)
    sql_query = validate_sql(sql_query)

    state["sql_query"] = sql_query

    state["steps"].append({
        "step": "sql_generator",
        "query": sql_query
    })

    return state