import logging
import pyodbc
import os
import json
import uuid
from datetime import datetime
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="consultarpedido")
def consultarpedido(req: func.HttpRequest) -> func.HttpResponse:
    # String de conexão (substitua pelos seus dados)
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
        # Conecta ao banco de dados
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Executa uma consulta
        cursor.execute("SELECT * FROM Pedidos")
        rows = cursor.fetchall()

        # Processa os resultados para um formato JSON
        pedidos = []
        for row in rows:
            pedido = {
                "id": row.id,
                "cliente": row.cliente,
                "email": row.email,
                "itens": json.loads(row.itens),  # Converte a string JSON para um objeto Python
                "total": float(row.total),  # Converte Decimal para float
                "status": row.status,
                "data_criacao": row.data_criacao.isoformat(),  # Converte datetime para string
                "data_atualizacao": row.data_atualizacao.isoformat()
            }
            pedidos.append(pedido)

        # Fecha a conexão
        cursor.close()
        conn.close()

        # Retorna os pedidos em formato JSON
        return func.HttpResponse(
            json.dumps(pedidos),  # Converte a lista de pedidos para JSON
            status_code=200,
            mimetype="application/json"  # Define o tipo de conteúdo como JSON
        )

    except Exception as e:
        # Retorna uma mensagem de erro em formato JSON
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )