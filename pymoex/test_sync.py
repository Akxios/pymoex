import logging

from pymoex import find_shares, get_share

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Получить акцию
try:
    share = get_share("SBER")
    print(share)
except Exception as e:
    print(f"Ошибка: {e}")

# Поиск
shares = find_shares("SBER")
print(shares)
