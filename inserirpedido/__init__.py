import logging
import pyodbc
import os
import json
import uuid
from datetime import datetime
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Obtém os dados do corpo da requisição
        req_body = req.get_json()
        pedido_id = str(uuid.uuid4())  # Gera um UUID único
        cliente = req_body.get("cliente")
        email = req_body.get("email")
        itens = json.dumps(req_body.get("itens", []))  # Converte a lista de itens para JSON
        total = req_body.get("total")
        status = req_body.get("status")
        data_criacao = datetime.utcnow()
        data_atualizacao = datetime.utcnow()
        
        if not all([cliente, email, total, status]):
            return func.HttpResponse("Campos obrigatórios ausentes!", status_code=400)

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

        # Conecta ao banco de dados
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Insere o pedido na tabela
        cursor.execute(
            """
            INSERT INTO Pedidos (id, cliente, email, itens, total, status, data_criacao, data_atualizacao) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (pedido_id, cliente, email, itens, total, status, data_criacao, data_atualizacao)
        )

        # Confirma a transação
        conn.commit()
        
        # Fecha a conexão
        cursor.close()
        conn.close()
        
        return func.HttpResponse("Pedido inserido com sucesso!", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Erro ao inserir pedido: {str(e)}", status_code=500)