#!/usr/bin/env python3
"""Ежедневный отчёт ECOMAPS в Telegram: реклама в ChatGPT, Meta, Яндекс Директ и Яндекс Метрика.

Ключи берутся из секретов GitHub (Settings → Secrets and variables → Actions):
  TG_TOKEN            — токен бота от @BotFather (обязательно)
  TG_CHAT_ID          — куда слать (необязательно: если пусто, бот шлёт всем, кто ему писал за сутки, и подсказывает chat_id)
  OPENAI_ADS_API_KEY  — ключ API из ads.openai.com → Настройки → API-ключи
  META_TOKEN          — токен Meta с правом ads_read
  META_AD_ACCOUNT     — ID рекламного аккаунта Meta, например act_1234567890
  YANDEX_TOKEN        — OAuth-токен Яндекса (права metrika:read и direct:api)
  DIRECT_CLIENT_LOGIN — логин клиента Директа (только для агентских аккаунтов)
Если ключа нет, раздел помечается «не подключено», остальные работают.
Ничего из данных не печатается в лог (репозиторий публичный).
"""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error, datetime as dt, html

TZ = dt.timezone(dt.timedelta(hours=5))  # Астана / Алматы
today = dt.datetime.now(TZ).date()
yday = today - dt.timedelta(days=1)
week0 = today - dt.timedelta(days=7)
YM_COUNTER = os.environ.get('YM_COUNTER', '103848088')


def env(k):
    v = os.environ.get(k, '').strip()
    return v or None


def http(url, method='GET', headers=None, data=None, timeout=60):
    body = None
    if data is not None:
        body = data if isinstance(data, bytes) else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode('utf-8', 'replace')


def num(x):
    try:
        f = float(x)
    except (TypeError, ValueError):
        return '—'
    return f'{f:,.0f}'.replace(',', ' ') if abs(f) >= 100 or f == int(f) else f'{f:,.2f}'.replace(',', ' ')


def money(x, cur='₸'):
    return '—' if x is None else f'{num(x)} {cur}'


def esc(s):
    return html.escape(str(s))


# ---------------- реклама в ChatGPT ----------------
def openai_ads():
    key = env('OPENAI_ADS_API_KEY')
    if not key:
        return '🤖 <b>Реклама в ChatGPT</b>\nне подключено (нет OPENAI_ADS_API_KEY)'
    out = ['🤖 <b>Реклама в ChatGPT</b>']
    for label, since in (('вчера', yday), ('7 дней', week0)):
        q = [('aggregation_level', 'campaign'), ('time_granularity', 'none'),
             ('time_ranges[]', json.dumps({'type': 'date_range', 'since': since.isoformat(),
                                           'until': yday.isoformat(), 'timezone': 'Asia/Aqtobe'}))]
        q += [('fields[]', f) for f in ('campaign_name', 'impressions', 'clicks', 'spend', 'conversions')]
        st, _, txt = http('https://api.ads.openai.com/v1/ad_account/insights?' + urllib.parse.urlencode(q),
                          headers={'Authorization': f'Bearer {key}', 'Accept': 'application/json'})
        if st != 200:
            out.append(f'{label}: ошибка API {st}')
            continue
        rows = json.loads(txt).get('data') or []
        imp = sum(float(r.get('impressions') or 0) for r in rows)
        clk = sum(float(r.get('clicks') or 0) for r in rows)
        conv = sum(float(r.get('conversions') or 0) for r in rows)
        sp = 0.0
        for r in rows:
            s = r.get('spend')
            if isinstance(s, dict):
                s = s.get('amount') or s.get('value')
            sp += float(s or 0)
        ctr = f'{clk / imp * 100:.1f}%' if imp else '—'
        out.append(f'{label}: показы {num(imp)} · клики {num(clk)} (CTR {ctr}) · заявки {num(conv)} · расход {money(sp)}')
    return '\n'.join(out)


# ---------------- Meta ----------------
def meta():
    tok, acc = env('META_TOKEN'), env('META_AD_ACCOUNT')
    if not (tok and acc):
        return '📘 <b>Meta (Instagram/Facebook)</b>\nне подключено (нет META_TOKEN / META_AD_ACCOUNT)'
    if not acc.startswith('act_'):
        acc = 'act_' + acc
    out = ['📘 <b>Meta (Instagram/Facebook)</b>']
    for label, preset in (('вчера', 'yesterday'), ('7 дней', 'last_7d')):
        q = urllib.parse.urlencode({'date_preset': preset, 'level': 'account', 'access_token': tok,
                                    'fields': 'spend,impressions,reach,clicks,ctr,actions,account_currency'})
        st, _, txt = http(f'https://graph.facebook.com/v21.0/{acc}/insights?{q}')
        if st != 200:
            try:
                msg = json.loads(txt)['error']['message'][:120]
            except Exception:
                msg = ''
            out.append(f'{label}: ошибка API {st} {esc(msg)}')
            continue
        d = (json.loads(txt).get('data') or [{}])
        d = d[0] if d else {}
        acts = {a['action_type']: float(a['value']) for a in d.get('actions', [])}
        msgs = acts.get('onsite_conversion.messaging_conversation_started_7d', 0)
        leads = acts.get('lead', 0) + acts.get('offsite_conversion.fb_pixel_lead', 0) + acts.get('offsite_conversion.fb_pixel_contact', 0) + acts.get('contact', 0)
        cur = {'KZT': '₸', 'USD': '$', 'RUB': '₽'}.get(d.get('account_currency', 'KZT'), d.get('account_currency', ''))
        line = (f'{label}: показы {num(d.get("impressions", 0))} · охват {num(d.get("reach", 0))} · '
                f'клики {num(d.get("clicks", 0))} · расход {money(d.get("spend", 0), cur)}')
        if msgs:
            line += f' · переписки {num(msgs)}'
        if leads:
            line += f' · заявки с сайта {num(leads)}'
        out.append(line)
    return '\n'.join(out)


# ---------------- Яндекс Директ ----------------
def direct():
    tok = env('YANDEX_TOKEN')
    if not tok:
        return '🟡 <b>Яндекс Директ</b>\nне подключено (нет YANDEX_TOKEN)'
    h = {'Authorization': f'Bearer {tok}', 'Accept-Language': 'ru', 'processingMode': 'auto',
         'returnMoneyInMicros': 'false', 'skipReportHeader': 'true', 'skipReportSummary': 'true',
         'Content-Type': 'application/json; charset=utf-8'}
    if env('DIRECT_CLIENT_LOGIN'):
        h['Client-Login'] = env('DIRECT_CLIENT_LOGIN')
    out = ['🟡 <b>Яндекс Директ</b>']
    for label, rng in (('вчера', 'YESTERDAY'), ('7 дней', 'LAST_7_DAYS')):
        body = {'params': {'SelectionCriteria': {}, 'FieldNames': ['Impressions', 'Clicks', 'Cost'],
                           'ReportName': f'tg-{label}-{today.isoformat()}', 'ReportType': 'ACCOUNT_PERFORMANCE_REPORT',
                           'DateRangeType': rng, 'Format': 'TSV', 'IncludeVAT': 'YES', 'IncludeDiscount': 'NO'}}
        txt, st = '', 0
        for _ in range(12):
            st, hd, txt = http('https://api.direct.yandex.com/json/v5/reports', 'POST', h, body)
            if st in (201, 202):
                time.sleep(int(hd.get('retryIn', 5)))
                continue
            break
        if st != 200:
            if 'error' in txt and ('53' in txt or 'нет доступа' in txt.lower()):
                return '🟡 <b>Яндекс Директ</b>\nнет доступа к Директу с этим токеном'
            out.append(f'{label}: ошибка API {st}')
            continue
        lines = [l for l in txt.strip().split('\n') if l]
        if len(lines) < 2:
            out.append(f'{label}: нет показов')
            continue
        imp, clk, cost = (lines[1].split('\t') + ['0', '0', '0'])[:3]
        out.append(f'{label}: показы {num(imp)} · клики {num(clk)} · расход {money(cost)}')
    return '\n'.join(out)


# ---------------- Яндекс Метрика (сайт) ----------------
def metrika():
    tok = env('YANDEX_TOKEN')
    if not tok:
        return '🌐 <b>Сайт ecomaps.kz (Метрика)</b>\nне подключено (нет YANDEX_TOKEN)'
    h = {'Authorization': f'OAuth {tok}'}
    st, _, txt = http(f'https://api-metrika.yandex.net/management/v1/counter/{YM_COUNTER}/goals', headers=h)
    if st != 200:
        return f'🌐 <b>Сайт ecomaps.kz (Метрика)</b>\nошибка API {st}'
    goals = {g['id']: g['name'] for g in json.loads(txt).get('goals', [])
             if g['name'].startswith('Сайт:') or g['name'] == 'Переход в WhatsApp'}
    gids = list(goals)[:6]
    metrics = ['ym:s:visits', 'ym:s:users'] + [f'ym:s:goal{g}reaches' for g in gids]

    def get(d1, dims=None, limit=8):
        q = {'ids': YM_COUNTER, 'metrics': ','.join(metrics), 'date1': d1.isoformat(), 'date2': yday.isoformat(),
             'limit': limit, 'accuracy': 'full', 'sort': '-ym:s:visits'}
        if dims:
            q['dimensions'] = dims
        st, _, t = http('https://api-metrika.yandex.net/stat/v1/data?' + urllib.parse.urlencode(q), headers=h)
        return json.loads(t) if st == 200 else None

    out = ['🌐 <b>Сайт ecomaps.kz (Метрика)</b>']
    for label, d1 in (('вчера', yday), ('7 дней', week0)):
        tot = get(d1)
        if not tot:
            out.append(f'{label}: ошибка API')
            continue
        t = tot['totals']
        parts = [f'визиты {num(t[0])}', f'посетители {num(t[1])}']
        parts += [f'{esc(goals[g].replace("Сайт: ", ""))} {num(v)}' for g, v in zip(gids, t[2:])]
        out.append(f'{label}: ' + ' · '.join(parts))
    src = get(yday, 'ym:s:lastsignUTMSource', 6)
    if src and src.get('data'):
        out.append('<i>вчера по меткам utm_source:</i>')
        for row in src['data']:
            name = row['dimensions'][0].get('name') or 'без метки'
            m = row['metrics']
            wa = [num(v) for g, v in zip(gids, m[2:]) if 'WhatsApp' in goals[g]]
            out.append(f'  • {esc(name)}: визиты {num(m[0])}' + (f', WhatsApp {" / ".join(wa)}' if wa else ''))
    return '\n'.join(out)


def main():
    tg = env('TG_TOKEN')
    if not tg:
        print('TG_TOKEN не задан')
        sys.exit(1)
    blocks = []
    for f in (openai_ads, meta, direct, metrika):
        try:
            blocks.append(f())
        except Exception as e:  # раздел не должен ронять весь отчёт
            blocks.append(f'⚠️ {f.__name__}: ошибка {type(e).__name__}')
    text = (f'📊 <b>ECOMAPS — отчёт за {yday.strftime("%d.%m.%Y")}</b>\n\n' + '\n\n'.join(blocks) +
            '\n\n<i>Google Ads: не подключено</i>')

    chats = [c.strip() for c in (env('TG_CHAT_ID') or '').split(',') if c.strip()]
    hint = False
    if not chats:
        st, _, t = http(f'https://api.telegram.org/bot{tg}/getUpdates')
        for u in json.loads(t).get('result', []):
            m = u.get('message') or u.get('channel_post') or u.get('my_chat_member') or {}
            cid = str((m.get('chat') or {}).get('id', ''))
            if cid and cid not in chats:
                chats.append(cid)
        hint = True
    if not chats:
        print('Нет получателей: напишите боту /start и запустите ещё раз')
        sys.exit(1)
    ok = 0
    for cid in chats:
        msg = text + (f'\n\n🔑 chat_id этого чата: <code>{cid}</code> — добавьте его в секрет TG_CHAT_ID' if hint else '')
        st, _, _ = http(f'https://api.telegram.org/bot{tg}/sendMessage', 'POST', {'Content-Type': 'application/json'},
                        {'chat_id': cid, 'text': msg, 'parse_mode': 'HTML', 'disable_web_page_preview': True})
        ok += st == 200
    print(f'Отправлено в {ok} из {len(chats)} чатов')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
