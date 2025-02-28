import logging
import pyodbc
import json
from datetime import datetime
import azure.functions as func
import uuid  # Import necessário para verificar UUIDs

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Função consultarpedido iniciada.")

    # Configuração de conexão com pyodbc
    server = "serversqldatabasesemanal.database.windows.net"
    database = "databasesqlsemanal"
    username = "vccasseb"
    password = "Lala3500@99"
    driver = "{ODBC Driver 17 for SQL Server}"  # Certifique-se de que o driver está instalado

    # String de conexão
    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    try:
        logging.info("Conectando ao banco de dados...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        logging.info("Conexão bem-sucedida!")

        logging.info("Executando consulta...")
        cursor.execute("SELECT * FROM Pedidos")
        rows = cursor.fetchall()
        logging.info(f"Consulta retornou {len(rows)} registros.")

        # Processa os resultados
        pedidos = []
        for row in rows:
            pedido = {
                "Id": str(row.Id) if isinstance(row.Id, uuid.UUID) else row.Id,  # Converte UUID para string
                "Cliente": row.Cliente,
                "Email": row.Email,
                "Itens": json.loads(row.Itens),
                "Total": float(row.Total),
                "Status": row.Status,
                "DataCriacao": row.DataCriacao.isoformat(),
                "DataAtualiza": row.DataAtualiza.isoformat()
            }
            pedidos.append(pedido)

        # Fecha a conexão
        cursor.close()
        conn.close()

        # Retorna os pedidos em formato JSON
        return func.HttpResponse(
            json.dumps(pedidos),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error("Erro na função consultarpedido", exc_info=True)  # Captura traceback completo
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )