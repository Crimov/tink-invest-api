import os

API_URL = "https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1"
API_TOKEN = os.getenv("API_TOKEN")
if API_TOKEN is None:
    raise ValueError(
        "API_TOKEN environment variable is not set. "
        "Please set it with: $env:API_TOKEN='your_token' in PowerShell"
    )

DB_HOST = "localhost"
DB_NAME = "tink_invest"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_PORT = 5432
