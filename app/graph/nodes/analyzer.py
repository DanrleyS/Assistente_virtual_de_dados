def analyzer_node(state):
    df = state.get("sql_result")

    if df is None:
        state["analysis"] = "Erro na execução da query."
        return state

    if df.empty:
        state["analysis"] = "Consulta sem resultados."
        state["chart_type"] = "none"
        state["chart_data"] = []
        return state

    columns = [col.lower() for col in df.columns]

    if any("data" in c or "mes" in c or "ano" in c for c in columns):
        chart_type = "line"
    elif len(df.columns) == 2:
        chart_type = "bar"
    else:
        chart_type = "table"

    state["analysis"] = df.to_string(index=False)
    state["chart_type"] = chart_type
    state["chart_data"] = df.to_dict(orient="records")

    return state