#!/bin/bash
# =============================================================================
# estmeteo-opentelemetry - Script de Desinstalação
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

INSTALL_DIR="/opt/estmeteo-opentelemetry"
SERVICE_NAME="estmeteo-otel"

echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║        estmeteo-opentelemetry - Desinstalador                ║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[ERROR]${NC} Execute como root (sudo)"
   exit 1
fi

read -p "Deseja remover completamente o estmeteo-opentelemetry? (s/N): " confirm
if [[ "$confirm" != "s" && "$confirm" != "S" ]]; then
    echo "Operação cancelada."
    exit 0
fi

echo -e "${YELLOW}[INFO]${NC} Parando serviço..."
systemctl stop $SERVICE_NAME 2>/dev/null || true
systemctl disable $SERVICE_NAME 2>/dev/null || true

echo -e "${YELLOW}[INFO]${NC} Removendo serviço systemd..."
rm -f /etc/systemd/system/${SERVICE_NAME}.service
systemctl daemon-reload

read -p "Deseja manter os arquivos de credenciais? (S/n): " keep_creds
if [[ "$keep_creds" == "n" || "$keep_creds" == "N" ]]; then
    echo -e "${YELLOW}[INFO]${NC} Removendo diretório de instalação..."
    rm -rf $INSTALL_DIR
else
    echo -e "${YELLOW}[INFO]${NC} Movendo credenciais para /tmp..."
    mv $INSTALL_DIR/credentials /tmp/estmeteo-credentials-backup 2>/dev/null || true
    rm -rf $INSTALL_DIR
    echo -e "${GREEN}[OK]${NC} Credenciais salvas em: /tmp/estmeteo-credentials-backup"
fi

echo ""
echo -e "${GREEN}[OK]${NC} Desinstalação concluída!"
