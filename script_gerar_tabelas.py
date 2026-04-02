import sqlite3
import csv

# Nome do banco
db_name = "db/clientes_completo.db"

# Conectar ao banco
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Lista de tabelas (incluindo sqlite_sequence)
tabelas = ["clientes", "compras", "suporte", "campanhas_marketing", "sqlite_sequence"]

for tabela in tabelas:
    print(f"Exportando tabela: {tabela}")
    
    try:
        # Consulta
        cursor.execute(f"SELECT * FROM {tabela} LIMIT 5")
        
        # Nome das colunas
        colunas = [description[0] for description in cursor.description]
        
        # Dados
        linhas = cursor.fetchall()
        
        # Nome do arquivo CSV
        nome_arquivo = f"{tabela}.csv"
        
        # Escrever CSV
        with open(nome_arquivo, mode="w", newline="", encoding="utf-8") as arquivo:
            writer = csv.writer(arquivo)
            
            # Cabeçalho
            writer.writerow(colunas)
            
            # Dados
            writer.writerows(linhas)
    
    except Exception as e:
        print(f"Erro ao processar {tabela}: {e}")

# Fechar conexão
conn.close()

print("Exportação concluída!")