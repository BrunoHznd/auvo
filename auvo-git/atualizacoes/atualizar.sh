#!/bin/bash

# Script para rodar o atualizar.py no Linux Ubuntu 24.04



# Caminho absoluto do diretório do script

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"



cd "$DIR"



# Executa o atualizar.py com python3 (usando o venv se estiver ativado)

python3 ../atualizar.py

