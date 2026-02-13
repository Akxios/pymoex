import logging

from pymoex import find, get_bond, get_share

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main():

    # Получаем акцию
    share = get_share("SBER")
    print(share)  # Выводим результат

    # Получаем облигацию
    share = get_bond("RU000A10DS74")
    print(share)  # Выводим результат

    # Выполняем поиск по ключевому слову
    results = find("Сбербанк", instrument_type="share")  # instrument_type="bond"

    for r in results:
        print(r)  # Выводим результат


if __name__ == "__main__":
    main()
