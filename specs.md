# Especificações do Sistema - estmeteo-opentelemetry

## Visão Geral
Sistema de telemetria e observabilidade para estações meteorológicas da Eletromidia, utilizando OpenTelemetry para coleta, processamento e exportação de logs estruturados para Google Sheets.

## Usuário
- **Conta Google**: alexandre.abreu@eletromidia.com.br
- **Planilha destino**: A ser configurada ou criada automaticamente

---

## Requisitos Funcionais

### 1. Coleta de Logs (OpenTelemetry)
| ID | Requisito | Descrição |
|----|-----------|-----------|
| RF-01 | Integração OpenTelemetry | Instrumentar o script `estacao_meteorologica.py` com OpenTelemetry SDK |
| RF-02 | Logs Estruturados | Converter logs existentes para formato OTLP (OpenTelemetry Protocol) |
| RF-03 | Atributos Customizados | Adicionar metadata: ID da estação, localização, timestamp UTC |
| RF-04 | Captura de Métricas | Registrar tempo de resposta RS485, latência da API, tamanho do cache |

### 2. Exportação para Google Sheets
| ID | Requisito | Descrição |
|----|-----------|-----------|
| RF-05 | Autenticação OAuth2 | Autenticar com conta `alexandre.abreu@eletromidia.com.br` |
| RF-06 | Exporter Customizado | Criar exporter OpenTelemetry → Google Sheets |
| RF-07 | Batch Processing | Enviar logs em lotes para otimizar uso da API |
| RF-08 | Retry Logic | Implementar retry com backoff exponencial em caso de falha |

### 3. Dados a Exportar
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `timestamp` | datetime | Data/hora do evento (UTC) |
| `station_id` | string | ID da estação meteorológica |
| `severity` | string | INFO, WARNING, ERROR, CRITICAL |
| `category` | string | SENSOR_READ, API_SEND, SYSTEM, OFFLINE_CACHE |
| `message` | string | Descrição do evento |
| `temperature` | float | Temperatura (°C) - quando aplicável |
| `humidity` | float | Umidade (%) - quando aplicável |
| `pressure` | float | Pressão (hPa) - quando aplicável |
| `rain` | float | Precipitação (mm) - quando aplicável |
| `api_status` | int | HTTP status code do envio |
| `response_time_ms` | int | Tempo de resposta em milissegundos |
| `offline_cache_size` | int | Quantidade de registros pendentes |

---

## Requisitos Não-Funcionais

| ID | Categoria | Requisito |
|----|-----------|-----------|
| RNF-01 | Performance | Exportação não deve impactar leitura de sensores (async) |
| RNF-02 | Resiliência | Sistema deve operar mesmo se Google Sheets estiver indisponível |
| RNF-03 | Quota | Respeitar limite de 300 requests/min da Google Sheets API |
| RNF-04 | Segurança | Credenciais OAuth2 armazenadas de forma segura |
| RNF-05 | Compatibilidade | Python 3.8+ |

---

## Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ESTAÇÃO METEOROLÓGICA (NUC)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐    ┌─────────────────────┐    ┌─────────────────┐   │
│  │  Sensores RS485  │───▸│ estacao_meteorolo-  │───▸│  API Eletromidia │   │
│  │  (Temp, Umid,    │    │ gica.py             │    │  (iothub)        │   │
│  │   Pressão, Rain) │    └──────────┬──────────┘    └─────────────────┘   │
│  └──────────────────┘               │                                      │
│                                     │ OpenTelemetry SDK                    │
│                                     ▼                                      │
│                    ┌────────────────────────────────┐                      │
│                    │    LoggerProvider (OTEL)       │                      │
│                    │    - LoggingHandler            │                      │
│                    │    - Resource Attributes       │                      │
│                    └───────────────┬────────────────┘                      │
│                                    │                                       │
│                    ┌───────────────┴───────────────┐                       │
│                    ▼                               ▼                       │
│       ┌─────────────────────┐         ┌─────────────────────┐             │
│       │   File Exporter     │         │ GoogleSheetsExporter │             │
│       │   (logs locais)     │         │ (custom OTEL)        │             │
│       └─────────────────────┘         └──────────┬──────────┘             │
│                                                  │                         │
└──────────────────────────────────────────────────│─────────────────────────┘
                                                   │ HTTPS (OAuth2)
                                                   ▼
                                    ┌─────────────────────────────┐
                                    │     Google Sheets API       │
                                    │  (alexandre.abreu@eletromidia)│
                                    └─────────────────────────────┘
```

---

## Estrutura de Arquivos

```
estmeteo-opentelemetry/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configurações (env vars)
│   ├── otel_setup.py             # Inicialização OpenTelemetry
│   ├── exporters/
│   │   ├── __init__.py
│   │   └── google_sheets.py      # Custom exporter para Google Sheets
│   ├── processors/
│   │   ├── __init__.py
│   │   └── batch_processor.py    # Processador de batches
│   └── utils/
│       ├── __init__.py
│       └── auth.py               # OAuth2 para Google
├── credentials/                  # (gitignored) Arquivos de credenciais
│   └── .gitkeep
├── tests/
│   ├── __init__.py
│   ├── test_exporter.py
│   └── test_integration.py
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
├── README.md
├── specs.md                      # Este arquivo
├── estacao-meteorologica.md      # Documentação do sistema de logs atual
├── install.sh                    # Script de instalação remota
├── uninstall.sh                  # Script de desinstalação
└── deploy.sh                     # Deploy em múltiplas estações
```

---

## 🚀 Instalação Remota via SSH

### One-liner (Método Recomendado)

Conecte-se à estação via SSH e execute:

```bash
# Usando curl
curl -fsSL https://raw.githubusercontent.com/alexandreabreuelt/estmeteo-opentelemetry/main/install.sh | sudo bash

# Ou usando wget
wget -qO- https://raw.githubusercontent.com/alexandreabreuelt/estmeteo-opentelemetry/main/install.sh | sudo bash
```

### Deploy em Múltiplas Estações

Para instalar em várias estações de uma vez:

```bash
# Do seu computador local, execute:
./deploy.sh root@192.168.1.100 root@192.168.1.101 root@192.168.1.102
```

### Pós-Instalação

Após a instalação, execute os seguintes passos em cada estação:

```bash
# 1. Copiar credenciais OAuth2 (do seu computador)
scp credentials.json root@IP_DA_ESTACAO:/opt/estmeteo-opentelemetry/credentials/

# 2. Configurar variáveis de ambiente
ssh root@IP_DA_ESTACAO "nano /opt/estmeteo-opentelemetry/.env"

# 3. Executar autenticação OAuth2 (primeira vez)
ssh root@IP_DA_ESTACAO "cd /opt/estmeteo-opentelemetry && ./venv/bin/python -m src.auth_setup"

# 4. Iniciar e habilitar serviço
ssh root@IP_DA_ESTACAO "systemctl enable --now estmeteo-otel"
```

### Comandos Úteis

```bash
# Verificar status do serviço
systemctl status estmeteo-otel

# Ver logs em tempo real
journalctl -u estmeteo-otel -f

# Reiniciar serviço
systemctl restart estmeteo-otel

# Desinstalar
curl -fsSL https://raw.githubusercontent.com/alexandreabreuelt/estmeteo-opentelemetry/main/uninstall.sh | sudo bash
```

---

## Dependências

```txt
# OpenTelemetry
opentelemetry-api>=1.20.0
opentelemetry-sdk>=1.20.0
opentelemetry-exporter-otlp>=1.20.0

# Google Sheets
google-api-python-client>=2.100.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1

# Utilities
python-dotenv>=1.0.0
tenacity>=8.2.0

# Development
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

---

## Configuração OAuth2

### Passos para configurar acesso ao Google Sheets:

1. **Google Cloud Console**:
   - Criar projeto: `estmeteo-opentelemetry`
   - Ativar API: Google Sheets API
   - Criar credenciais OAuth2 (Desktop App)

2. **Arquivo de credenciais**:
   - Download `credentials.json` para `/credentials/`
   - Primeira execução gerará `token.json`

3. **Variáveis de ambiente** (`.env`):
   ```env
   GOOGLE_CREDENTIALS_PATH=./credentials/credentials.json
   GOOGLE_TOKEN_PATH=./credentials/token.json
   GOOGLE_SHEET_ID=<ID_DA_PLANILHA>
   GOOGLE_SHEET_NAME=Logs
   OTEL_SERVICE_NAME=estacao-meteorologica
   BATCH_SIZE=100
   EXPORT_INTERVAL_SECONDS=60
   ```

---

## Próximos Passos

1. [ ] Aprovação das especificações
2. [ ] Criação do projeto e estrutura de diretórios
3. [ ] Implementação do exporter customizado
4. [ ] Configuração OAuth2 com conta Google
5. [ ] Testes de integração
6. [ ] Documentação de deploy
