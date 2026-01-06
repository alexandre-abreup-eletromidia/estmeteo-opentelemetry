#!/bin/bash
# =============================================================================
# estmeteo-opentelemetry - Script de Instalação Remota
# Executar via SSH no NUC Linux da estação meteorológica
# =============================================================================
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/alexandreabreuelt/estmeteo-opentelemetry/main/install.sh | bash
# Ou:
#   wget -qO- https://raw.githubusercontent.com/alexandreabreuelt/estmeteo-opentelemetry/main/install.sh | bash
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
# Configurações
INSTALL_DIR="/opt/estmeteo-opentelemetry"
GITHUB_USER="${GITHUB_USER:-alexandre-abreup-eletromidia}"
REPO_NAME="${REPO_NAME:-estmeteo-opentelemetry}"

if [[ -n "$GITHUB_TOKEN" ]]; then
    # Repositório Privado (usa token)
    REPO_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"
else
    # Repositório Público (tentativa padrão)
    REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
fi

PYTHON_MIN_VERSION="3.8"
SERVICE_NAME="estmeteo-otel"

# Funções de log
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        estmeteo-opentelemetry - Instalador Remoto            ║${NC}"
echo -e "${BLUE}║        Eletromidia - Estações Meteorológicas                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se está rodando como root
if [[ $EUID -ne 0 ]]; then
   log_error "Este script precisa ser executado como root (use sudo)"
   exit 1
fi

# Verificar sistema operacional
log_info "Verificando sistema operacional..."
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$NAME
    VERSION=$VERSION_ID
    log_success "Sistema: $OS $VERSION"
else
    log_error "Sistema operacional não suportado"
    exit 1
fi

# Verificar Python
log_info "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    # Usar o próprio Python para verificar a versão (evita erro de float 3.12 < 3.8)
    if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_success "Python $PYTHON_VERSION encontrado"
    else
        log_error "Python $PYTHON_MIN_VERSION ou superior necessário (atual: $PYTHON_VERSION)"
        exit 1
    fi
else
    log_error "Python3 não encontrado. Instalando..."
    apt-get update && apt-get install -y python3 python3-pip python3-venv
fi

# Instalar dependências do sistema
log_info "Instalando dependências do sistema..."
apt-get update
apt-get install -y git curl wget bc

# Criar diretório de instalação
log_info "Criando diretório de instalação..."
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Clonar ou atualizar repositório
if [[ -d "$INSTALL_DIR/.git" ]]; then
    log_info "Atualizando repositório existente..."
    GIT_TERMINAL_PROMPT=0 git pull origin main || log_warn "Falha na atualização. Verifique as credenciais."
else
    log_info "Clonando repositório..."
    GIT_TERMINAL_PROMPT=0 git clone $REPO_URL . || {
        log_error "Falha ao clonar repositório."
        log_warn "Se o repositório for PRIVADO, use:"
        log_warn "export GITHUB_TOKEN=seu_token_aqui"
        log_warn "curl ... | sudo -E bash"
        exit 1
    }
fi

# Criar ambiente virtual Python
log_info "Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
log_info "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretório de credenciais
log_info "Criando diretório de credenciais..."
mkdir -p $INSTALL_DIR/credentials
chmod 700 $INSTALL_DIR/credentials

# Criar arquivo .env se não existir
if [[ ! -f "$INSTALL_DIR/.env" ]]; then
    log_info "Criando arquivo de configuração..."
    cp $INSTALL_DIR/.env.example $INSTALL_DIR/.env
    log_warn "Edite o arquivo $INSTALL_DIR/.env com suas configurações"
fi

# Criar serviço systemd
log_info "Configurando serviço systemd..."
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=estmeteo-opentelemetry - Exportador de Logs para Google Sheets
After=network.target estacao-meteorologica.service
Wants=estacao-meteorologica.service

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
systemctl daemon-reload

# Mensagem de conclusão
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Instalação Concluída com Sucesso!               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
log_success "Diretório de instalação: $INSTALL_DIR"
log_success "Serviço systemd: $SERVICE_NAME"
echo ""
log_warn "PRÓXIMOS PASSOS:"
echo "  1. Copie o arquivo credentials.json para: $INSTALL_DIR/credentials/"
echo "  2. Edite o arquivo de configuração: nano $INSTALL_DIR/.env"
echo "  3. Execute a autenticação: cd $INSTALL_DIR && ./venv/bin/python -m src.auth_setup"
echo "  4. Inicie o serviço: systemctl start $SERVICE_NAME"
echo "  5. Habilite início automático: systemctl enable $SERVICE_NAME"
echo ""
log_info "Para verificar status: systemctl status $SERVICE_NAME"
log_info "Para ver logs: journalctl -u $SERVICE_NAME -f"
echo ""
