# tracking_braspress

Integração com a API da **Braspress** para registrar e atualizar ocorrências no `FATURAMENTO_OCORRENCIAS`.

## Estrutura

```text
tracking_braspress/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada (CLI)
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configurações e variáveis de ambiente
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── logger.py           # Logger centralizado (arquivo e console)
│   │   ├── constants.py        # Constantes e mapas
│   │   └── utils.py            # Funções utilitárias
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py       # Conexão com banco
│   │   └── faturamento_repo.py # Operações SQL e manipulação de dados
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── braspress_service.py # Integração com a API Braspress
│   │
│   └── use_cases/
│       ├── __init__.py
│       └── process_faturamento.py # Regras de negócio (inserir e atualizar)
│
├── .env
├── .env.example
├── requirements.txt
├── README.md
└── run.py                      # Script simples pra rodar o app
```

Uma pasta `logs/` é criada automaticamente para armazenar o arquivo de log (`app.log`).

## Requisitos

- Python 3.9+
- Driver ODBC para SQL Server instalado no sistema (ex.: **ODBC Driver 17 for SQL Server**)
- Acesso ao banco de dados e à API da Braspress

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Crie seu arquivo `.env` (ou edite o existente) — **não comite este arquivo em repositórios públicos**.

## Uso

Existem três comandos principais no CLI:

- `insert` – insere registros iniciais na `FATURAMENTO_OCORRENCIAS` (COD_OCORRENCIA = '00').
- `update` – consulta a API da Braspress e atualiza `COD_OCORRENCIA`, `OBSERVACAO`, `DATA_OCORRENCIA` e `HORA_OCORRENCIA`.
- `all` – executa `insert` e, em seguida, `update`.

Você pode opcionalmente informar a data inicial (padrão vem de `FATURAMENTO_START_DATE` no .env) no formato `YYYYMMDD`:

```bash
python run.py insert --since 20251001
python run.py update --since 20251001
python run.py all --since 20251001
```

## Variáveis de ambiente (.env)

Ver arquivo `.env.example` para referência. Principais chaves:

- `API_CNPJ`, `API_USER`, `API_PASSWORD`, `API_URL`
- `DB_DRIVER`, `DB_SERVER`, `DB_DATABASE`, `DB_USER`, `DB_PASSWORD`
- `FATURAMENTO_START_DATE` (ex.: `20251001`)
- `REQUEST_TIMEOUT_SECONDS`, `REQUEST_RETRIES`, `REQUEST_BACKOFF`
- `LOG_DIR` (padrão: `logs`)

## Observações

- O sistema mantém `DATA_OCORRENCIA` e `HORA_OCORRENCIA` existentes. Caso já exista valor no banco, eles **não** serão sobrescritos durante o `update`.
- A atualização ignora linhas com `COD_OCORRENCIA = '01'` (FINALIZADO).
- O `driver` do ODBC é normalizado para possuir chaves (`{}`) caso não estejam presentes.
