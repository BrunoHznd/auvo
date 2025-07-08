import os
import sys
import sqlite3
import requests
import pandas as pd
from datetime import datetime

# Usa os módulos de conexão já existentes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.api_auvo import autenticar
from app.env_reader import API_URL, API_KEY

# Detecta sistema operacional e define caminho do banco
if os.name == 'nt':
    DB_EQUIPAMENTOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "db.sqlite3"))
else:
    DB_EQUIPAMENTOS = "/root/auvo-git/data/db.sqlite3"

def fetch_equipamentos_auvo():
    """Busca todos os equipamentos na API da Auvo usando autenticação do projeto."""
    token = autenticar()
    if not token:
        print('Falha na autenticação com a API Auvo.')
        return []
    headers = {
        'Authorization': f'Bearer {token}',
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    url = f"{API_URL}/equipments/"
    equipamentos = []
    page = 1
    page_size = 100
    while True:
        params = {
            "page": page,
            "pageSize": page_size,
            "order": "asc"
        }
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"Erro ao buscar equipamentos: {resp.status_code}")
            break
        result = resp.json().get("result", {})
        page_items = result.get("entityList", [])
        equipamentos.extend(page_items)
        total_items = result.get("pagedSearchReturnData", {}).get("totalItems", 0)
        if len(equipamentos) >= total_items or not page_items:
            break
        page += 1
    return equipamentos

def atualizar_banco_equipamentos(equipamentos_api):
    """Atualiza a tabela equipamentos com base nos dados da API Auvo."""
    if not equipamentos_api:
        print('Nenhum equipamento recebido da API.')
        return
    conn = sqlite3.connect(DB_EQUIPAMENTOS)
    df_local = pd.read_sql('SELECT * FROM equipamentos', conn)
    # Mapeamento dos campos principais
    df_api = pd.DataFrame(equipamentos_api)
    # Renomeia para bater com o banco local
    df_api.rename(columns={
        'id': 'id',
        'name': 'name',
        'categoryId': 'tipo',
        'associatedCustomerId': 'associated_customer_id',
        'active': 'ativo',
        'identifier': 'identificador',
    }, inplace=True)
    # Ajusta campo ativo para int
    if 'ativo' in df_api.columns:
        df_api['ativo'] = df_api['ativo'].astype(int)
    # Seleciona apenas colunas do banco
    cols_banco = ['id','name','tipo','associated_customer_id','ativo','identificador']
    df_api = df_api[[col for col in cols_banco if col in df_api.columns]]
    # Atualização incremental
    for _, row in df_api.iterrows():
        equip_id = row['id']
        existe = df_local['id'].eq(equip_id).any()
        if existe:
            campos_update = ', '.join([f"{col}=?" for col in cols_banco if col != 'id'])
            valores = [row[col] for col in cols_banco if col != 'id'] + [equip_id]
            conn.execute(f"UPDATE equipamentos SET {campos_update} WHERE id=?", valores)
        else:
            campos = ', '.join(cols_banco)
            placeholders = ', '.join(['?'] * len(cols_banco))
            valores = [row.get(col) for col in cols_banco]
            conn.execute(f"INSERT INTO equipamentos ({campos}) VALUES ({placeholders})", valores)
    # Inativa equipamentos que sumiram da API
    ids_api = set(df_api['id'])
    ids_local = set(df_local['id'])
    ids_inativar = ids_local - ids_api
    if ids_inativar:
        conn.execute(f"UPDATE equipamentos SET ativo=0 WHERE id IN ({','.join(['?']*len(ids_inativar))})", list(ids_inativar))
    conn.commit()
    conn.close()
    print('Atualização concluída.')

if __name__ == '__main__':
    print('Buscando equipamentos na API Auvo...')
    equipamentos_api = fetch_equipamentos_auvo()
    print(f'Total recebido: {len(equipamentos_api)}')
    atualizar_banco_equipamentos(equipamentos_api)
