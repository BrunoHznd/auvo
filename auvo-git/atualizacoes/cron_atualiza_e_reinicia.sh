#!/bin/bash

#
# cron_atualiza_e_reinicia.sh
#
# 1) Executa o atualizar_tarefas.py para atualizar o banco
# 2) Executa o limpar_tarefas_inexistentes.py para limpar registros órfãos
# 3) Aguarda 5 segundos
# 4) Reinicia os serviços Streamlit
#

# Caminho absoluto dos scripts
BASE_DIR="/root/auvo-git/atualizacoes"
PYTHON="/usr/bin/python3"
LOG="/var/log/cron_atualizacoes.log"

# Lista dos serviços Streamlit
SERVICOS=(
  "auvo-dashboard.service"
  "dashboard_semestral.service"
  "dashboard_mensal.service"
  "painel_setor1.service"
  "painel_setor2.service"
  "painel_setor3.service"
  "painel_setor4.service"
  "painel_setor5.service"
)

# Cores para o terminal
verde='\033[0;32m'
amarelo='\033[1;33m'
vermelho='\033[0;31m'
neutro='\033[0m'

echo -e "${amarelo}========== [$(date '+%Y-%m-%d %H:%M:%S')] Iniciando atualização do banco ==========${neutro}" | tee -a "$LOG"

cd "$BASE_DIR" || {
  echo -e "${vermelho}Erro: não conseguiu acessar $BASE_DIR${neutro}" | tee -a "$LOG"
  exit 1
}

## --------- Atualizar tarefas ---------
echo -e "${amarelo}Executando atualizar_tarefas.py...${neutro}" | tee -a "$LOG"
if $PYTHON atualizar_tarefas.py >> "$LOG" 2>&1; then
  echo -e "${verde}✔ atualizar_tarefas.py concluído com sucesso${neutro}" | tee -a "$LOG"
else
  echo -e "${vermelho}✖ Erro ao executar atualizar_tarefas.py (verificar $LOG)${neutro}" | tee -a "$LOG"
  # exit 1
fi


## --------- Limpar tarefas inexistentes ---------
echo -e "${amarelo}Executando limpar_tarefas_inexistentes.py...${neutro}" | tee -a "$LOG"
if $PYTHON limpar_tarefas_inexistentes.py >> "$LOG" 2>&1; then
  echo -e "${verde}✔ limpar_tarefas_inexistentes.py concluído com sucesso${neutro}" | tee -a "$LOG"
else
  echo -e "${vermelho}✖ Erro ao executar limpar_tarefas_inexistentes.py (verificar $LOG)${neutro}" | tee -a "$LOG"
  # exit 1
fi


## --------- Reiniciar serviços ---------
echo -e "${amarelo}Aguardando 5 segundos antes de reiniciar os serviços...${neutro}" | tee -a "$LOG"
sleep 5

for svc in "${SERVICOS[@]}"; do
  echo -e "${amarelo}Reiniciando $svc...${neutro}" | tee -a "$LOG"
  if sudo systemctl restart "$svc"; then
    echo -e "${verde}✔ $svc reiniciado com sucesso${neutro}" | tee -a "$LOG"
  else
    echo -e "${vermelho}✖ Erro ao reiniciar $svc${neutro}" | tee -a "$LOG"
  fi
  sleep 2
done


echo -e "${verde}========== [$(date '+%Y-%m-%d %H:%M:%S')] Processamento concluído. Todos os serviços reiniciados. ==========${neutro}" | tee -a "$LOG"
echo "" | tee -a "$LOG"
