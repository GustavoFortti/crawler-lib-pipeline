#!/bin/bash

# Definir o diretório de log
LOG_DIR="$LOCAL/temp/logs"
MAX_FILES=50
# Criar o diretório de log, caso não exista
mkdir -p $LOG_DIR

# Contar o número de arquivos de log existentes
LOG_COUNT=$(ls $LOG_DIR | wc -l)

# Excluir todos os arquivos de log, exceto o último, se houver mais de 50 arquivos de log
if [ $LOG_COUNT -gt $MAX_FILES ]; then
    ls -1t $LOG_DIR | tail -n +2 | xargs -I {} rm -- $LOG_DIR/{}
fi

# Gerar uma string aleatória de 8 caracteres
RANDOM_STRING=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1)

# Obter a data e hora atual formatada
CURRENT_DATETIME=$(date '+%Y-%m-%d_%H-%M-%S')

# Criar o nome do arquivo de log com data, hora, string aleatória e ID
LOGFILE="${LOG_DIR}/logfile_${CURRENT_DATETIME}_${RANDOM_STRING}.log"

# Funções para log
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a $LOGFILE
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a $LOGFILE >&2
}

log_warning() {
    echo "[WARNING] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a $LOGFILE >&2
}

# Exemplos de uso das funções de log
log_info "Iniciando lib de logs..."
log_info "FILE: $LOGFILE"