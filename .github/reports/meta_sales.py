#!/usr/bin/env python3
"""Продажи из МойСклад → Meta Conversions API (событие Purchase).

Каждый час берёт заказы покупателей, созданные за последние LOOKBACK_HOURS часов,
и отправляет их в Meta: сумма заказа + номер телефона и имя клиента в виде SHA-256
(Meta сама не получает номер в открытом виде). По номеру Meta находит, какую рекламу
человек видел/нажимал, и засчитывает продажу этой рекламе.

Повторы не страшны: event_id = id заказа, Meta отбрасывает дубли с тем же event_id.

Секреты GitHub:
  MOYSKLAD_TOKEN   — токен API МойСклад (только чтение)
  META_CAPI_TOKEN  — маркер Conversions API из Events Manager (пиксель/набор данных ниже)
  META_PIXEL_ID    — необязательно, по умолчанию пиксель ecomaps.kz
  META_TEST_CODE   — необязательно: код «Тестовых событий» из Events Manager для проверки
Ничего из данных клиентов не печатается в лог (репозиторий публичный).
"""
import gzip, hashlib, json, os, re, sys, time, urllib.request, urllib.parse, urllib.error, datetime as dt

PIXEL = os.environ.get('META_PIXEL_ID', '').strip() or '576043711342731'
LOOKBACK_HOURS = int(os.environ.get('LOOKBACK_HOURS', '') or 3)
MSK = dt.timezone(dt.timedelta(hours=3))  # МойСклад хранит время по Москве


def env(k):
    return (os.environ.get(k) or '').strip() or None


def http(url, method='GET', headers=None, data=None):
    h = {'User-Agent': 'ecomaps-sales-sync/1.0 (+https://ecomaps.kz)', 'Accept-Encoding': 'gzip'}
    h.update(headers or {})
    body = json.dumps(data).encode() if data is not None else None
    if body:
        h['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw, st, enc = r.read(), r.status, r.headers.get('Content-Encoding', '')
    except urllib.error.HTTPError as e:
        raw, st, enc = e.read(), e.code, e.headers.get('Content-Encoding', '')
    if enc == 'gzip' or raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    return st, raw.decode('utf-8', 'replace')


def sha(s):
    return hashlib.sha256(s.strip().lower().encode()).hexdigest()


def phone(p):
    d = re.sub(r'\D', '', p or '')
    if len(d) == 11 and d[0] == '8':
        d = '7' + d[1:]
    elif len(d) == 10:
        d = '7' + d
    return d if len(d) >= 11 else None


def orders(token):
    since = (dt.datetime.now(MSK) - dt.timedelta(hours=LOOKBACK_HOURS)).strftime('%Y-%m-%d %H:%M:%S')
    q = urllib.parse.urlencode({'filter': f'created>={since}', 'expand': 'agent', 'limit': 100, 'order': 'created,asc'})
    st, txt = http(f'https://api.moysklad.ru/api/remap/1.2/entity/customerorder?{q}',
                   headers={'Authorization': f'Bearer {token}'})
    if st != 200:
        print('МойСклад: ошибка', st)
        sys.exit(1)
    return json.loads(txt).get('rows', [])


def main():
    ms, capi = env('MOYSKLAD_TOKEN'), env('META_CAPI_TOKEN')
    if not ms or not capi:
        print('Нет MOYSKLAD_TOKEN или META_CAPI_TOKEN — пропускаю')
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
        ud = {'ph': [sha(ph)], 'country': [sha('kz')], 'external_id': [sha(agent.get('id', ph))]}
        first = (agent.get('name') or '').split()
        if first and re.match(r'^[^\d\W]+$', first[0]):
            ud['fn'] = [sha(first[0])]
        events.append({'event_name': 'Purchase', 'event_time': int(created.timestamp()),
                       'event_id': f'ms-order-{o["id"]}', 'action_source': 'physical_store',
                       'user_data': ud, 'custom_data': {'currency': 'KZT', 'value': round(total, 2),
                                                        'order_id': o.get('name') or o['id']}})
    print(f'Заказов к отправке: {len(events)}, пропущено без телефона/суммы: {skipped}')
    if not events:
        return
    payload = {'data': events}
    if env('META_TEST_CODE'):
        payload['test_event_code'] = env('META_TEST_CODE')
    st, txt = http(f'https://graph.facebook.com/v21.0/{PIXEL}/events?access_token={urllib.parse.quote(capi)}',
                   'POST', data=payload)
    try:
        res = json.loads(txt)
    except Exception:
        res = {}
    if st != 200:
        print('Meta: ошибка', st, (res.get('error') or {}).get('message', '')[:200])
        sys.exit(1)
    print('Meta приняла событий:', res.get('events_received'))


if __name__ == '__main__':
    main()
