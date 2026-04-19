import config
import tink_api
import psycopg2
import logging
from datetime import date

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


def load_money_amount_daily():
    logger.info("Запуск загрузки данных по деньгам на счётах")

    try:
        accounts = tink_api.get_accounts()
        logger.info("Получено аккаунтов: %d", len(accounts))
    except Exception as e:
        logger.error("Ошибка при получении аккаунтов: %s", e)
        return

    today_dt = date.today()

    try:
        pg_conn = psycopg2.connect(
            host=config.DB_HOST,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        logger.info("Подключение к базе данных установлено")
    except psycopg2.Error as e:
        logger.error("Ошибка подключения к базе данных: %s", e)
        return

    cur = pg_conn.cursor()

    for acc in accounts:
        logger.info("Обработка аккаунта: %s", acc)
        try:
            curr_map_rub = tink_api.get_money_amount(acc, "RUB")
            curr_map_usd = tink_api.get_money_amount(acc, "USD")
        except Exception as e:
            logger.error("Ошибка при получении данных по валютам для %s: %s", acc, e)
            continue

        if curr_map_rub and curr_map_usd:
            try:
                cur.execute("""
                    DELETE FROM tink_invest_api.money_amount_daily 
                    WHERE report_dt = %s
                """, (today_dt,))
                logger.debug("Удалены старые записи за дату %s", today_dt)

                for active in curr_map_rub.keys():
                    cur.execute("""
                        INSERT INTO tink_invest_api.money_amount_daily(
                            report_dt,
                            active_type,
                            amount_usd,
                            amount_rub
                        ) VALUES (
                            %(report_dt)s,
                            %(active_type)s,
                            %(amount_usd)s,
                            %(amount_rub)s
                        )
                    """, {
                        "report_dt": today_dt,
                        "active_type": curr_map_rub[active]["active_type"],
                        "amount_usd": curr_map_usd[active]["amount"],
                        "amount_rub": curr_map_rub[active]["amount"]
                    })
                    logger.info(
                        "Добавлена запись: %s | RUB=%.2f | USD=%.2f",
                        active,
                        float(curr_map_rub[active]['amount']),
                        float(curr_map_usd[active]['amount'])
                    )
                pg_conn.commit()
                logger.info("Изменения сохранены в БД для аккаунта %s", acc)
            except psycopg2.Error as e:
                pg_conn.rollback()
                logger.error("Ошибка при вставке данных для аккаунта %s: %s", acc, e)

    cur.close()
    pg_conn.close()
    logger.info("Подключение к базе данных закрыто")
    logger.info("Загрузка завершена успешно")


if __name__ == "__main__":
    load_money_amount_daily()