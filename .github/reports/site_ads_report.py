#!/usr/bin/env python3
"""Отчёт «Реклама Meta на сайт» по городам и креативам за сегодня (по Астане) → Telegram.

Meta: расход и просмотры целевой страницы по каждому объявлению кампаний «Трафик | Сайт …»
(название объявления = «Город | креатив»). Кабинет живёт в Asia/Omsk, поэтому берутся почасовые
данные и сдвигаются к суткам Астаны.
Метрика: визиты по utm_content (= название объявления), среднее время, посчитали цену,
нажали WhatsApp. Только визиты из Казахстана; прочие страны одной строкой (в Мете часто ночные пачки из Ирландии). Данные в лог не печатаются (репозиторий публичный), только в Telegram.
Ручной запуск: Actions → «Реклама на сайт: отчёт сейчас» → Run workflow (date — необязательно).
"""
import json, os, sys, urllib.parse, urllib.request, urllib.error, datetime as dt
from html import escape

ASTANA = dt.timezone(dt.timedelta(hours=5))
ACC = os.environ.get('META_AD_ACCOUNT_SITE', '335569223558023')
YM = os.environ.get('YM_COUNTER', '103848088')
CAMP = 'Трафик | Сайт'


def env(k):
    v = os.environ.get(k, '').strip()
    return v or None


def http(url, data=None, headers=None):
    body = json.dumps(data).encode() if data is not None else None
    h = {'User-Agent': 'ecomaps-site-ads/1.0', 'Accept': 'application/json'}
    if body is not None:
        h['Content-Type'] = 'application/json'
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, headers=h, method='POST' if body is not None else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')


def meta(day, tok):
    st, txt = http(f'https://graph.facebook.com/v21.0/act_{ACC}?fields=timezone_offset_hours_utc&access_token={tok}')
    if st != 200:
        raise RuntimeError(f'Meta: ошибка {st}')
    shift = float(json.loads(txt).get('timezone_offset_hours_utc', 6)) - 5
    q = {'level': 'ad', 'time_increment': 1, 'limit': 500, 'access_token': tok,
         'breakdowns': 'hourly_stats_aggregated_by_advertiser_time_zone', 'fields': 'ad_name,spend,actions',
         'filtering': json.dumps([{'field': 'campaign.name', 'operator': 'CONTAIN', 'value': CAMP}]),
         'time_range': json.dumps({'since': day.isoformat(), 'until': (day + dt.timedelta(days=1)).isoformat()})}
    url = f'https://graph.facebook.com/v21.0/act_{ACC}/insights?' + urllib.parse.urlencode(q)
    out = {}
    while url:
        st, txt = http(url)
        if st != 200:
            raise RuntimeError(f'Meta: ошибка {st}')
        j = json.loads(txt)
        for x in j.get('data', []):
            h = int(x['hourly_stats_aggregated_by_advertiser_time_zone'][:2])
            if (dt.datetime.fromisoformat(x['date_start']) + dt.timedelta(hours=h - shift)).date() != day:
                continue
            a = out.setdefault(x['ad_name'], [0.0, 0])
            a[0] += float(x.get('spend', 0) or 0)
            a[1] += sum(int(float(v['value'])) for v in x.get('actions', []) if v['action_type'] == 'landing_page_view')
        url = (j.get('paging') or {}).get('next')
    return out


def metrika(day, tok, country='in'):
    h = {'Authorization': f'OAuth {tok}'}
    st, txt = http(f'https://api-metrika.yandex.net/management/v1/counter/{YM}/goals', headers=h)
    if st != 200:
        raise RuntimeError(f'Метрика: ошибка {st}')
    goals = {g['name']: g['id'] for g in json.loads(txt).get('goals', [])}
    gw, gc = goals.get('Сайт: клик WhatsApp'), goals.get('Сайт: расчёт цены')
    metrics = ['ym:s:visits', 'ym:s:avgVisitDurationSeconds'] + [f'ym:s:goal{g}reaches' for g in (gc, gw) if g]
    q = {'ids': YM, 'date1': day.isoformat(), 'date2': day.isoformat(), 'accuracy': 'full', 'limit': 200,
         'dimensions': 'ym:s:lastsignUTMContent', 'metrics': ','.join(metrics),
         'filters': "ym:s:lastsignUTMSource=='meta' AND ym:s:lastsignUTMContent=@'|' AND ym:s:regionCountry" + ("=='Казахстан'" if country == 'in' else "!='Казахстан'")}
    st, txt = http('https://api-metrika.yandex.net/stat/v1/data?' + urllib.parse.urlencode(q), headers=h)
    if st != 200:
        raise RuntimeError(f'Метрика: ошибка {st}')
    out = {}
    for x in json.loads(txt).get('data', []):
        m = x['metrics']
        calc = m[2] if gc else 0
        wa = m[3] if (gc and gw) else (m[2] if gw else 0)
        k = urllib.parse.unquote_plus(x['dimensions'][0]['name'])
        o = out.setdefault(k, [0, 0.0, 0, 0])
        o[0] += int(m[0]); o[1] = float(m[1]); o[2] += int(calc); o[3] += int(wa)
    return out


def agg(keys, meta_d, ym_d, f):
    res = {}
    for k in keys:
        g = f(k)
        r = res.setdefault(g, [0.0, 0, 0, 0.0, 0, 0])  # расход, просмотры, визиты, сек*визиты, расчёт, WA
        s, l = meta_d.get(k, [0.0, 0])
        v, d, c, w = ym_d.get(k, [0, 0.0, 0, 0])
        r[0] += s; r[1] += l; r[2] += v; r[3] += d * v; r[4] += c; r[5] += w
    return res


def lines(res):
    out = []
    for g, r in sorted(res.items(), key=lambda kv: -kv[1][0]):
        avg = round(r[3] / r[2]) if r[2] else 0
        cpw = f' · ${r[0] / r[5]:.2f}/WA' if r[5] else ''
        out.append(f'<b>{escape(g)}</b>: ${r[0]:.2f} · просм {r[1]} · визиты {r[2]} ({avg} с) · расчёт {r[4]} · WhatsApp {r[5]}{cpw}')
    return out


def main():
    d = env('REPORT_DATE')
    day = dt.date.fromisoformat(d) if d else dt.datetime.now(ASTANA).date()
    mt, yt, tg = env('META_TOKEN'), env('YANDEX_TOKEN'), env('TG_TOKEN')
    notes = []
    try:
        md = meta(day, mt) if mt else {}
    except RuntimeError as e:
        md, _ = {}, notes.append(str(e))
    try:
        yd = metrika(day, yt) if yt else {}
    except RuntimeError as e:
        yd, _ = {}, notes.append(str(e))
    try:
        fd = metrika(day, yt, 'out') if yt else {}
    except RuntimeError as e:
        fd, _ = {}, notes.append(str(e))
    f_vis, f_wa = sum(v[0] for v in fd.values()), sum(v[3] for v in fd.values())
    keys = set(md) | set(yd)
    norm = lambda k: [p.strip() for p in k.split('|')] + ['', '']
    tot = agg(keys, md, yd, lambda k: 'Итого')['Итого'] if keys else [0, 0, 0, 0, 0, 0]
    now = dt.datetime.now(ASTANA).strftime('%H:%M')
    msg = [f'🌐 <b>Реклама Meta на сайт</b> — {day.strftime("%d.%m")} (по Астане, на {now})',
           f'Итого: ${tot[0]:.2f} · просмотры {tot[1]} · визиты {tot[2]} · расчёт цены {tot[4]} · <b>WhatsApp {tot[5]}</b>'
           + (f' · ${tot[0] / tot[5]:.2f} за WhatsApp' if tot[5] else ''),
           '', '🎬 <b>Креативы</b>'] + lines(agg(keys, md, yd, lambda k: norm(k)[1])) + \
          ['', '🏙 <b>Города</b>'] + lines(agg(keys, md, yd, lambda k: norm(k)[0]))
    if f_vis:
        msg += ['', f'🌍 Вне Казахстана (в таблицы выше не входят): визитов {f_vis}, кликов WhatsApp {f_wa}']
    if notes:
        msg += ['', '⚠️ ' + '; '.join(notes)]
    text = '\n'.join(msg)
    if tg:
        st, _ = http(f'https://api.telegram.org/bot{tg}/sendMessage',
                     data={'chat_id': env('TG_CHAT_ID') or '271851854', 'text': text, 'parse_mode': 'HTML'})
        print('Telegram:', st)
    print('объявлений:', len(keys), '| ошибок:', len(notes), notes)


if __name__ == '__main__':
    main()
