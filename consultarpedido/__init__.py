import logging
import pymssql
import json
from datetime import datetime
import azure.functions as func
import uuid  # Import necessário para verificar UUIDs

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Função consultarpedido iniciada.")

    # Configuração de conexão com pymssql
    server = "serversqldatabasesemanal.database.windows.net"
    database = "databasesqlsemanal"
    username = "vccasseb"
    password = "Lala3500@99"


    try:
        logging.info("Conectando ao banco de dados...")
        conn = pymssql.connect(server, username, password, database)
        cursor = conn.cursor(as_dict=True)  # Retorna os resultados como dicionários
        logging.info("Conexão bem-sucedida!")

        logging.info("Executando consulta...")
        cursor.execute("SELECT * FROM Pedidos")
        rows = cursor.fetchall()
        logging.info(f"Consulta retornou {len(rows)} registros.")

        
        for row in rows:
            print("Linha retornada",rows)

        # Processa os resultados
        pedidos = [
            {
                "Id": str(row["Id"]) if isinstance(row["Id"], uuid.UUID) else row["Id"],  # Converte UUID para string
                "Cliente": row["Cliente"],
                "Email": row["Email"],
                "Itens": json.loads(row["Itens"]),
                "Total": float(row["Total"]),
                "Status": row["Status"],
                "DataCriacao": row["DataCriacao"].isoformat(),
                "DataAtualiza": row["DataAtualiza"].isoformat()
            }
            for row in rows
        ]

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
