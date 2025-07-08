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


def baixar_tarefas_ultimos_10_dias():
    criar_tabela_tarefas()

    hoje = datetime.now().date()

    if not USUARIOS:
        print("❌ O dicionário USUARIOS está vazio. Verifique o arquivo env_reader.py.")
        return

    print(f"\n✅ {len(USUARIOS)} usuários carregados:")
    for uid, nome in USUARIOS.items():
        print(f"- {nome} (ID {uid})")

    for dias_atras in range(0, 10):  # hoje até 9 dias atrás
        data_ref = hoje - timedelta(days=dias_atras)
        data_str = data_ref.strftime("%Y-%m-%d")

        print(f"\n📅 Buscando tarefas para o dia: {data_str}")

        for user_id, nome in USUARIOS.items():
            print(f"🔍 [{data_str}] {nome} (ID {user_id})...")
            try:
                tarefas = get_user_tasks(user_id, data_str, data_str)
                if isinstance(tarefas, list):
                    for tarefa in tarefas:
                        salvar_tarefa(tarefa, user_id, data_str)
                    print(f"✔️ {len(tarefas)} tarefa(s) salvas.")
                else:
                    print(f"⚠️ Retorno inesperado da API: {tarefas}")
            except Exception as e:
                print(f"❌ Erro ao buscar tarefas para {nome} em {data_str}: {e}")


def limpar_tarefas_inexistentes():
    from app.api_auvo import get_user_tasks

    conn = sqlite3.connect(DB_TAREFAS)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT data_referencia FROM tarefas_raw")
    datas = [row[0] for row in cursor.fetchall()]

    tarefas_atuais = set()

    for user_id, nome in USUARIOS.items():
        print(f"\n🔄 Verificando tarefas atuais da API para {nome} (ID {user_id})")
        for data in datas:
            try:
                tarefas = get_user_tasks(user_id, data, data)
                if isinstance(tarefas, list):
                    for tarefa in tarefas:
                        task_id = tarefa.get("taskID")
                        if task_id:
                            tarefas_atuais.add(str(task_id))
            except Exception as e:
                print(f"⚠️ Erro ao verificar {nome} em {data}: {e}")

    cursor.execute("SELECT taskID FROM tarefas_raw")
    tarefas_banco = {row[0] for row in cursor.fetchall()}

    tarefas_para_remover = tarefas_banco - tarefas_atuais
    print(f"\n🗑️ Tarefas a remover: {len(tarefas_para_remover)}")

    removidas = 0
    for task_id in tarefas_para_remover:
        cursor.execute("DELETE FROM tarefas_raw WHERE taskID = ?", (task_id,))
        removidas += cursor.rowcount

    conn.commit()
    conn.close()
    print(f"✅ Total de tarefas removidas: {removidas}")


if __name__ == "__main__":
    print("🔁 Iniciando atualização de tarefas dos últimos 10 dias...")
    baixar_tarefas_ultimos_10_dias()

    print("\n🧹 Iniciando limpeza de tarefas inexistentes na API...")
    limpar_tarefas_inexistentes()

    print("\n✅ Processo finalizado com sucesso!")
