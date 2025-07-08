import os
import sys
import sqlite3
from datetime import datetime, timedelta
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.api_auvo import get_user_tasks
from app.env_reader import USUARIOS

# Detectar o sistema operacional
is_windows = os.name == 'nt'

# Definir caminhos dos bancos de dados baseado no sistema operacional
if is_windows:
    # Caminhos locais para Windows
    DB_TAREFAS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "tarefas.sqlite3"))
    DB_USUARIOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "usuarios.sqlite3"))
    DB_EQUIPAMENTOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "db.sqlite3"))
    DB_CLIENTES = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "clientes_por_grupo.sqlite3"))
    
    # Garante que a pasta data existe
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
else:
    # Caminhos do servidor Linux
    DB_TAREFAS = "/root/auvo-git/data/tarefas.sqlite3"
    DB_USUARIOS = "/root/auvo-git/data/usuarios.sqlite3"
    DB_EQUIPAMENTOS = "/root/auvo-git/data/db.sqlite3"
    DB_CLIENTES = "/root/auvo-git/data/clientes_por_grupo.sqlite3"
    
    # Garante que a pasta data existe
    os.makedirs("/root/auvo-git/data", exist_ok=True)


def criar_tabela_tarefas():
    conn = sqlite3.connect(DB_TAREFAS)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tarefas_raw (
            taskID TEXT,
            user_id INTEGER,
            data_referencia TEXT,
            json TEXT,
            PRIMARY KEY (taskID, user_id)
        )
    """
    )
    conn.commit()
    conn.close()


def salvar_tarefa(task, user_id, data_ref):
    conn = sqlite3.connect(DB_TAREFAS)
    cursor = conn.cursor()
    task_id = task.get("taskID")
    if task_id:
        cursor.execute(
            """
            INSERT OR REPLACE INTO tarefas_raw (taskID, user_id, data_referencia, json)
            VALUES (?, ?, ?, ?)
        """,
            (task_id, user_id, data_ref, json.dumps(task)),
        )
    conn.commit()
    conn.close()


def baixar_todas_tarefas_ultimos_10_dias():
    criar_tabela_tarefas()

    hoje = datetime.now().date()
    data_inicio = hoje - timedelta(days=9)
    data_fim = hoje

    if not USUARIOS:
        print("❌ Dicionário USUARIOS está vazio. Verifique seu .env ou env_reader.py.")
        return

    print(
        f"\n✅ Coletando tarefas de {data_inicio} até {data_fim} para {len(USUARIOS)} usuários."
    )

    for user_id, nome in USUARIOS.items():
        print(
            f"\n👤 Buscando tarefas de {nome} (ID {user_id}) no intervalo completo..."
        )
        try:
            tarefas = get_user_tasks(
                user_id, data_inicio.strftime("%Y-%m-%d"), data_fim.strftime("%Y-%m-%d")
            )

            if isinstance(tarefas, list):
                print(f"🔎 {len(tarefas)} tarefa(s) encontradas.")
                for tarefa in tarefas:
                    # Salva com base na data de atribuição, não só na coleta
                    data_referencia = (
                        tarefa.get("appointmentDate")
                        or tarefa.get("creationDate")
                        or data_fim.strftime("%Y-%m-%d")
                    )
                    salvar_tarefa(tarefa, user_id, data_referencia[:10])
                print("✅ Tarefas salvas com sucesso.")
            else:
                print(f"⚠️ Erro ao buscar tarefas: {tarefas}")
        except Exception as e:
            print(f"❌ Exceção ao buscar tarefas de {nome}: {e}")


if __name__ == "__main__":
    print("🔁 Iniciando atualização completa das tarefas dos últimos 10 dias...")
    baixar_todas_tarefas_ultimos_10_dias()
    print("\n✅ Finalizado com sucesso!")
