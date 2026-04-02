from langgraph.graph import StateGraph, END

from app.graph.nodes.planner import planner_node
from app.graph.nodes.sql_generator import sql_generator_node
from app.graph.nodes.executor import executor_node
from app.graph.nodes.error_handler import error_handler_node
from app.graph.nodes.analyzer import analyzer_node
from app.graph.nodes.responder import responder_node


def should_retry(state):
    """
    Retry quando:
    - houve erro de execução
    - OU query retornou vazia (erro lógico)
    - E ainda não atingiu o limite de tentativas
    """
    return (
        (
            state.get("error") is not None
            or state.get("empty_result", False)
        )
        and state.get("attempts", 0) < state.get("max_attempts", 3)
    )


def should_fail(state):
    """
    Falha definitiva quando:
    - erro OU resultado vazio
    - E já atingiu limite de tentativas
    """
    return (
        (
            state.get("error") is not None
            or state.get("empty_result", False)
        )
        and state.get("attempts", 0) >= state.get("max_attempts", 3)
    )


def build_graph():

    graph = StateGraph(dict)

    # Nodes
    graph.add_node("planner", planner_node)
    graph.add_node("sql_generator", sql_generator_node)
    graph.add_node("executor", executor_node)
    graph.add_node("error_handler", error_handler_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("responder", responder_node)

    # Entry
    graph.set_entry_point("planner")

    # Fluxo principal
    graph.add_edge("planner", "sql_generator")
    graph.add_edge("sql_generator", "executor")

    # Decisão após execução
    graph.add_conditional_edges(
        "executor",
        lambda state: (
            "retry"
            if should_retry(state)
            else ("fail" if should_fail(state) else "success")
        ),
        {
            "retry": "error_handler",
            "fail": "responder",
            "success": "analyzer",
        }
    )

    # Loop de correção
    graph.add_edge("error_handler", "executor")

    # Finalização
    graph.add_edge("analyzer", "responder")
    graph.add_edge("responder", END)

    return graph.compile()