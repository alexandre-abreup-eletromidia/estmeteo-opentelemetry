#!/bin/bash
# =============================================================================
# Script de Deploy Rápido para Múltiplas Estações
# Uso: ./deploy.sh usuario@ip1 usuario@ip2 usuario@ip3
# =============================================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_SCRIPT="https://raw.githubusercontent.com/alexandreabreuelt/estmeteo-opentelemetry/main/install.sh"

if [[ $# -eq 0 ]]; then
    echo "Uso: $0 usuario@host1 [usuario@host2] [usuario@host3] ..."
    echo "Exemplo: $0 root@192.168.1.100 root@192.168.1.101"
    exit 1
fi

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Deploy Remoto - estmeteo-opentelemetry                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

for HOST in "$@"; do
    echo -e "${BLUE}[DEPLOY]${NC} Iniciando deploy em: $HOST"
    
    if ssh -o ConnectTimeout=10 "$HOST" "curl -fsSL $INSTALL_SCRIPT | bash"; then
        echo -e "${GREEN}[OK]${NC} Deploy concluído em: $HOST"
    else
        echo -e "${RED}[ERRO]${NC} Falha no deploy em: $HOST"
    fi
    
    echo "---"
done

echo ""
echo -e "${GREEN}Deploy finalizado!${NC}"
echo ""
echo "Próximos passos para cada estação:"
echo "  1. Copie credentials.json via SCP"
echo "  2. Configure o .env"
echo "  3. Execute a autenticação OAuth2"
echo "  4. Inicie o serviço"
