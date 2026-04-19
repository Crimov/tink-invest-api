import requests
import config
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

headers = {
    "Authorization": f"Bearer {config.API_TOKEN}",
    "accept": "application/json",
    "Content-Type": "application/json"
}

def get_accounts() -> list:
    url = f"{config.API_URL}.UsersService/GetAccounts"
    logger.info("Запрос списка аккаунтов: %s", url)
    try:
        response = requests.post(url=url, headers=headers, json={})
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Ошибка при запросе аккаунтов: %s", e)
        return []
    resp_json = response.json()
    acc_id = []
    for acc in resp_json.get("accounts", []):
        if acc.get("name") == "Брокерский счёт":
            acc_id.append(acc["id"])
        logger.info("Найдено брокерских счетов: %d", len(acc_id))
        return acc_id

def get_products(acc_id: list) -> list:
    logger.info("Получение списка активов для %d аккаунтов", len(acc_id))
    active = []
    for id in acc_id:
        body = {"accountId": id}
        url = f"{config.API_URL}.OperationsService/GetPositions"
        logger.debug("Запрос активов по аккаунту %s %s", id, url)
        try:
            response = requests.post(url=url, headers=headers, json=body)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning("Ошибка при запросе активов по аккаунту %s: %s", id, e)
            continue
        data = response.json().get("securities", [])
        logger.info("Активов найдено по аккаунту %s: %d", id, len(data))
        active.extend(data)
    logger.info("Всего активов получено: %d", len(active))
    return active

def get_money_amount(account_id: str, currency: str):
    body = {"accountId": account_id, "currency": currency}
    url = f"{config.API_URL}.OperationsService/GetPortfolio"
    logger.info("Получение портфеля для аккаунта %s в валюте %s    %s", account_id, currency, url)
    if currency not in ("RUB", "USD", "EUR"):
        logger.error("Передана неподдерживаемая валюта: %s", currency)
        raise ValueError("Unsupported currency, use only: RUB, USD, EUR")
    try:
        response = requests.post(url=url, headers=headers, json=body)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Ошибка при запросе портфеля (%s): %s", currency, e)
        return None
    resp_json = response.json()
    total_curr = {
        "share": {
            "active_type": "share",
            "currency": currency,
            "amount": resp_json["totalAmountShares"]["units"],
        },
        "bond": {
            "active_type": "bond",
            "currency": currency,
            "amount": resp_json["totalAmountBonds"]["units"],
        },
        "etf": {
            "active_type": "etf",
            "currency": currency,
            "amount": resp_json["totalAmountEtf"]["units"],
        },
    }
    logger.info("Получены данные портфеля для %s: %s", currency, total_curr)
    return total_curr


url = f"{config.API_URL}.UsersService/GetAccounts"
body = {
  "instrumentType": "INSTRUMENT_TYPE_SHARE",
  "instrumentStatus": "INSTRUMENT_STATUS_ALL"
}