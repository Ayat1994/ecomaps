#!/usr/bin/env python3
"""Заполнение таблицы «ССП Ecomaps от Claude» (лист «Метрики по дням») за вчерашний день по времени Астаны.

Что пишется (строки ищутся по названию в столбце D, столбец — по дате в строке 3):
  Потрачено денег Инста (ОП-1) / Кол-во заявок Инста (ОП-1)
  Потрачено денег (ОП-2)       / Кол-во заявок (ОП-2)
  Потрачено денег (ОП-3 Woodmaps) / Кол-во заявок (ОП-3 Woodmaps)

Правила (решение владельца 10.11.2026):
  * Кабинеты Meta живут в поясе Asia/Omsk (UTC+6), а Астана — UTC+5. Статистика берётся по часам
    и сдвигается на нужное число часов, чтобы день был 00:00–24:00 по Астане, как в amoCRM.
  * Кабинет «Ecomaps.kz» (335569223558023): кампании с «ОП1 / ОП-1 / ОП 1» в названии → ОП-1,
    с «ОП2 / ОП-2 / ОП 2» → ОП-2, кампании на сайт («Трафик | Сайт …») → делятся между ОП-1 и ОП-2,
    остальные → ОП-1.
  * Кабинет «Ecomaps ads» (273020681867232, Woodmaps) → ОП-3.
  * Заявки = переписки в WhatsApp/Direct из рекламы Meta (messaging_conversation_started_7d).
  * Реклама на сайт: распределитель ecomaps.kz/whatsapp пишет в Метрику цель «redirect» с номером.
    Переходы с рекламы Meta (utm_source=meta) на 77064299895 → заявки ОП-1, на 77762979276 → ОП-2.
    Расход кампаний сайта делится между ОП-1 и ОП-2 в той же пропорции (если переходов нет — пополам).

Секреты: META_TOKEN, YANDEX_TOKEN, SSP_WEBHOOK (адрес веб-приложения Apps Script в таблице, с ?key=…),
необязательно TG_TOKEN/TG_CHAT_ID — короткое подтверждение в Telegram.
Ручной запуск за любой день: Actions → «ССП: заполнить таблицу» → Run workflow → date=ГГГГ-ММ-ДД.
Данные в лог не печатаются (репозиторий публичный).
"""
import json, os, re, sys, urllib.parse, urllib.request, urllib.error, datetime as dt

ASTANA = dt.timezone(dt.timedelta(hours=5))
YM_COUNTER = os.environ.get('YM_COUNTER', '103848088')
ACC_MAIN, ACC_WOOD = '335569223558023', '273020681867232'
NUM_OP1, NUM_OP2 = '77064299895', '77762979276'
CONV = 'onsite_conversion.messaging_conversation_started_7d'
RE_OP1 = re.compile(r'оп\s*-?\s*1(?!\d)', re.I)
RE_OP2 = re.compile(r'оп\s*-?\s*2(?!\d)', re.I)
RE_SITE = re.compile(r'трафик\s*\|\s*сайт', re.I)


def env(k):
    v = os.environ.get(k, '').strip()
    return v or None


def http(url, data=None, headers=None, timeout=90):
    body = json.dumps(data).encode() if data is not None else None
    h = {'User-Agent': 'ecomaps-ssp/1.0', 'Accept': 'application/json'}
    if body is not None:
        h['Content-Type'] = 'application/json'
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, headers=h, method='POST' if body is not None else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')


def meta_hourly(acc, day, tok):
    """[(campaign_name, spend, conversations)] за сутки `day` по Астане (почасовые данные со сдвигом пояса)."""
    st, txt = http(f'https://graph.facebook.com/v21.0/act_{acc}?fields=timezone_offset_hours_utc&access_token={tok}')
    if st != 200:
        raise RuntimeError(f'Meta {acc}: ошибка {st}')
    shift = float(json.loads(txt).get('timezone_offset_hours_utc', 6)) - 5  # на сколько часов кабинет «впереди» Астаны
    q = {'level': 'campaign', 'time_increment': 1, 'limit': 500, 'access_token': tok,
         'breakdowns': 'hourly_stats_aggregated_by_advertiser_time_zone', 'fields': 'campaign_name,spend,actions',
         'time_range': json.dumps({'since': (day - dt.timedelta(days=1)).isoformat(),
                                   'until': (day + dt.timedelta(days=1)).isoformat()})}
    url = f'https://graph.facebook.com/v21.0/act_{acc}/insights?' + urllib.parse.urlencode(q)
    rows = []
    while url:
        st, txt = http(url)
        if st != 200:
            raise RuntimeError(f'Meta {acc}: ошибка {st}')
        j = json.loads(txt)
        for x in j.get('data', []):
            h = int(x['hourly_stats_aggregated_by_advertiser_time_zone'][:2])
            t = dt.datetime.fromisoformat(x['date_start']) + dt.timedelta(hours=h - shift)
            if t.date() != day:
                continue
            conv = sum(float(a['value']) for a in x.get('actions', []) if a['action_type'] == CONV)
            rows.append((x.get('campaign_name', ''), float(x.get('spend', 0) or 0), conv))
        url = (j.get('paging') or {}).get('next')
    return rows


def site_redirects(day, tok):
    """Сколько переходов с рекламы Meta распределитель отправил на номер ОП-1 и ОП-2 (по данным Метрики)."""
    q = {'ids': YM_COUNTER, 'metrics': 'ym:s:visits', 'date1': day.isoformat(), 'date2': day.isoformat(),
         'dimensions': 'ym:s:paramsLevel1,ym:s:paramsLevel2', 'accuracy': 'full', 'limit': 100,
         'filters': "ym:s:lastsignUTMSource=='meta' AND ym:s:paramsLevel1=='to'"}
    st, txt = http('https://api-metrika.yandex.net/stat/v1/data?' + urllib.parse.urlencode(q),
                   headers={'Authorization': f'OAuth {tok}'})
    if st != 200:
        raise RuntimeError(f'Метрика: ошибка {st}')
    op1 = op2 = 0
    for x in json.loads(txt).get('data', []):
        url = str(x['dimensions'][1].get('name') or '')
        n = x['metrics'][0] or 0
        if NUM_OP1 in url:
            op1 += n
        elif NUM_OP2 in url:
            op2 += n
    return int(op1), int(op2)


def main():
    day = env('SSP_DATE')
    day = dt.date.fromisoformat(day) if day else dt.datetime.now(ASTANA).date() - dt.timedelta(days=1)
    mt, yt, hook = env('META_TOKEN'), env('YANDEX_TOKEN'), env('SSP_WEBHOOK')
    if not (mt and hook):
        print('ССП: пропуск — не задан секрет META_TOKEN или SSP_WEBHOOK')
        return

    sp = {'op1': 0.0, 'op2': 0.0, 'op3': 0.0, 'site': 0.0}
    cv = {'op1': 0.0, 'op2': 0.0, 'op3': 0.0}
    for name, s, c in meta_hourly(ACC_MAIN, day, mt):
        k = 'site' if RE_SITE.search(name) else 'op2' if RE_OP2.search(name) else 'op1'
        sp[k] += s
        if k != 'site':
            cv[k] += c
    for _, s, c in meta_hourly(ACC_WOOD, day, mt):
        sp['op3'] += s
        cv['op3'] += c

    r1 = r2 = 0
    note = ''
    if yt:
        try:
            r1, r2 = site_redirects(day, yt)
        except RuntimeError as e:
            note = str(e)
    share1 = r1 / (r1 + r2) if (r1 + r2) else 0.5
    sp1 = sp['op1'] + sp['site'] * share1
    sp2 = sp['op2'] + sp['site'] * (1 - share1)

    values = {
        'Потрачено денег Инста (ОП-1)': round(sp1, 2),
        'Кол-во заявок Инста (ОП-1)': int(round(cv['op1'] + r1)),
        'Потрачено денег (ОП-2)': round(sp2, 2),
        'Кол-во заявок (ОП-2)': int(round(cv['op2'] + r2)),
        'Потрачено денег (ОП-3 Woodmaps)': round(sp['op3'], 2),
        'Кол-во заявок (ОП-3 Woodmaps)': int(round(cv['op3'])),
    }
    st, txt = http(hook, data={'date': day.strftime('%d.%m.%Y'), 'values': values})
    try:
        res = json.loads(txt)
    except Exception:
        res = {'ok': False, 'err': f'ответ {st}'}
    ok = bool(res.get('ok'))
    print('ССП', day.isoformat(), 'записано' if ok else 'ОШИБКА', '' if ok else str(res.get('err', ''))[:120])

    tg = env('TG_TOKEN')
    if tg:
        msg = (f'📊 ССП за {day.strftime("%d.%m")} (время Астаны) ' + ('заполнена' if ok else f'НЕ заполнена: {res.get("err")}') +
               f'\nОП-1: ${sp1:.2f} · заявок {values["Кол-во заявок Инста (ОП-1)"]}'
               f'\nОП-2: ${sp2:.2f} · заявок {values["Кол-во заявок (ОП-2)"]}'
               f'\nОП-3 Woodmaps: ${sp["op3"]:.2f} · заявок {values["Кол-во заявок (ОП-3 Woodmaps)"]}'
               + (f'\nСайт: ${sp["site"]:.2f}, переходы с Meta → ОП-1 {r1}, ОП-2 {r2}' if sp['site'] or r1 or r2 else '')
               + (f'\n⚠️ {note}' if note else ''))
        http(f'https://api.telegram.org/bot{tg}/sendMessage',
             data={'chat_id': env('TG_CHAT_ID') or '271851854', 'text': msg})
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
