# Документация по облигациям (Bonds)

[← Вернуться к README](../README.md)

Здесь собраны основные поля, которые возвращает MOEX ISS API для рынка облигаций, и их соответствие типам в `pymoex`. Посмотреть все поля можно тут: https://iss.moex.com/iss/engines/stock/markets/bonds/

## Поля используемые в Московской бирже
### Securities (Инструменты)
Статические параметры выпуска (меняются редко).

| Поле (API) | Атрибут в SDK | Тип в Python | Описание |
| --- | --- | --- | --- |
| **Идентификация** |  |  |  |
| `SECID` | `sec_id` | `str` | Идентификатор финансового инструмента |
| `BOARDID` | `board_id` | `str` | Идентификатор режима торгов |
| `ISIN` | `isin` | `str` | ISIN |
| `SHORTNAME` | `short_name` | `str`  | Краткое наименование ценной бумаги |
| `SECNAME` | `name` |  `str` | Наименование финансового инструмента |
| `REGNUMBER` | `reg_number` |  `str` | Регистрационный номер |
| `STATUS` | `status` |  `str` | Статус |
| `LISTLEVEL` | `list_level` |  `int` | Уровень листинга |
| `SECTYPE` | `sec_type` |  `str` | Тип ценной бумаги |
| `BONDTYPE` | `bond_type` |  `str` | Вид облигации |
| `BONDSUBTYPE` | `bond_sub_type` | `str` | Подвид облигации |
| **Параметры номинала** |  |  |
| `FACEVALUE` | `face_value` |  `Decimal` | Непогашенный долг |
| `FACEUNIT` | `face_unit` |  `str` | Валюта номинала |
| `CURRENCYID` | `currency_id` |  `str` | Валюта, в которой проводятся расчеты по сделкам |
| `LOTSIZE` | `lot_size` |  `int` | Размер лота |
| `LOTVALUE` | `lot_value` |  `Decimal` | Номинальная стоимость лота, в валюте номинала |
| `MINSTEP` | `min_step` |  `Decimal` | Мин. шаг цены |
| `ISSUESIZEPLACED` | `issue_size_placed` |  `int` | Количество ценных бумаг в обращении |
| **Купоны и доходность** |  |  |
| `COUPONVALUE` | `coupon_value` |  `Decimal` | Сумма купона, в валюте номинала |
| `COUPONPERCENT` | `coupon_percent` |  `Decimal` | Ставка купона, % |
| `ACCRUEDINT` | `accruedint` |  `Decimal` | НКД на дату расчетов, в валюте расчетов |
| `NEXTCOUPON` | `next_coupon` |  `date` | Дата окончания купона |
| `COUPONPERIOD` | `coupon_period` |  `int` | Длительность купона |
| **Календарь и цены** |  |  |
| `MATDATE` | `mat_date` |  `date` | Дата погашения |
| `BUYBACKDATE` | `buyback_date` |  `date` | Дата, к кот.рассч.доходность |
| `BUYBACKPRICE` | `buyback_price` |  `Decimal` | Цена оферты |
| `OFFERDATE` | `offer_date` |  `date` | Дата Оферты |
| `PREV` | `prev` |  `Decimal` | Цена последней сделки предыдущего торгового дня, % от номинала |
| `PREVPRICE` | `prev_price` |  `Decimal` | Цена последней сделки пред. дня, % к номиналу |
| `PREVWAPRICE` | `prev_weighted_price` |  `Decimal` | Средневзвешенная цена предыдущего дня, % к номиналу |
| `YIELDATPREVWAPRICE` |  `yield_at_prev_weighted_price` |  `Decimal` | Доходность по оценке пред. дня |

### Marketdata (Ход торгов)
Динамические данные, обновляемые в реальном времени в ходе сессии.


| Поле (API) | Атрибут в SDK | Тип в Python | Описание |
| --- | --- | --- | --- |
| **Цены (% от номинала)** |  |  |
| `LAST` |  `price_percent` |  `Decimal` | Цена последней сделки, % |
| `OPEN` |  `open_price` |  `Decimal` | Цена первой сделки, % к номиналу |
| `CLOSE` |  `close_price` |  `Decimal` | Цена последней сделки, % |
| `LOW` |  `low_price` |  `Decimal` | Минимальная цена сделки, % к номиналу |
| `HIGH` |  `high_price` |  `Decimal` | Максимальная цена сделки, % к номиналу |
| `WAPRICE` |  `weighted_price` |  `Decimal` | Средневзвешенная цена, % к номиналу |
| `LCLOSEPRICE` | `lclose_price` |  `Decimal` | Цена закрытия |
| `PREVLEGALCLOSEPRICE` | `prev_close_price` |  `Decimal` | Официальная цена закрытия предыдущего дня |
| **Спрос и предложение** | | |
| `BID` | `bid` |  `Decimal` | Цена спроса (котировка на покупку) на момент окончания торговой сессии, % от номинала |
| `OFFER` | `offer` |  `Decimal` | Цена предложения (котировка на продажу) на момент окончания торговой сессии, % от номинала |
| `SPREAD` | `spread` |  `Decimal` | Разница между лучшей котировкой на продажу и покупку (спред), % к номиналу |
| `BIDDEPTHT` | `bid_deptht` |  `int` | Совокупный спрос |
| `OFFERDEPTHT` | `offer_deptht` |  `int` | Общий объем котировок на продажу, лотов |
| **Активность и объемы** | | |
| `NUMTRADES` | `num_trades` |  `int` | Количество заключенных сделок, штук |
| `VOLTODAY` | `volume_today` |  `int` | Объем заключенных сделок в единицах ценных бумаг, штук |
| `VALTODAY` | `value_today` |  `Decimal` | Объем в валюте, в которой проводятся расчеты по сделкам |
| `QTY` | `qty` |  `int` | Объем последней сделки, лотов |
| `VALUE` | `value` |  `Decimal` | Объем последней сделки, руб. |
| **Расчетные показатели** | | |
| `YIELD` | `last_yield` |  `Decimal` | Доходность по последней сделке |
| `EFFECTIVEYIELD` | `effective_yield` |  `Decimal` | Эффективная доходность |
| `YIELDATWAPRICE`| `yield_at_weighted_price` |  `Decimal` | Доходность по средневзвешенной цене, % годовых |
| `DURATION` | `duration` |  `int` | Дюрация, дней |
| `LASTCHANGE` | `last_change` |  `Decimal` | Изменение цены последней сделки к цене последней сделки предыдущего торгового дня |
| **Служебная информация** | | |
| `TRADINGSTATUS` | `trading_status` |  `str` | Состояние торговой сессии |

## Пример использования в коде
Благодаря типизации, работа с полями выглядит так:


```python
# Получаем данные по облигации
bond = await client.bond("RU000A10DS74")

print(f"Название: {bond.short_name}")
print(f"Текущая цена: {bond.last_price}%")
print(f"Доходность: {bond.effective_yield}%")
print(f"Ближайший купон: {bond.next_coupon} ({bond.coupon_value} {bond.face_unit})")
```

[← Вернуться к README](../README.md)
