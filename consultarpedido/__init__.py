import logging
import pyodbc
import json
from datetime import datetime
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Função consultarpedido iniciada.")

    # String de conexão
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=tcp:serverprojetomensales.database.windows.net,1433;"
        "DATABASE=projetomensalesdatabase;"
        "UID=vccasseb;"
        "PWD=Lala3500@99;"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    try:
        logging.info("Conectando ao banco de dados...")
        conn = pyodbc.connect(conn_str)
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
                "id": row.id,
                "cliente": row.cliente,
                "email": row.email,
                "itens": json.loads(row.itens),
                "total": float(row.total),
                "status": row.status,
                "data_criacao": row.data_criacao.isoformat(),
                "data_atualizacao": row.data_atualizacao.isoformat()
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
        logging.error(f"Erro na função consultarpedido: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )