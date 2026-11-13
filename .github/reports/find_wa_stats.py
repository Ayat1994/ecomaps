import os, json, urllib.request, urllib.parse, urllib.error
TOK = os.environ['META_TOKEN']; TG = os.environ['TG_TOKEN']; CHAT = os.environ.get('TG_CHAT_ID') or '271851854'
NUM = '77066000735'
ACCTS = ['act_335569223558023', 'act_273020681867232']
G = 'https://graph.facebook.com/v21.0/'

def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)

def pages(path, fields, limit=100, extra=None):
    q = {'fields': fields, 'limit': limit, 'access_token': TOK}
    q.update(extra or {})
    url = G + path + '?' + urllib.parse.urlencode(q)
    out = []
    while url:
        d = get(url); out += d.get('data', []); url = d.get('paging', {}).get('next')
    return out

def act(lst, t):
    for a in lst or []:
        if a['action_type'] == t: return float(a['value'])
    return 0.0

out, notes, ids = [], [], []
phone = {}
for a in ACCTS:
    try: adsets = pages(a + '/adsets', 'name,effective_status,created_time,promoted_object,campaign{name,effective_status}', 200)
    except Exception as e: notes.append(a + ' adsets: ' + str(e)[:80]); continue
    for s in adsets:
        po = s.get('promoted_object') or {}
        pid = po.get('whats_app_business_phone_number_id')
        if pid and pid not in phone:
            try: phone[pid] = ''.join(c for c in get(G + pid + '?fields=display_phone_number&access_token=' + TOK).get('display_phone_number', '') if c.isdigit())
            except Exception: phone[pid] = ''
        if (po.get('whatsapp_phone_number') or phone.get(pid, '')) == NUM:
            ids.append((a, s))
    # объявления: повторный поиск номера в креативах мелкими страницами
    n_ads = 0; hits = []
    try:
        url = G + a + '/ads?' + urllib.parse.urlencode({'fields': 'name,effective_status,created_time,creative{object_story_spec,asset_feed_spec}', 'limit': 25, 'access_token': TOK})
        while url:
            try: d = get(url)
            except urllib.error.HTTPError as e:
                notes.append(a + ' ads страница: HTTP %s' % e.code); break
            for ad in d.get('data', []):
                n_ads += 1
                if NUM in json.dumps(ad.get('creative') or {}, ensure_ascii=False):
                    hits.append('ОБЪЯВЛЕНИЕ [%s] %s' % (ad['effective_status'], ad['name'][:50]))
            url = d.get('paging', {}).get('next')
    except Exception as e: notes.append(a + ' ads: ' + str(e)[:80])
    notes.append('%s: объявлений просмотрено %d, номер в креативах: %d' % (a, n_ads, len(hits)))
    out += hits

for a, s in ids:
    try:
        ins = get(G + s['id'] + '/insights?' + urllib.parse.urlencode({'fields': 'spend,impressions,reach,inline_link_clicks,actions,cost_per_action_type,date_start,date_stop', 'date_preset': 'maximum', 'access_token': TOK})).get('data', [])
    except Exception as e: ins = []
    i = ins[0] if ins else {}
    conv = act(i.get('actions'), 'onsite_conversion.messaging_conversation_started_7d')
    sp = float(i.get('spend', 0) or 0)
    out.append('%s | кампания: %s [%s] | создана %s | потрачено $%.2f | показы %s | охват %s | клики %s | переписки %d | цена переписки %s | период %s — %s' % (
        s['name'][:45], (s.get('campaign') or {}).get('name', '')[:40], s['effective_status'], s['created_time'][:10], sp,
        i.get('impressions', 0), i.get('reach', 0), i.get('inline_link_clicks', 0), conv, ('$%.2f' % (sp / conv)) if conv else '—',
        i.get('date_start', '—'), i.get('date_stop', '—')))
msg = 'Аналитика по рекламе на +7 706 600 0735\n' + '\n\n'.join(out) + '\n\n' + '\n'.join(notes)
for c in [msg[i:i+3500] for i in range(0, len(msg), 3500)]:
    try: urllib.request.urlopen(urllib.request.Request('https://api.telegram.org/bot%s/sendMessage' % TG, data=urllib.parse.urlencode({'chat_id': CHAT, 'text': c}).encode()), timeout=30)
    except urllib.error.HTTPError as e: print('telegram error:', e.code)
print('готово, групп:', len(ids), '| заметок:', len(notes))
