from langchain_openai import ChatOpenAI
import sqlite3
import re

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

MAX_ATTEMPTS = 3


def clean_sql(query: str) -> str:
    query = query.replace("```sql", "").replace("```", "")

    if ";" in query:
        query = query.split(";")[0] + ";"

    query = re.sub(r"\*\*.*", "", query, flags=re.DOTALL)

    return query.strip()


def remove_date_filters(query: str) -> str:
    # remove filtros de data STRFTIME
    query = re.sub(r"AND\s*STRFTIME\([^)]+\)\s*=\s*'[^']+'", "", query, flags=re.IGNORECASE)
    query = re.sub(r"STRFTIME\([^)]+\)\s*=\s*'[^']+'\s*AND", "", query, flags=re.IGNORECASE)
    return query


def relax_filters(query: str, attempt: int) -> str:
    """
    Estratégia progressiva:
    tentativa 1 → remove filtros de data
    tentativa 2 → remove TODOS os filtros (WHERE)
    """

    if attempt == 1:
        return remove_date_filters(query)

    if attempt >= 2:
        # remove WHERE inteiro
        return re.sub(r"WHERE\s+.*?(GROUP BY|ORDER BY|LIMIT)", r"\1", query, flags=re.IGNORECASE | re.DOTALL)

    return query


def get_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    ).fetchall()

    schema = "Tabelas disponíveis:\n\n"

    for table in tables:
        table_name = table[0]
        columns = cursor.execute(f"PRAGMA table_info({table_name});").fetchall()
        col_names = [col[1] for col in columns]

        schema += f"{table_name}({', '.join(col_names)})\n"

    conn.close()
    return schema


def error_handler_node(state):
    error = state.get("error")
    query = state["sql_query"]
    db_path = state["db_path"]
    empty = state.get("empty_result", False)

    state["attempts"] = state.get("attempts", 0) + 1
    attempt = state["attempts"]

    if attempt >= MAX_ATTEMPTS:
        state["force_finish"] = True

        state["steps"].append({
            "step": "error_handler",
            "status": "max_attempts_reached",
            "error": error,
            "attempts": attempt
        })

        return state

    #CASO 1: EMPTY RESULT → lógica determinística (SEM LLM)
    if empty:
        new_query = relax_filters(query, attempt)

        state["sql_query"] = clean_sql(new_query)

        state["steps"].append({
            "step": "error_handler",
            "strategy": "relax_filters",
            "fixed_query": state["sql_query"],
            "attempt": attempt
        })

        return state

    #CASO 2: ERRO REAL → usa LLM
    schema = get_schema(db_path)

    prompt = f"""
        Você é um especialista em SQL.

        Corrija a query abaixo.

        IMPORTANTE:
        - Retorne APENAS SQL
        - NÃO explique nada
        - NÃO use markdown

        Query:
        {query}

        Erro:
        {error}

        Schema:
        {schema}
        """

    response = llm.invoke(prompt).content
    fixed_query = clean_sql(response)

    state["sql_query"] = fixed_query

    state["steps"].append({
        "step": "error_handler",
        "strategy": "llm_fix",
        "fixed_query": fixed_query,
        "attempt": attempt
    })

    return state