# ecomaps

Static site for **ecomaps.kz**, hosted on GitHub Pages (see `CNAME`).

Its only page is `whatsapp/index.html`: a redirect that distributes incoming leads from
`ecomaps.kz/whatsapp` across the company's WhatsApp numbers.

## How routing works

Two numbers are in rotation, defined in `whatsapp/index.html`:

| Index | Number         |
|-------|----------------|
| 0     | `77064299895`  |
| 1     | `77068385000`  |

**First visit** — the page atomically increments a shared `counter` in Firebase Realtime
Database and assigns `numbers[counter % 2]`, so consecutive new visitors alternate evenly
between the two managers. The assignment is then saved to the visitor's browser.

**Return visit** — the saved assignment is read back and the visitor is sent to the *same*
number as last time. Firebase is not contacted at all, and the Firebase SDK is not even
downloaded, which makes repeat redirects noticeably faster on mobile.

This stickiness is the point: without it, a returning customer would land on whichever
manager was next in the rotation, and would have to re-explain themselves to someone new.

### Stored value

Saved under the key `ecomaps_wa_route`, to **both** `localStorage` and a cookie:

```json
{ "v": 1, "i": 1, "t": 1784199391566 }
```

- `v` — schema version. Bump it to invalidate every existing assignment at once.
- `i` — index into the numbers array (not the URL — see *Changing a number* below).
- `t` — timestamp of the last visit.

Both stores are written on every visit. Writing both is deliberate: browsers evict cookies
and `localStorage` on different schedules, so if one is lost the other restores it. The
refresh on every visit also slides the expiry — an assignment is forgotten after 400 days
**without a visit**, rather than 400 days after it was first made, so an active customer
keeps their manager indefinitely.

## Limitations (important)

**Stickiness is per-browser, not per-person.** The same customer on a phone and a laptop
gets two independent assignments. Private/incognito windows never stick.

**Safari/iOS forgets after 7 days.** Safari's Intelligent Tracking Prevention deletes all
script-writable storage — `localStorage` and JavaScript-set cookies alike — after 7 days
of Safari use without a visit to the site. Other browsers cap cookie lifetime too: the page
requests 400 days, but Chrome allows at most 400, Brave truncates to ~180, and Safari to 7.

None of this is fixable from a static page. Only a **server-set `HttpOnly` cookie** is exempt
from these caps, and GitHub Pages cannot set one. Expect a meaningful share of returning
iPhone visitors to be reassigned.

Unrecognised visitors are treated as brand new and re-enter the normal rotation.

If per-person, cross-device, genuinely permanent routing is ever needed, the only real answer
is the **WhatsApp Business API** (Wazzup24, Green API, 360dialog, Twilio): one public number,
with the provider routing each *phone number* to the same manager forever. A phone number is
the only permanent identifier in this system — and it is only knowable *after* the customer
sends a message, which is why the web page cannot do this alone.

## Maintenance

### Changing a number

Edit the `numbers` array in `whatsapp/index.html`.

> **Never reorder the array.** Visitors store an *index*, not a URL. Replacing a number in
> place is safe and intended — that manager's existing customers follow the new number.
> Reordering silently reassigns every existing customer to the wrong manager.

To add a third number, append it. New visitors will rotate across all three; existing ones
keep whoever they have.

### Failure behaviour

If Firebase fails to load or does not answer within 3 seconds, the visitor is still
redirected — to a **random** number, which is then remembered. Random rather than a fixed
fallback keeps the two managers balanced during an outage instead of skewing every error
toward the first number. Exact alternation is impossible here, since the counter is precisely
what is unreachable.

## Analytics

Both Yandex.Metrika (`103848088`) and Google Analytics (`G-HMMT7JD949`) receive a `redirect`
goal carrying the destination and a `returning: true | false` flag. That flag is how you
measure how well stickiness actually holds up in real traffic — in particular how often
Safari's 7-day eviction is costing you a returning customer.

## Local testing

```bash
python3 -m http.server 8000
# open http://localhost:8000/whatsapp/
```

Note that this hits the **live** Firebase counter and will increment it. To avoid touching
production, temporarily point the transaction at a throwaway path
(`.ref('counter_test')`) — and revert before deploying.

Useful checks in DevTools (Application → Storage, and the Network tab):

1. First visit — Firebase loads, both `localStorage` and cookie are written.
2. Reload — no `gstatic.com` requests at all, same number, faster.
3. Delete either store — the other restores it, same number.
4. Clear both — treated as new, fresh assignment.
5. Block `*gstatic.com*` — still redirects within ~3s, to a random remembered number.

## Deployment

Pushing to the default branch publishes to GitHub Pages. There is no build step — the page
is plain HTML with no dependencies beyond the Firebase compat SDK (pinned at 8.10.1), which
is loaded from `gstatic.com` at runtime and only when needed.

## Note

Firebase security rules are not part of this repo. The `apiKey` in the page is public by
design and is not what protects the database — if `counter` is publicly writable, anyone can
reset or skew the rotation. Worth auditing in the Firebase console.
