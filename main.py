from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI(
    title="API de Analise de Dados"
)

# Importacao do CORSMiddleware para permitir requisições de qualquer origem e portas diferentes 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota GET (/) para verificar se a API está rodando corretamente
@app.get("/")
async def root():
    return FileResponse("index.html")

# Rota POST (/api/processar-dados) para processar o arquivo CSV enviado pelo usuário, com filtros opcionais
@app.post("/api/processar-dados")
async def processar_dados(
    file: UploadFile = File(...),
    tipo_filtro: str = Form(...),
    coluna: str = Form(None),
    valor: str = Form(None)
):
    if not file.filename.endswith('.csv'): # Se o arquivo nao finalizar em .csv, retorna um erro
        raise HTTPException(status_code=400, detail="Envie um arquivo CSV.")

    try:
        conteudo = await file.read() # Le o arquivo CSV enviado pelo usuário
        df = pd.read_csv(io.StringIO(conteudo.decode('utf-8'))) # Converte o conteúdo do arquivo para utf-8 e depois para um DataFrame do pandas

        # Aplica o filtro genérico escolhido pelo usuário
        if tipo_filtro == "remover_nulos":
            df = df.dropna() # Remove as linhas que contêm valores nulos (NaN) do DataFrame
            
        elif tipo_filtro == "remover_duplicatas":
            df = df.drop_duplicates() # Remove as linhas duplicadas do DataFrame, mantendo apenas a primeira ocorrência de cada linha duplicada
            
        elif tipo_filtro == "filtro_exato": # Aplica um filtro exato com base na coluna e valor fornecidos pelo usuário
            if coluna and valor and coluna in df.columns: # Verifica se a coluna e o valor foram fornecidos e se a coluna existe no DataFrame
                df = df[df[coluna].astype(str) == valor] 
            else: # Se nao for fornecido ou a coluna nao existir, retorna um erro
                raise HTTPException(status_code=400, detail="Coluna ou valor inválido para o filtro.")

        # Converte o DataFrame modificado de volta para texto CSV
        stream = io.StringIO()
        df.to_csv(stream, index=False) 
        response_bytes = stream.getvalue().encode('utf-8')
        
        # Envia o arquivo para o navegador como um anexo para download
        nome_arquivo_saida = f"modificado_{file.filename}"
        return StreamingResponse(
            io.BytesIO(response_bytes), 
            media_type="text/csv", 
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo_saida}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))