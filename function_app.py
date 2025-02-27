import logging
import pyodbc
import os
import json
import uuid
from datetime import datetime
import azure.functions as func
import msal

app = func.FunctionApp()

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

@app.route(route="pedidos", auth_level=func.AuthLevel.FUNCTION)
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Obter a string de conexão
    connection_string = os.getenv("SQLConnectionString")

    try:
        # Ler o corpo da requisição
        req_body = req.get_json()

        # Extrair dados do pedido
        cliente = req_body.get('cliente')
        email = req_body.get('email')
        itens = req_body.get('itens')

        print(cliente)
        print(email)
        print(itens)

        # Calcular o total do pedido
        total = sum(item['quantidade'] * item['preco'] for item in itens)

        # Gerar um ID único para o pedido
        pedido_id = str(uuid.uuid4())
        status = "PENDENTE"
        data_criacao = datetime.utcnow().isoformat() + "Z"

        # Conectar ao SQL Server
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Inserir o pedido no banco de dados
        cursor.execute("""
            INSERT INTO Pedidos (Id, Cliente, Email, Status, Total, DataCriacao)
            VALUES (?, ?, ?, ?, ?, ?)
        """, pedido_id, cliente, email, status, total, data_criacao)

        # Inserir os itens do pedido
        for item in itens:
            cursor.execute("""
                INSERT INTO ItensPedido (PedidoId, Produto, Quantidade, Preco)
                VALUES (?, ?, ?, ?)
            """, pedido_id, item['produto'], item['quantidade'], item['preco'])

        # Commit da transação
        conn.commit()

        # Fechar a conexão
        cursor.close()
        conn.close()

        # Retornar a resposta
        response = {
            "id": pedido_id,
            "status": status,
            "total": total,
            "data_criacao": data_criacao
        }

        return func.HttpResponse(json.dumps(response), status_code=201, mimetype="application/json")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

# Configurações do Azure AD e SQL Server
SERVER='tcp:serverdatabasesemanal.database.windows.net,1433;Initial Catalog=sqldatabaseprojetosemanal;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;Authentication="Active Directory Default"'
DATABASE = "sqldatabaseprojetosemanal"
TENANT_ID = "SEU_TENANT_ID"  # Substituir pelo Tenant ID do Azure
CLIENT_ID = "SEU_CLIENT_ID"  # Substituir pelo Client ID da aplicação no Azure AD
CLIENT_SECRET = "SEU_CLIENT_SECRET"  # Chave do app registrada no Azure AD

@app.route(route="consultarpedidos", auth_level=func.AuthLevel.FUNCTION)
def consultarpedidos(req: func.HttpRequest) -> func.HttpResponse:
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

        # Processa os resultados
        for row in rows:
            print(row)

        # Fecha a conexão
        cursor.close()
        conn.close()

        return "Consulta executada com sucesso!"
    except Exception as e:
        return f"Erro: {str(e)}"