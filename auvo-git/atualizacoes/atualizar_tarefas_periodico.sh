#!/bin/bash
# Atualiza tarefas e reinicia painéis dos setores
# Para rodar via cron como root

cd /root/auvo-git/atualizacoes
source /root/auvo-git/venv/bin/activate
python atualizar_tarefas.py

# Reinicia todos os painéis dos setores
for servico in painel_setor1.service painel_setor2.service painel_setor3.service painel_setor4.service painel_setor5.service; do
    systemctl restart $servico
    sleep 3
    echo "Reiniciado $servico"
done
