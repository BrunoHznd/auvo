#!/bin/bash



# Caminho do diretório onde estão os scripts Python

SCRIPT_DIR="/root/auvo-git/atualizacoes"

PYTHON="/usr/bin/python3"

LOG="/var/log/atualizacoes_pix.log"



# Estilo para as mensagens no terminal

verde='\033[0;32m'

vermelho='\033[0;31m'

amarelo='\033[1;33m'

neutro='\033[0m'



# Lista dos scripts a serem executados

SCRIPTS=(

    "atualizar_tarefas.py"

    "baixar_tarefas_10_dias.py"

    "baixar_tarefas_completo.py"

    "baixar_tarefas_dia_atual.py"

    "baixar_tarefas_mes_atual.py"

    "limpar_tarefas_inexistentes.py"

)



TOTAL=${#SCRIPTS[@]}

PROGRESS=0



echo -e "${amarelo}=== Iniciando execução dos scripts de atualização... $(date '+ %d/%m/%Y %H:%M:%S') ===${neutro}"

echo "==================== $(date '+%Y-%m-%d %H:%M:%S') ====================" >> "$LOG"



cd "$SCRIPT_DIR" || { echo -e "${vermelho}Erro: pasta não encontrada.$neutro"; exit 1; }



for i in "${!SCRIPTS[@]}"; do

    SCRIPT=${SCRIPTS[$i]}

    PROGRESS=$(( (i + 1) * 100 / TOTAL ))



    echo -e "${amarelo}[${PROGRESS}%] Executando ${SCRIPT}...${neutro}"

    if $PYTHON "$SCRIPT" >> "$LOG" 2>&1; then

        echo -e "${verde}✔ ${SCRIPT} finalizado com sucesso.${neutro}"

    else

        echo -e "${vermelho}✖ Erro ao executar ${SCRIPT}. Verifique o log.${neutro}"

    fi

done



echo "==================== FIM DAS ATUALIZAÇÕES ====================" >> "$LOG"

echo "" >> "$LOG"

echo -e "${verde}✅ Todos os scripts foram executados. Veja o log em $LOG${neutro}"



# Aguarda 10 segundos antes de reiniciar o dashboard principal

echo -e "${amarelo}Aguardando 10 segundos antes de reiniciar o dashboard.service...${neutro}"

sleep 10



echo -e "${amarelo}Reiniciando dashboard.service...${neutro}"

if sudo systemctl restart dashboard.service; then

    echo -e "${verde}✔ dashboard.service reiniciado com sucesso.${neutro}"

else

    echo -e "${vermelho}✖ Falha ao reiniciar dashboard.service.${neutro}"

fi



# Lista de serviços de painel a serem reiniciados em sequência

PANEIS=(

    "painel_setor1.service"

    "painel_setor2.service"

    "painel_setor3.service"

    "painel_setor4.service"

    "painel_setor5.service"

)



for SERVICO in "${PANEIS[@]}"; do

    echo -e "${amarelo}Aguardando 5 segundos antes de reiniciar ${SERVICO}...${neutro}"

    sleep 5



    echo -e "${amarelo}Reiniciando ${SERVICO}...${neutro}"

    if sudo systemctl restart "$SERVICO"; then

        echo -e "${verde}✔ ${SERVICO} reiniciado com sucesso.${neutro}"

    else

        echo -e "${vermelho}✖ Falha ao reiniciar ${SERVICO}.${neutro}"

    fi

done



echo -e "${verde}✅ Todos os serviços foram reiniciados.${neutro}"

