// Заявки «Перезвоните мне» с сайта ecomaps.kz → Telegram.
// Маршрут: ecomaps.kz/api/* (см. worker/wrangler.toml). Секреты TG_TOKEN и TG_CHAT_ID
// задаются при деплое из секретов GitHub (workflow deploy-worker.yml), в коде их нет.
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').slice(0, 500);
const json = (o, st = 200) => new Response(JSON.stringify(o), { status: st, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname !== '/api/lead') return json({ ok: false, error: 'not_found' }, 404);
    if (req.method !== 'POST') return json({ ok: false, error: 'method' }, 405);
    const origin = req.headers.get('origin') || '';
    if (origin && !/^https:\/\/(www\.)?ecomaps\.kz$/.test(origin)) return json({ ok: false, error: 'origin' }, 403);
    let d;
    try { d = await req.json(); } catch { return json({ ok: false, error: 'bad_json' }, 400); }
    if (d.website) return json({ ok: true }); // ловушка для ботов: скрытое поле заполнено
    let digits = String(d.phone || '').replace(/\D/g, '');
    if (digits.length === 10) digits = '7' + digits;
    if (digits.length === 11 && digits[0] === '8') digits = '7' + digits.slice(1);
    if (digits.length < 11 || digits.length > 13) return json({ ok: false, error: 'phone' }, 400);
    const phone = '+' + digits;
    const city = req.cf && req.cf.city ? `${req.cf.city}${req.cf.country ? ', ' + req.cf.country : ''}` : '';
    const lines = [
      '📞 <b>Заявка с сайта: перезвонить</b>',
      `Телефон: <a href="tel:${phone}">${phone}</a>`,
      d.name ? `Имя: ${esc(d.name)}` : '',
      d.note ? `Интерес: ${esc(d.note)}` : '',
      `Страница: ${esc(d.page)}${d.place ? ' · кнопка ' + esc(d.place) : ''}`,
      d.utm ? `Источник: ${esc(d.utm)}` : '',
      city ? `Город по IP: ${esc(city)}` : '',
      `WhatsApp: https://wa.me/${digits}`,
    ].filter(Boolean);
    let sent = 0;
    for (const chat of String(env.TG_CHAT_ID).split(',').map(s => s.trim()).filter(Boolean)) {
      const r = await fetch(`https://api.telegram.org/bot${env.TG_TOKEN}/sendMessage`, {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ chat_id: chat, text: lines.join('\n'), parse_mode: 'HTML', disable_web_page_preview: true }),
      });
      if (r.ok) sent++;
    }
    if (!sent) return json({ ok: false, error: 'telegram' }, 502);
    return json({ ok: true });
  },
};
