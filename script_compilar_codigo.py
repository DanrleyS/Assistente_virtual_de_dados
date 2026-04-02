import os

# Usa automaticamente a pasta do script
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = "codigo_completo.md"

# Pastas a ignorar
IGNORAR_PASTAS = {
    "venv",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode"
}

# Arquivos específicos a ignorar
IGNORAR_ARQUIVOS = {
    ".env"
}

# Extensões permitidas (somente código relevante)
EXTENSOES_PERMITIDAS = {
    ".py",
#    ".js",
#    ".ts",
#    ".html",
#    ".css",
#    ".json",
#    ".md",
#    ".sh"
}

def linguagem_markdown(ext):
    mapa = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".md": "markdown",
        ".sh": "bash"
    }
    return mapa.get(ext, "")

def coletar_arquivos(base_dir):
    arquivos = []

    for root, dirs, files in os.walk(base_dir):
        # remove pastas indesejadas
        dirs[:] = [d for d in dirs if d not in IGNORAR_PASTAS]

        for file in files:
            # ignora arquivos específicos
            if file in IGNORAR_ARQUIVOS:
                continue

            ext = os.path.splitext(file)[1]

            # só pega extensões permitidas
            if ext not in EXTENSOES_PERMITIDAS:
                continue

            caminho = os.path.join(root, file)
            arquivos.append(caminho)

    return arquivos

def gerar_markdown(arquivos, output_file):
    with open(output_file, "w", encoding="utf-8") as md:
        for caminho in sorted(arquivos):
            nome = os.path.relpath(caminho, PROJECT_DIR)
            ext = os.path.splitext(caminho)[1]

            md.write(f"## {nome}\n\n")

            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
            except Exception as e:
                conteudo = f"Erro ao ler arquivo: {e}"

            lang = linguagem_markdown(ext)

            md.write(f"```{lang}\n")
            md.write(conteudo)
            md.write("\n```\n\n")

    print(f"Markdown gerado em: {output_file}")
    print(f"Total de arquivos incluídos: {len(arquivos)}")

if __name__ == "__main__":
    arquivos = coletar_arquivos(PROJECT_DIR)
    gerar_markdown(arquivos, OUTPUT_FILE)