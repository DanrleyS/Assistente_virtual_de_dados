from tools.sql_tool import SQLTool
import re


def sanitize_query(query: str) -> str:
    # remove markdown
    query = query.replace("```sql", "").replace("```", "")

    # mantém só primeira query
    if ";" in query:
        query = query.split(";")[0] + ";"

    # bloqueia lixo do LLM
    forbidden_patterns = [
        r"\*\*",          # markdown
        r"Correções",     # texto explicativo
        r"Explicação",
        r"Passos",
    ]

    for pattern in forbidden_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            raise ValueError("Query contém texto inválido do LLM")

    return query.strip()


def executor_node(state):
    query = state["sql_query"]

    try:
        query = sanitize_query(query)

    except Exception as e:
        state["sql_result"] = None
        state["error"] = str(e)
        state["empty_result"] = False

        state["steps"].append({
            "step": "executor",
            "status": "error",
            "error": f"Sanitização falhou: {str(e)}"
        })

        return state

    tool = SQLTool(state["db_path"])
    result = tool.run(query)

    if result["success"]:
        df = result["data"]

        state["sql_result"] = df
        state["error"] = None
        state["empty_result"] = df.empty

        state["steps"].append({
            "step": "executor",
            "status": "success",
            "rows": len(df),
            "empty": df.empty
        })

    else:
        state["sql_result"] = None
        state["error"] = result["error"]
        state["empty_result"] = False

        state["steps"].append({
            "step": "executor",
            "status": "error",
            "error": result["error"]
        })

    return state