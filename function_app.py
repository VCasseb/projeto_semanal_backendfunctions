import logging
import pyodbc
import os
import json
import uuid
from datetime import datetime
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
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

        # Processa os resultados
        for row in rows:
            print(row)

        # Fecha a conexão
        cursor.close()
        conn.close()

        return "Consulta executada com sucesso!"
    except Exception as e:
        return f"Erro: {str(e)}"
    

@app.route(route="inserirpedido")
def inserirpedido(req: func.HttpRequest) -> func.HttpResponse:
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


@app.route(route="consultarumpedido")
def consultarumpedido(req: func.HttpRequest) -> func.HttpResponse:
    try:
        pedido_id = req.params.get("id")
        if not pedido_id:
            return func.HttpResponse("ID do pedido é obrigatório!", status_code=400)

        print(pedido_id)

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

        # Consulta o pedido específico
        cursor.execute("SELECT id, cliente, email, itens, total, status, data_criacao, data_atualizacao FROM Pedidos WHERE id = ?", pedido_id)
        row = cursor.fetchone()
        
        if not row:
            return func.HttpResponse("Pedido não encontrado!", status_code=404)

        # Formata a resposta
        pedido = {
            "id": row[0],
            "cliente": row[1],
            "email": row[2],
            "itens": json.loads(row[3]),
            "total": float(row[4]),  # Converte Decimal para float
            "status": row[5],
            "data_criacao": row[6].isoformat(),
            "data_atualizacao": row[7].isoformat()
        }
        
        # Fecha a conexão
        cursor.close()
        conn.close()
        
        return func.HttpResponse(json.dumps(pedido), status_code=200, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(f"Erro ao obter pedido: {str(e)}", status_code=500)

@app.route(route="atualizarstatus")
def atualizarstatus(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        pedido_id = req_body.get("id")
        novo_status = req_body.get("status")
        
        if not pedido_id or not novo_status:
            return func.HttpResponse("ID do pedido e novo status são obrigatórios!", status_code=400)

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

        # Atualiza o status do pedido
        cursor.execute(
            "UPDATE Pedidos SET status = ?, data_atualizacao = ? WHERE id = ?",
            (novo_status, datetime.utcnow(), pedido_id)
        )

        # Confirma a transação
        conn.commit()
        
        # Fecha a conexão
        cursor.close()
        conn.close()
        
        return func.HttpResponse("Status do pedido atualizado com sucesso!", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Erro ao atualizar status do pedido: {str(e)}", status_code=500)


@app.route(route="deletarpedido")
def deletarpedido(req: func.HttpRequest) -> func.HttpResponse:
    try:
        pedido_id = req.params.get("id")
        if not pedido_id:
            return func.HttpResponse("ID do pedido é obrigatório!", status_code=400)

        print(pedido_id)

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

        # Executa o comando DELETE
        cursor.execute("DELETE FROM Pedidos WHERE id = ?", pedido_id)

        # Confirma a transação
        conn.commit()

        # Verifica quantas linhas foram afetadas
        if cursor.rowcount == 0:
            return func.HttpResponse("Pedido não encontrado!", status_code=404)

        # Fecha a conexão
        cursor.close()
        conn.close()
        
        return func.HttpResponse(json.dumps(f"Pedido {pedido_id} deletado com sucesso!"), status_code=200, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(f"Erro ao obter pedido: {str(e)}", status_code=500)