from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def responder_node(state):
    df = state.get("sql_result")
    error = state.get("error")
    question = state["question"]

    if error:
        answer = f"Erro ao executar consulta: {error}"

    else:
        data_text = df.to_string(index=False)

        prompt = f"""
            Você é um analista de dados.

            RESPONDA usando SOMENTE os dados abaixo.

            PROIBIDO:
            - Inferir
            - Generalizar
            - Inventar explicações

            PERMITIDO:
            - Reescrever os números claramente
            - Destacar o maior/menor SE VISÍVEL

            Pergunta:
            {question}

            Dados:
            {data_text}

            Responda em português claro e direto.
            """

        answer = llm.invoke(prompt).content

    state["final_answer"] = answer
    return state