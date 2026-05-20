from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import io

app = FastAPI(
    title="API de Analise de Dados",
    description="API para upload e processamento de arquivos CSV"
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
async def processar_dados( #Cria a funcao processar_dados que recebe um arquivo CSV e filtros opcionais para processar os dados
    file: UploadFile = File(...),
    coluna_filtro: str = Form(None),
    valor_filtro: str = Form(None)
):
    if not file.filename.endswith('.csv'): # Se o arquivo nao terminar com .csv
        raise HTTPException(status_code=400, detail="Arquivo deve ser do tipo CSV") #Retorna um erro 400 informando que o arquivo deve ser do tipo CSV
    
    try:
        conteudo_bytes = await file.read() # Se nao, le o conteudo do arquivo como bytes

        texto_csv = conteudo_bytes.decode('utf-8') # Decodifica os bytes para texto usando UTF-8
        df = pd.read_csv(io.StringIO(texto_csv)) # Le o texto CSV usando pandas e armazena em um DataFrame

        if coluna_filtro and valor_filtro:
            if coluna_filtro in df.columns: # Tenta verificar se a coluna de filtro existe no DataFrame
                df = df[df[coluna_filtro].astype(str) == valor_filtro] # Se sim, filtra a coluna especificada pelo valor fornecido
            else:
                raise HTTPException(status_code=400, detail=f"A coluna '{coluna_filtro}' não existe neste CSV.") # Se nao, retorna um erro 400 informando que a coluna de filtro nao existe no CSV
            
        resposta = { # Cria uma resposta
            "arquivo_processado": file.filename, # Qual arquivo foi processado
            "total_linhas_resultado": len(df), # Quantas linhas tem o resultado apos o filtro ser aplicado
            "colunas_disponiveis": list(df.columns), # Quais colunas estao disponiveis no DataFrame apos o processamento
            "dados": df.to_dict(orient='records')  # Converte o DataFrame para uma lista de dicionários
        }
        
        return resposta # Retorna a resposta com os dados processados
    
    except Exception as e: # Caso de erro durante o processamento do arquivo, captura a exceção e retorna um erro 500 com a mensagem de erro
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}")
    




