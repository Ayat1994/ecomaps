import os, json, urllib.request, urllib.parse, urllib.error
TOK = os.environ['META_TOKEN']; TG = os.environ['TG_TOKEN']; CHAT = os.environ.get('TG_CHAT_ID') or '271851854'
NUM = '77066000735'
ACCTS = ['act_335569223558023', 'act_273020681867232']
G = 'https://graph.facebook.com/v21.0/'

def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)

def pages(path, fields, extra=''):
    url = G + path + '?' + urllib.parse.urlencode({'fields': fields, 'limit': 200, 'access_token': TOK}) + extra
    out = []
    while url:
        d = get(url); out += d.get('data', []); url = d.get('paging', {}).get('next')
    return out

lines, notes = [], []
phone_ids = {}
for a in ACCTS:
    try:
        adsets = pages(a + '/adsets', 'name,effective_status,created_time,promoted_object,campaign{name}')
    except Exception as e:
        notes.append(a + ' adsets: ' + str(e)[:100]); continue
    for s in adsets:
        po = s.get('promoted_object') or {}
        pid = po.get('whats_app_business_phone_number_id')
        if pid and pid not in phone_ids:
            try: phone_ids[pid] = get(G + pid + '?fields=display_phone_number&access_token=' + TOK).get('display_phone_number', '')
            except Exception as e: phone_ids[pid] = ''
        num = po.get('whatsapp_phone_number') or ''.join(c for c in phone_ids.get(pid, '') if c.isdigit())
        if num == NUM:
            lines.append('ГРУППА [%s] %s | кампания: %s | %s' % (s['effective_status'], s['name'][:50], (s.get('campaign') or {}).get('name', '')[:50], s['created_time'][:10]))
    try:
        ads = pages(a + '/ads', 'name,effective_status,created_time,adset{name},creative{object_story_spec,asset_feed_spec,effective_object_story_id,call_to_action_type}')
    except Exception as e:
        notes.append(a + ' ads: ' + str(e)[:100]); continue
    for ad in ads:
        if NUM in json.dumps(ad.get('creative') or {}, ensure_ascii=False):
            lines.append('ОБЪЯВЛЕНИЕ [%s] %s | %s' % (ad['effective_status'], ad['name'][:50], ad['created_time'][:10]))
    notes.append('%s: групп %d, объявлений %d' % (a, len(adsets), len(ads)))

msg = 'Поиск номера +7 706 600 0735 в рекламе Meta (весь год)\n' + ('\n'.join(lines[:40]) if lines else 'Не найден ни в группах объявлений, ни в креативах') + '\n\n' + '\n'.join(notes) + '\nНомеров в группах: ' + ', '.join(sorted(set(phone_ids.values()))) 
chunks = [msg[i:i+3500] for i in range(0, len(msg), 3500)] or ['пусто']
for c in chunks:
    try:
        urllib.request.urlopen(urllib.request.Request('https://api.telegram.org/bot%s/sendMessage' % TG, data=urllib.parse.urlencode({'chat_id': CHAT, 'text': c}).encode()), timeout=30)
    except urllib.error.HTTPError as e:
        print('telegram error:', e.code, e.read().decode()[:200])
print('готово, совпадений:', len(lines), '| ошибок:', len(notes))
