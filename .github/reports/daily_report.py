#!/usr/bin/env python3
"""Ежедневный отчёт ECOMAPS (по понедельникам — ещё и отдельный за неделю) в Telegram: реклама в ChatGPT, Meta, Яндекс Директ и Яндекс Метрика.

Ключи берутся из секретов GitHub (Settings → Secrets and variables → Actions):
  TG_TOKEN            — токен бота от @BotFather (обязательно)
  TG_CHAT_ID          — куда слать (необязательно: если пусто, бот шлёт всем, кто ему писал за сутки, и подсказывает chat_id)
  OPENAI_ADS_API_KEY  — ключ API из ads.openai.com → Настройки → API-ключи
  META_TOKEN          — токен Meta с правом ads_read
  META_AD_ACCOUNT     — необязательно: ID рекламных аккаунтов через запятую (по умолчанию все 3 аккаунта Ecomaps company)
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
DAY = [('вчера', yday, 'yesterday', 'YESTERDAY')]
WEEK = [('за неделю', week0, 'last_7d', 'LAST_7_DAYS')]
PER = DAY  # текущий период отчёта (меняется в main)
YM_COUNTER = os.environ.get('YM_COUNTER', '103848088')
DEFAULT_CHAT = '271851854'  # личный чат владельца с ботом @ecomaps_ads_report_bot


def env(k):
    v = os.environ.get(k, '').strip()
    return v or None


def http(url, method='GET', headers=None, data=None, timeout=60):
    body = None
    if data is not None:
        body = data if isinstance(data, bytes) else json.dumps(data).encode()
    h = {'User-Agent': 'ecomaps-daily-report/1.0 (+https://ecomaps.kz)', 'Accept': 'application/json'}
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode('utf-8', 'replace')


def err(st, txt):
    try:
        j = json.loads(txt)
        m = j.get('error', j)
        if isinstance(m, dict):
            m = m.get('message') or m.get('error_detail') or m.get('error_string') or m.get('detail') or json.dumps(m)[:150]
        return f'ошибка {st}: {esc(str(m)[:150])}'
    except Exception:
        return f'ошибка {st}: {esc(txt[:150])}'


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
    for label, since, _, _ in PER:
        q = [('aggregation_level', 'campaign'), ('time_granularity', 'none'),
             ('time_ranges[]', json.dumps({'type': 'date_range', 'since': since.isoformat(),
                                           'until': yday.isoformat(), 'timezone': 'Asia/Aqtobe'}))]
        q += [('fields[]', f) for f in ('campaign_name', 'impressions', 'clicks', 'spend', 'conversions')]
        st, _, txt = http('https://api.ads.openai.com/v1/ad_account/insights?' + urllib.parse.urlencode(q),
                          headers={'Authorization': f'Bearer {key}', 'Accept': 'application/json'})
        if st != 200:
            out.append(f'{label}: {err(st, txt)}')
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
# Рекламные аккаунты бизнеса «Ecomaps company» (ID не секретные). Можно переопределить секретом META_AD_ACCOUNT через запятую.
META_ACCOUNTS = {'3415680628696876': 'Ecomaps Ads 2', '273020681867232': 'Ecomaps ads', '335569223558023': 'Ecomaps.kz - Аят'}


def meta():
    tok = env('META_TOKEN')
    if not tok:
        return '📘 <b>Meta (Instagram/Facebook)</b>\nне подключено (нет META_TOKEN)'
    accs = [a.strip().replace('act_', '') for a in (env('META_AD_ACCOUNT') or ','.join(META_ACCOUNTS)).split(',') if a.strip()]
    out = ['📘 <b>Meta (Instagram/Facebook)</b>']
    any_rows = False
    for acc in accs:
        lines = []
        for label, _, preset, _ in PER:
            q = urllib.parse.urlencode({'date_preset': preset, 'level': 'account', 'access_token': tok,
                                        'fields': 'spend,impressions,reach,clicks,actions,account_currency'})
            st, _, txt = http(f'https://graph.facebook.com/v21.0/act_{acc}/insights?{q}')
            if st != 200:
                try:
                    msg = json.loads(txt)['error']['message'][:100]
                except Exception:
                    msg = ''
                lines.append(f'{label}: ошибка API {st} {esc(msg)}')
                continue
            d = json.loads(txt).get('data') or []
            if not d:
                continue
            d = d[0]
            acts = {a['action_type']: float(a['value']) for a in d.get('actions', [])}
            msgs = acts.get('onsite_conversion.messaging_conversation_started_7d', 0)
            # лиды внутри Meta: лид-форма в Instagram/Facebook или чат, отмеченный как «лид»
            meta_leads = acts.get('onsite_conversion.lead_grouped', acts.get('onsite_conversion.lead', 0))
            # заявки с нашего сайта — события пикселя Meta на ecomaps.kz
            leads = sum(acts.get(k, 0) for k in ('offsite_conversion.fb_pixel_lead', 'offsite_conversion.fb_pixel_contact'))
            cur = {'KZT': '₸', 'USD': '$', 'RUB': '₽'}.get(d.get('account_currency', 'KZT'), d.get('account_currency', ''))
            line = (f'{label}: показы {num(d.get("impressions", 0))} · охват {num(d.get("reach", 0))} · '
                    f'клики {num(d.get("clicks", 0))} · расход {money(d.get("spend", 0), cur)}')
            if msgs:
                line += f' · переписки {num(msgs)}'
            if meta_leads:
                line += f' · лиды в Meta {num(meta_leads)}'
            if leads:
                line += f' · заявки с сайта {num(leads)}'
            if env('META_DEBUG'):
                line += '\n<code>' + esc(', '.join(f'{k}={num(v)}' for k, v in sorted(acts.items()))) + '</code>'
            lines.append(line)
        if lines:
            any_rows = True
            out.append(f'<i>{esc(META_ACCOUNTS.get(acc, acc))}</i>\n' + '\n'.join(lines))
    if not any_rows:
        out.append('показов не было')
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
    for label, _, _, rng in PER:
        body = {'params': {'SelectionCriteria': {}, 'FieldNames': ['Impressions', 'Clicks', 'Cost'],
                           'ReportName': f'tg-{rng}-{today.isoformat()}', 'ReportType': 'ACCOUNT_PERFORMANCE_REPORT',
                           'DateRangeType': rng, 'Format': 'TSV', 'IncludeVAT': 'YES', 'IncludeDiscount': 'NO'}}
        txt, st = '', 0
        for _ in range(12):
            st, hd, txt = http('https://api.direct.yandex.com/json/v5/reports', 'POST', h, body)
            if st in (201, 202):
                time.sleep(int(hd.get('retryIn', 5)))
                continue
            break
        if st != 200:
            if 'не подключен к Яндекс.Директу' in txt:
                return '🟡 <b>Яндекс Директ</b>\nне подключено: у логина Яндекса нет аккаунта Директа'
            if 'заявку на доступ' in txt:
                return '🟡 <b>Яндекс Директ</b>\nреклама не запущена · ждём одобрения доступа к статистике'
            out.append(f'{label}: {err(st, txt)}')
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

    def get(d1, dims=None, limit=8, filters=None):
        q = {'ids': YM_COUNTER, 'metrics': ','.join(metrics), 'date1': d1.isoformat(), 'date2': yday.isoformat(),
             'limit': limit, 'accuracy': 'full', 'sort': '-ym:s:visits'}
        if dims:
            q['dimensions'] = dims
        if filters:
            q['filters'] = filters
        st, _, t = http('https://api-metrika.yandex.net/stat/v1/data?' + urllib.parse.urlencode(q), headers=h)
        return json.loads(t) if st == 200 else None

    # ecomaps.kz/whatsapp — страница-распределитель номеров, на неё ведёт ссылка из шапки Instagram.
    # Визит, НАЧАВШИЙСЯ с /whatsapp, — переход из шапки; остальные визиты — сайт.
    IG = "ym:s:startURLPath=~'^/(whatsapp|wa)/?$'"
    SITE = "ym:s:startURLPath!~'^/(whatsapp|wa)/?$'"
    wa = [i for i, g in enumerate(gids) if goals[g] == 'Переход в WhatsApp']
    wi = 2 + wa[0] if wa else None
    site_g = [(i, g) for i, g in enumerate(gids) if goals[g].startswith('Сайт:') and 'WhatsApp' not in goals[g]]

    out = ['🌐 <b>Сайт ecomaps.kz</b>']
    for label, d1, _, _ in PER:
        r = get(d1, filters=SITE)
        if not r:
            out.append(f'{label}: ошибка API')
            continue
        t = r['totals']
        parts = [f'визиты {num(t[0])}']
        if wi is not None:
            parts.append(f'перешли в WhatsApp {num(t[wi])}')
        parts += [f'{esc(goals[g].replace("Сайт: ", ""))} {num(t[2 + i])}' for i, g in site_g]
        out.append(f'{label}: ' + ' · '.join(parts))
    src = get(PER[0][1], 'ym:s:lastsignUTMSource', 5, SITE)
    rows = [x for x in (src or {}).get('data', []) if x['metrics'][0]]
    if rows:
        out.append('  откуда пришли: ' + ', '.join(
            f"{esc(x['dimensions'][0].get('name') or 'без метки')} {num(x['metrics'][0])}" for x in rows))

    if wi is not None:
        # прямые ссылки на распределитель: шапка Instagram, Google Карты, 2ГИС и т.д. — различаем по utm_source
        names = {'': '📲 Шапка Instagram', 'ig': '📲 Шапка Instagram', 'google': '📍 Google Карты',
                 '2gis': '📍 2ГИС', 'yandex_maps': '📍 Яндекс Карты', 'meta': '📘 Реклама Meta'}
        r = get(PER[0][1], 'ym:s:lastsignUTMSource', 10, IG)
        agg = {}
        for x in (r or {}).get('data', []):
            src = (x['dimensions'][0].get('name') or '').lower()
            label = names.get(src, f'🔗 {esc(src)}')
            agg[label] = agg.get(label, 0) + (x['metrics'][wi] or 0)
        out.append(f'\n<b>Прямые переходы в WhatsApp</b> ({PER[0][0]}):')
        if not agg:
            out.append('нет')
        for label, n in sorted(agg.items(), key=lambda kv: -kv[1]):
            out.append(f'{label}: {num(n)}')
    return '\n'.join(out)


def main():
    tg = env('TG_TOKEN')
    if not tg:
        print('TG_TOKEN не задан')
        sys.exit(1)
    global PER
    texts = []
    periods = [('day', DAY)]
    if today.weekday() == 0 or env('REPORT_WEEK'):  # по понедельникам — ещё и отчёт за неделю
        periods.append(('week', WEEK))
    for kind, per in periods:
        PER = per
        blocks = []
        for f in (openai_ads, meta, direct, metrika):
            try:
                blocks.append(f())
            except Exception as e:  # раздел не должен ронять весь отчёт
                blocks.append(f'⚠️ {f.__name__}: ошибка {type(e).__name__}')
        title = (f'📊 <b>ECOMAPS — отчёт за {yday.strftime("%d.%m.%Y")}</b>' if kind == 'day' else
                 f'📅 <b>ECOMAPS — отчёт за неделю {week0.strftime("%d.%m")}–{yday.strftime("%d.%m.%Y")}</b>')
        texts.append(title + '\n\n' + '\n\n'.join(blocks))

    chats = [c.strip() for c in (env('TG_CHAT_ID') or DEFAULT_CHAT).split(',') if c.strip()]
    hint = False
    st, _, me = http(f'https://api.telegram.org/bot{tg}/getMe')
    try:
        print('Бот:', '@' + json.loads(me)['result']['username'])
    except Exception:
        print('Токен бота не принят Telegram (getMe', st, ') — проверьте секрет TG_TOKEN')
        sys.exit(1)
    if not chats:
        st, _, t = http(f'https://api.telegram.org/bot{tg}/getUpdates')
        res = json.loads(t)
        if not res.get('ok'):
            print('getUpdates:', st, res.get('description', '')[:120])
        for u in res.get('result', []):
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
      for text in texts:
        msg = text + (f'\n\n🔑 chat_id этого чата: <code>{cid}</code> — добавьте его в секрет TG_CHAT_ID' if hint else '')
        st, _, _ = http(f'https://api.telegram.org/bot{tg}/sendMessage', 'POST', {'Content-Type': 'application/json'},
                        {'chat_id': cid, 'text': msg, 'parse_mode': 'HTML', 'disable_web_page_preview': True})
        ok += st == 200
    print(f'Отправлено сообщений: {ok} из {len(chats) * len(texts)}')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
