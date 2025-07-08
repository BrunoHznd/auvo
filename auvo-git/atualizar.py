#!/usr/bin/env python3
import subprocess
import time
import sys
import os

# Caminho absoluto do script atualizar_tarefas.py
SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atualizacoes", "atualizar_tarefas.py")

# Lista dos serviços de painel a serem reiniciados
PANEIS = [
    "painel_setor1.service",
    "painel_setor2.service",
    "painel_setor3.service",
    "painel_setor4.service",
    "painel_setor5.service",
]

def main():
    print("=== Executando atualizar_tarefas.py ===")
    try:
        result = subprocess.run([sys.executable, SCRIPT_PATH], check=True)
        print("✔ atualizar_tarefas.py executado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"✖ Erro ao executar atualizar_tarefas.py: {e}")
        sys.exit(1)

    print("\n=== Reiniciando serviços dos painéis ===")
    for servico in PANEIS:
        print(f"Reiniciando {servico}...")
        try:
            subprocess.run(["sudo", "systemctl", "restart", servico], check=True)
            print(f"✔ {servico} reiniciado com sucesso.")
        except subprocess.CalledProcessError as e:
            print(f"✖ Falha ao reiniciar {servico}: {e}")
        time.sleep(5)
    print("\n✅ Todos os serviços foram reiniciados.")

if __name__ == "__main__":
    main()
