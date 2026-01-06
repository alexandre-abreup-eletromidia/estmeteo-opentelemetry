# Explicação do Sistema de Logs - Meteo Stations Linux

O sistema de monitoramento meteorológico possui uma arquitetura de logs robusta, projetada para operação 24/7 e recuperação de falhas. Abaixo está o detalhamento de como os registros são gerados, armazenados e rotacionados.

## 1. Geração de Logs (Python)

O script principal `estacao_meteorologica.py` utiliza o módulo `logging` do Python para centralizar todos os eventos.

- **Localização**: `~/logs_estacao/estacao_YYYYMMDD.log`
- **Conteúdo**:
  - **Leituras de Sensores**: Registra os valores de temperatura, umidade, pressão e chuva de cada estação.
  - **Status da API**: Indica se os dados foram enviados com sucesso ou se houve falha (HTTP status codes).
  - **Eventos do Sistema**: Scans de portas RS485, detecção de IDs de estações e tentativas de reconexão.
- **Saída Dupla**: Os logs são gravados simultaneamente no arquivo físico e no stdout (capturado pelo systemd).

## 2. Rotação e Retenção

Para evitar que o disco do NUC fique cheio, o sistema utiliza o `logrotate` do Linux.

- **Configuração**: `/etc/logrotate.d/estacao-meteorologica`
- **Frequência**: Diária
- **Retenção**: Mantém os logs dos últimos 30 dias
- **Otimização**: Logs antigos são compactados (.gz) para economizar espaço

## 3. Armazenamento Offline (Cache)

Quando a conexão com a internet falha, o sistema não perde os registros.

- **Banco de Dados**: SQLite em `/opt/estacao_meteorologica/offline_cache/pendencias.db`
- **Funcionamento**: Se o envio para a API falha, o registro é salvo localmente. O sistema tenta reenviar esses registros automaticamente assim que a conexão é restabelecida.

## 4. Integração com Systemd

O sistema roda como um serviço (`estacao-meteorologica.service`), o que permite monitoramento em tempo real via terminal:

```bash
sudo journalctl -u estacao-meteorologica -f
```

---

## Endpoints e Configurações

| Item | Valor |
|------|-------|
| **API Endpoint** | `https://iothub.eletromidia.com.br/api/v1/estacoes_mets/storeOrUpdate` |
| **Script Principal** | `/opt/estacao_meteorologica/estacao_meteorologica.py` |
| **Logs** | `~/logs_estacao/` |
| **Cache Offline** | `/opt/estacao_meteorologica/offline_cache/pendencias.db` |
| **Logrotate Config** | `/etc/logrotate.d/estacao-meteorologica` |
| **Systemd Service** | `estacao-meteorologica.service` |

---

## Estrutura de Log Atual

```log
2026-01-06 10:30:15 INFO [STATION_001] Leitura de sensores iniciada
2026-01-06 10:30:16 INFO [STATION_001] Temp: 25.3°C, Umid: 65%, Press: 1013hPa, Rain: 0.0mm
2026-01-06 10:30:17 INFO [STATION_001] Enviando dados para API...
2026-01-06 10:30:18 INFO [STATION_001] API Response: 200 OK (latency: 245ms)
2026-01-06 10:30:18 INFO [STATION_002] Leitura de sensores iniciada
2026-01-06 10:30:19 ERROR [STATION_002] RS485 timeout após 3 tentativas
2026-01-06 10:30:20 WARNING [CACHE] Registro salvo offline (pendencias: 15)
```

---

## Integração com OpenTelemetry (Proposta)

Para habilitar a exportação dos logs para Google Sheets, a migração para OpenTelemetry seguirá este mapeamento:

| Log Tradicional | OpenTelemetry Attribute |
|-----------------|-------------------------|
| `[STATION_001]` | `service.instance.id` |
| Timestamp | `timestamp` (nanoseconds) |
| `INFO/ERROR/...` | `severity_text` |
| Mensagem | `body` |
| Dados de sensores | `attributes` (key-value) |

### Exemplo de Log OpenTelemetry

```python
from opentelemetry import logs

logger = logs.get_logger("estacao-meteorologica")
logger.emit(
    LogRecord(
        timestamp=time.time_ns(),
        observed_timestamp=time.time_ns(),
        body="Leitura de sensores concluída",
        severity_number=SeverityNumber.INFO,
        severity_text="INFO",
        attributes={
            "station_id": "STATION_001",
            "temperature": 25.3,
            "humidity": 65.0,
            "pressure": 1013.0,
            "rain": 0.0,
            "api_status": 200,
            "response_time_ms": 245
        }
    )
)
```
