#!/usr/bin/env python3
"""Продажи из МойСклад → TikTok Events API (событие CompletePayment).

Та же логика, что meta_sales.py: каждый час берёт заказы покупателей за последние
LOOKBACK_HOURS часов и отправляет их в TikTok к пикселю ecomaps.kz: сумма заказа +
телефон клиента в виде SHA-256 (номер в открытом виде TikTok не получает).
По номеру TikTok находит, какую рекламу человек видел/нажимал, и засчитывает продажу ей.

Повторы не страшны: event_id = id заказа, TikTok отбрасывает дубли.

Секреты GitHub:
  MOYSKLAD_TOKEN    — токен API МойСклад (только чтение)
  TIKTOK_EVENTS_TOKEN — токен Events API из TikTok Events Manager (пиксель ниже)
  TIKTOK_TEST_CODE  — необязательно: код «Тестовых событий» для проверки
Ничего из данных клиентов не печатается в лог (репозиторий публичный).
"""
import json, os, re, sys, datetime as dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meta_sales import env, http, sha, phone, orders, MSK  # noqa: E402

PIXEL = os.environ.get('TIKTOK_PIXEL_ID', '').strip() or 'DBQ1JJJC77UBQ4PDTHPG'
URL = 'https://business-api.tiktok.com/open_api/v1.3/event/track/'


def main():
    ms, tok = env('MOYSKLAD_TOKEN'), env('TIKTOK_EVENTS_TOKEN')
    if not ms or not tok:
        print('Нет MOYSKLAD_TOKEN или TIKTOK_EVENTS_TOKEN — пропускаю')
        return
    events, skipped = [], 0
    for o in orders(ms):
        agent = o.get('agent') or {}
        ph = phone(agent.get('phone'))
        total = (o.get('sum') or 0) / 100  # МойСклад хранит суммы в тиынах
        if not ph or total <= 0:
            skipped += 1
            continue
        created = dt.datetime.strptime(o['created'][:19], '%Y-%m-%d %H:%M:%S').replace(tzinfo=MSK)
        events.append({
            'event': 'CompletePayment',
            'event_time': int(created.timestamp()),
            'event_id': f'ms-order-{o["id"]}',
            'user': {'phone': sha('+' + ph), 'external_id': sha(agent.get('id', ph))},
            'page': {'url': 'https://ecomaps.kz/'},
            'properties': {'currency': 'KZT', 'value': round(total, 2), 'content_type': 'product',
                           'order_id': o.get('name') or o['id']},
        })
    print(f'Заказов к отправке: {len(events)}, пропущено без телефона/суммы: {skipped}')
    if not events:
        return
    sent = 0
    for i in range(0, len(events), 500):  # TikTok принимает до 1000 событий за раз
        payload = {'event_source': 'web', 'event_source_id': PIXEL, 'data': events[i:i + 500]}
        if env('TIKTOK_TEST_CODE'):
            payload['test_event_code'] = env('TIKTOK_TEST_CODE')
        st, txt = http(URL, 'POST', headers={'Access-Token': tok}, data=payload)
        try:
            res = json.loads(txt)
        except Exception:
            res = {}
        if st != 200 or res.get('code') != 0:
            print('TikTok: ошибка', st, res.get('code'), str(res.get('message', ''))[:200])
            sys.exit(1)
        sent += len(payload['data'])
    print('TikTok принял событий:', sent)


if __name__ == '__main__':
    main()
