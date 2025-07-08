#!/bin/bash

# Caminho do diretório onde está o script Python principal de atualização de bancos
SCRIPT_DIR="/root/auvo-git/atualizacoes"
PYTHON="/usr/bin/python3"
LOG="/var/log/atualizacoes_bancos.log"

# Cores para as mensagens no terminal
verde='\033[0;32m'
vermelho='\033[0;31m'
amarelo='\033[1;33m'
neutro='\033[0m'

# Nome do único script que realmente atualiza os bancos
SCRIPT="atualizar_tarefas.py"

echo -e "${amarelo}=== Iniciando atualização dos bancos... $(date '+%d/%m/%Y %H:%M:%S') ===${neutro}"
echo "==================== $(date '+%Y-%m-%d %H:%M:%S') ====================" >> "$LOG"

cd "$SCRIPT_DIR" || { echo -e "${vermelho}Erro: pasta não encontrada.$neutro"; exit 1; }

echo -e "${amarelo}Executando ${SCRIPT}...${neutro}"
if $PYTHON "$SCRIPT" >> "$LOG" 2>&1; then
    echo -e "${verde}✔ ${SCRIPT} finalizado com sucesso.${neutro}"
else
    echo -e "${vermelho}✖ Erro ao executar ${SCRIPT}. Verifique o log em $LOG${neutro}"
fi

echo "==================== FIM DA ATUALIZAÇÃO DE BANCOS ====================" >> "$LOG"
echo "" >> "$LOG"
echo -e "${verde}✅ O banco foi atualizado. Confira os detalhes em $LOG${neutro}"
