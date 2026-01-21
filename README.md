# estmeteo-opentelemetry

Projeto para instrumentação e envio de telemetria (traces, métricas e logs) do EstMeteo usando OpenTelemetry.  
Este repositório reúne configurações, exemplos e boas práticas para integrar aplicações do EstMeteo a uma pipeline de observabilidade baseada em OpenTelemetry (OTel).

## Sumário
- [Objetivo](#objetivo)
- [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação e Execução](#instalação-e-execução)
- [Configuração de Telemetria (exemplos)](#configuração-de-telemetria-exemplos)
- [Exemplo de docker-compose](#exemplo-de-docker-compose)
- [Como instrumentar seu código](#como-instrumentar-seu-código)
- [Observability tips / Boas práticas](#observability-tips--boas-práticas)
- [Contribuição](#contribuição)
- [Licença](#licença)
- [Contato](#contato)

## Objetivo
Centralizar e padronizar a instrumentação das aplicações EstMeteo utilizando OpenTelemetry, permitindo:
- Coletar traces distribuídos para diagnosticar latências e fluxos entre serviços;
- Exportar métricas para sistemas de monitoramento (Prometheus, metrics backend, etc.);
- Exportar logs correlacionados com traces para facilitar debugging;
- Fornecer configurações reutilizáveis (Collector, pipelines, exporters) e exemplos por linguagem.

## Visão Geral da Arquitetura
- Instrumentação (SDK) — integrada nas aplicações (ex.: Python, Node.js, Java, Go).
- OpenTelemetry Collector — centraliza, processa e envia telemetria para backends (OTLP, Jaeger, Prometheus, etc.).
- Backend(s) de observabilidade — Jaeger, Tempo, Grafana, Prometheus, New Relic, Honeycomb, etc.

Fluxo simplificado:
Aplicação instrumentada -> OTEL SDK -> OTEL Collector (local/cluster) -> Exportadores -> Backend observability

## Funcionalidades
- Exemplos de configuração do OpenTelemetry Collector (pipelines de traces/metrics/logs).
- Modelos de environment variables para configurar endpoints OTLP/Jaeger.
- Snippets de instrumentação por linguagem (exemplos básicos).
- docker-compose de demonstração para executar Collector + backend leve (ex.: Jaeger).

## Requisitos
- Docker / docker-compose (para executar exemplos)
- Backend observability (ou usar demonstrações locais como Jaeger/Prometheus)
- Variáveis de ambiente para configurar endpoints OTEL (detalhes abaixo)

## Instalação e Execução (exemplo local)
1. Clone o repositório:
   - git clone https://github.com/alexandre-abreup-eletromidia/estmeteo-opentelemetry.git
2. Ajuste as configurações de acordo com sua aplicação e backend (veja seção de configuração).
3. Execute os exemplos com Docker:
   - docker-compose up --build

(Remarque: adapte os comandos conforme o build e scripts presentes no seu repositório.)

## Configuração de Telemetria (exemplos)
As opções abaixo são exemplos comuns de variáveis de ambiente utilizadas pelas SDKs e pelo Collector.

Variáveis comuns:
- OTEL_SERVICE_NAME=estmeteo-service
- OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
- OTEL_RESOURCE_ATTRIBUTES=deployment.environment=dev,service.version=0.1.0
- OTEL_TRACES_EXPORTER=otlp
- OTEL_METRICS_EXPORTER=prometheus,otlp

Exemplo para enviar via OTLP gRPC:
- export OTEL_EXPORTER_OTLP_ENDPOINT="http://collector:4317"

Exemplo para Jaeger (quando a SDK suporta exporter direto):
- export JAEGER_AGENT_HOST=jaeger
- export JAEGER_AGENT_PORT=6831

Collector: pipeline mínimo (conceitual)
- receivers: otlp
- processors: batch, memory_limiter
- exporters: jaeger, prometheus, otlp
- service.pipelines: traces (otlp -> batch -> jaeger), metrics (otlp -> prometheus)

## Exemplo de docker-compose
Abaixo um exemplo reduzido para demonstração com Collector + Jaeger:

```yaml
version: "3.7"
services:
  otel-collector:
    image: otel/opentelemetry-collector:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC
      - "55681:55681" # OTLP http (se necessário)
      - "8888:8888"   # Prometheus metrics (se exposto)

  jaeger:
    image: jaegertracing/all-in-one:1.43
    ports:
      - "16686:16686" # UI
      - "14268:14268" # collector
```

Obs.: Ajuste a `collector-config.yaml` conforme sua pipeline.

## Como instrumentar seu código
A instrumentação depende da linguagem e framework. Exemplo resumido para Node.js:

1. Instale SDKs:
   - npm install @opentelemetry/api @opentelemetry/sdk-node @opentelemetry/exporter-otlp-grpc

2. Código inicial (index.js):
```js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-otlp-grpc');

const exporter = new OTLPTraceExporter({ url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT });

const sdk = new NodeSDK({
  traceExporter: exporter,
});

sdk.start();
```

Para outras linguagens (Python, Java, Go) existem instruções e auto-instrumentation. Consulte a documentação oficial de OpenTelemetry para o SDK e instrumentação automática da sua linguagem:
- https://opentelemetry.io/docs/

## Observability tips / Boas práticas
- Defina resource attributes (service.name, service.version, environment) para facilitar filtragem.
- Capture spans significativos (requests HTTP, chamadas a banco, filas).
- Adicione atributos úteis e não sensíveis (evite PII).
- Configure sampling adequado (eventualmente downsample em produção).
- Centralize configuração via environment variables e/ou configurador do Collector.
- Correlacione logs com trace_id/trace_span_id para diagnóstico eficiente.

## Contribuição
Contribuições são bem-vindas! Sugestões:
- Adicione exemplos de instrumentação por linguagem encontrados no seu código.
- Melhore o arquivo `collector-config.yaml` com pipelines reais usados no ambiente EstMeteo.
- Documente comandos de build/run específicos das aplicações.

Processo:
1. Fork do repositório
2. Crie uma branch com sua feature/fix
3. Abra um Pull Request descrevendo as mudanças

## Licença
Adicione aqui a licença do projeto (por exemplo MIT). Se preferir, forneça a licença que sua organização exige.

## Contato
Para dúvidas ou suporte, abra uma issue no repositório ou contate o autor/maintainer.

---

Observação: este README é um rascunho genérico focado em integrar OpenTelemetry ao projeto "estmeteo". Posso:
- Ajustar o conteúdo conforme as linguagens e scripts reais do repositório;
- Gerar um arquivo `collector-config.yaml` de exemplo completo;
- Abrir um commit no repositório com este README (se você autorizar).

Diga como prefere prosseguir: ajustar ao código existente, gerar configurações extras (collector, exemplo por linguagem), ou fazer o commit diretamente.
