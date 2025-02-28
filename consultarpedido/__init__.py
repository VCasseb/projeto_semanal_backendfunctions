import logging
import pymssql
import json
from datetime import datetime
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Função consultarpedido iniciada.")

    # Configuração de conexão com pymssql
    server = "serverprojetomensales.database.windows.net"
    database = "projetomensalesdatabase"
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

        # Processa os resultados
        pedidos = [
            {
                "id": row["id"],
                "cliente": row["cliente"],
                "email": row["email"],
                "itens": json.loads(row["itens"]),
                "total": float(row["total"]),
                "status": row["status"],
                "data_criacao": row["data_criacao"].isoformat(),
                "data_atualizacao": row["data_atualizacao"].isoformat()
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
        logging.error(f"Erro na função consultarpedido: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
