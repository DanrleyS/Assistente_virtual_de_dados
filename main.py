import os
from dotenv import load_dotenv

# carrega o .env
load_dotenv()

from app.graph.workflow import build_graph


def run_chat():
    graph = build_graph()

    print("\n🤖 Assistente de Dados iniciado!")
    print("Digite sua pergunta ou 'sair'\n")

    while True:
        question = input("Você: ")

        if question.lower() in ["sair", "exit", "quit"]:
            print("Encerrando...")
            break

        state = {
            "question": question,
            "db_path": "db/clientes_completo.db",
            "attempts": 0,
            "max_attempts": 3,
            "steps": []
        }

        result = graph.invoke(state)

        print("\n📊 Resposta:")
        print(result.get("final_answer", "Sem resposta"))

        print("\n🔍 Etapas:")
        for step in result["steps"]:
            print(step)

        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    run_chat()