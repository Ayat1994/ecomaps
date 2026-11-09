#!/usr/bin/env python3
"""Собирает три языковые версии сайта из src/template.html:
   /index.html (ru), /kz/index.html (kk), /en/index.html (en)."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, 'src', 'template.html'), encoding='utf-8').read()

T = {
 'title': ['Деревянная карта мира с подсветкой — купить в РК | ECOMAPS', 'Подсветкасы бар ағаш әлем картасы — Қазақстан | ECOMAPS', 'Wooden backlit world map for your wall | ECOMAPS'],
 'desc': ['Многоуровневые карты мира из дерева с подсветкой: 13 расцветок, надписи на 3 языках, 8 рабочих дней. Доставка и монтаж по Казахстану, рассрочка Kaspi.', 'Подсветкасы бар көп деңгейлі ағаш әлем карталары: 13 түс, 3 тілде жазу, 8 жұмыс күні. Бүкіл Қазақстан бойынша жеткізу, орнату, Kaspi бөліп төлеу.', 'Multi-layer wooden world maps with backlight: 13 colour schemes, labels in 3 languages, made in 8 working days.'],
 'og_title': ['ECOMAPS — весь мир перед тобой', 'ECOMAPS — бүкіл әлем алдыңда', 'ECOMAPS — the whole world before you'],
 'descriptor': ['интерьерные карты мира', 'интерьерлік әлем карталары', 'interior world maps'],
 'nav_catalog': ['Каталог', 'Каталог', 'Catalog'],
 'nav_services': ['Услуги', 'Қызметтер', 'Services'],
 'nav_calc': ['Расчёт цены', 'Баға есебі', 'Get a price'],
 'nav_geo': ['Города', 'Қалалар', 'Cities'],
 'nav_works': ['Работы', 'Жұмыстар', 'Our work'],
 'nav_faq': ['Вопросы', 'Сұрақтар', 'FAQ'],
 'phone_sub': ['WhatsApp · по всему Казахстану', 'WhatsApp · бүкіл Қазақстан бойынша', 'WhatsApp · all over Kazakhstan'],
 'hero_alt': ['Деревянная карта мира с подсветкой на стене', 'Қабырғадағы подсветкасы бар ағаш әлем картасы', 'Backlit wooden world map on a wall'],
 'badge_tag': ['Акция', 'Акция', 'Offer'],
 # Акция 10–12.11.2026 (реклама Meta «Только 3 дня — скидки до 50%»); полоска сама исчезает после 12.11 23:59 по Астане.
 'sale_tag': ['Только 3 дня', 'Тек 3 күн', ''], 'sale_txt': ['Скидки до 50% на карты из дерева', 'Ағаш карталарға 50%-ға дейін жеңілдік', ''], 'sale_btn': ['Узнать цену со скидкой', 'Жеңілдікпен бағасын білу', ''],
 'badge': ['Логотип компании на карте в подарок', 'Компания логотипі картаға сыйлыққа', 'Your company logo on the map for free'],
 'h1k': ['Деревянная карта мира с подсветкой', 'Подсветкасы бар ағаш әлем картасы', 'Wooden backlit world map'],
 'h1a': ['Весь мир', 'Бүкіл әлем', 'The whole world'],
 'h1b': ['перед тобой', 'алдыңда', 'before you'],
 'hero_lead': ['Многоуровневая деревянная карта мира с подсветкой: главный акцент гостиной, кабинета или детской. Лидер продаж интерьерных карт в Казахстане.', 'Подсветкасы бар көп деңгейлі ағаш әлем картасы: қонақ бөлменің, кабинеттің немесе балалар бөлмесінің басты әшекейі. Қазақстандағы интерьер карталары сатылымының көшбасшысы.', 'A multi-layer wooden world map with backlight, the centrepiece of a living room, study or kids’ room. Kazakhstan’s best-selling interior maps.'],
 'check1': ['Доставка и установка в любом городе Казахстана', 'Қазақстанның кез келген қаласына жеткізу және орнату', 'Delivery and installation in any city of Kazakhstan'],
 'check2': ['Изготовление за 8 рабочих дней', '8 жұмыс күнінде дайындаймыз', 'Made in 8 working days'],
 'check3': ['Рассрочка Kaspi Red, 0-0-12 и 0-0-24', 'Kaspi Red, 0-0-12 және 0-0-24 бөліп төлеу', 'Kaspi Red installments 0-0-12 and 0-0-24'],
 'btn_calc': ['Рассчитать стоимость', 'Бағасын есептеу', 'Get a price'],
 'btn_wa': ['Написать в WhatsApp', 'WhatsApp-қа жазу', 'Message on WhatsApp'],
 'stat1': ['лет на рынке', 'жыл нарықта', 'years on the market'],
 'stat2': ['довольных клиентов', 'риза клиент', 'happy clients'],
 'stat3b': ['Весь РК', 'Бүкіл ҚР', 'All KZ'],
 'stat3': ['доставка и установка', 'жеткізу және орнату', 'delivery & installation'],
 'stat4': ['подписчиков в Instagram', 'Instagram жазылушысы', 'Instagram followers'],
 'trust': ['Нам доверяют', 'Бізге сенім артады', 'Trusted by'],
 'cat_h_a': ['Выберите', 'Өз картаңызды', 'Choose'],
 'cat_h_b': ['свою карту', 'таңдаңыз', 'your map'],
 'tab_world': ['Карта мира', 'Әлем картасы', 'World map'],
 'tab_kz': ['Карта Казахстана', 'Қазақстан картасы', 'Kazakhstan map'],
 'tab_biz': ['Для бизнеса', 'Бизнес үшін', 'For business'],
 'tab_kids': ['Для школ и садов', 'Мектеп пен балабақшаға', 'Schools & kindergartens'],
 'world_h': ['Карта мира из дерева', 'Ағаштан жасалған әлем картасы', 'Wooden world map'],
 'world_p': ['Многоуровневая рельефная карта: главный акцент гостиной, спальни, кабинета или детской. Каждая страна — отдельная деталь.',
             'Көп деңгейлі рельефті карта: қонақ бөлмесінің, жатын бөлменің, кабинеттің немесе балалар бөлмесінің басты әшекейі. Әр ел — жеке бөлшек.',
             'A multi-layer relief map that becomes the centrepiece of a living room, bedroom, study or kids’ room. Every country is a separate piece.'],
 'world_l1': ['13 готовых расцветок или ваша', '13 дайын түс нұсқасы немесе өзіңіздікі', '13 ready colour schemes or your own'],
 'world_l2': ['Тёплая или холодная подсветка', 'Жылы немесе суық подсветка', 'Warm or cool backlight'],
 'world_l3': ['Надписи на русском, казахском или английском', 'Жазулар орыс, қазақ немесе ағылшын тілінде', 'Labels in Russian, Kazakh or English'],
 'own_size': ['Свой размер', 'Өз өлшеміңіз', 'Custom size'],
 'kz_pane_alt': ['Ночная карта Казахстана с подсветкой', 'Подсветкасы бар түнгі Қазақстан картасы', 'Night-style backlit map of Kazakhstan'],
 'kz_h': ['Карта Казахстана', 'Қазақстан картасы', 'Map of Kazakhstan'],
 'kz_p': ['Обновлённая карта РК с новыми границами областей. От минимальной детализации до карты с железными дорогами, Каспийским морем и населёнными пунктами.',
          'Облыстардың жаңа шекаралары бар жаңартылған ҚР картасы. Қарапайым нұсқадан бастап темір жолдар, Каспий теңізі және елді мекендер бар картаға дейін.',
          'An up-to-date map of Kazakhstan with the new regional borders, from a minimal version to a detailed one with railways, the Caspian Sea and settlements.'],
 'kz_l1': ['Области разными оттенками или в фирменных цветах', 'Облыстар әртүрлі реңкте немесе фирмалық түстерде', 'Regions in different shades or in your brand colours'],
 'kz_l2': ['Логотип компании на карте', 'Картада компания логотипі', 'Your company logo on the map'],
 'kz_l3': ['Рельефная 3D-версия — наша разработка', 'Рельефті 3D нұсқасы — біздің әзірлеме', 'A 3D relief version, developed by us'],
 'biz_h': ['Декор для бизнеса', 'Бизнеске арналған декор', 'Décor for business'],
 'biz_p': ['Декор-панели, Instagram-зеркала и картины в фирменном стиле: то, что клиенты фотографируют и запоминают. Плюс карты мира и Казахстана с вашим логотипом. Работаем с юрлицами и по госзакупкам.', 'Фирмалық стильдегі декор-панельдер, Instagram-айналар және суреттер: клиенттер суретке түсіріп, есте сақтайтын дүниелер. Сондай-ақ логотипіңіз бар әлем және Қазақстан карталары. Заңды тұлғалармен және мемлекеттік сатып алу арқылы жұмыс істейміз.', 'Wall panels, Instagram mirrors and artwork in your brand style that clients photograph and remember, plus world and Kazakhstan maps with your logo. We work with companies and through public procurement.'],
 'biz_l1': ['Бесплатная визуализация по фото помещения', 'Бөлме фотосы бойынша тегін визуализация', 'Free mock-up based on a photo of your space'],
 'biz_l2': ['Логотип компании в подарок', 'Компания логотипі сыйлыққа', 'Your company logo for free'],
 'biz_l3': ['Монтаж в вашем городе, безнал и госзакупки', 'Сіздің қалаңызда орнату, қолма-қолсыз төлем және мемлекеттік сатып алу', 'Installation in your city, bank transfer and public procurement'],
 'svc_kicker': ['Не только карты', 'Тек карта емес', 'Not just maps'],
 'svc_h_a': ['Оформим', 'Интерьерді', 'We design'],
 'svc_h_b': ['весь интерьер', 'толық безендіреміз', 'the whole interior'],
 'svc_sub': ['Собственное производство в Казахстане: режем, гравируем, печатаем и собираем. Поэтому кроме карт делаем панели, картины, зеркала и полностью оформляем помещения.',
             'Қазақстандағы өз өндірісіміз: кесеміз, гравировка жасаймыз, басып шығарамыз және құрастырамыз. Сондықтан картадан бөлек панельдер, суреттер, айналар жасаймыз және бөлмелерді толық безендіреміз.',
             'Our own production in Kazakhstan: cutting, engraving, printing and assembly. That is why besides maps we make panels, paintings, mirrors and design complete interiors.'],
 'sv1_h': ['Внутреннее оформление', 'Ішкі безендіру', 'Interior design'],
 'sv1_p': ['Оформление детских садов, школ, офисов и коворкингов под ключ: декор стен, подсветка, тематические зоны.',
           'Балабақша, мектеп, кеңсе және коворкингтерді толық безендіру: қабырға декоры, подсветка, тақырыптық аймақтар.',
           'Turnkey design of kindergartens, schools, offices and co-working spaces: wall décor, lighting, themed zones.'],
 'sv2_h': ['Декор-панели', 'Декор-панельдер', 'Wall panels'],
 'sv2_p': ['Многоуровневые настенные панели из дерева, ХДФ и МДФ. Больше 20 шаблонов или ваш дизайн.',
           'Ағаш, ХДФ және МДФ-тен жасалған көп деңгейлі қабырға панельдері. 20-дан астам үлгі немесе сіздің дизайныңыз.',
           'Multi-layer wall panels in wood, HDF and MDF. 20+ templates or your own design.'],
 'sv3_h': ['Картины', 'Суреттер', 'Paintings'],
 'sv3_p': ['Картины, постеры и мотивационные панно в рамах для дома и офиса, в том числе в фирменном стиле компании.',
           'Үй мен кеңсеге арналған жақтаудағы суреттер, постерлер және мотивациялық панно, соның ішінде компанияның фирмалық стилінде.',
           'Framed paintings, posters and motivational artwork for homes and offices, including in your corporate style.'],
 'sv4_h': ['Instagram-зеркала', 'Instagram-айналар', 'Instagram mirrors'],
 'sv4_p': ['Зеркало в виде поста Instagram с вашим аккаунтом, логотипом, QR-кодом и подсветкой. Готовая фотозона для салона, кофейни, магазина или офиса.', 'Instagram жазбасы түріндегі айна: аккаунтыңыз, логотип, QR-код және подсветка. Салон, кофейня, дүкен немесе кеңсеге дайын фотоаймақ.', 'A mirror styled as an Instagram post with your account, logo, QR code and backlight. A ready-made photo zone for a salon, café, shop or office.'],
 'sv5_h': ['Неон и вывески', 'Неон және маңдайшалар', 'Neon & signs'],
 'sv5_p': ['Неоновые надписи и световые вывески для интерьера, фотозон и входных групп.',
           'Интерьерге, фотоаймақтарға және кіреберіске арналған неон жазулар мен жарықты маңдайшалар.',
           'Neon lettering and illuminated signs for interiors, photo zones and entrances.'],
 'sv6_h': ['Часы с логотипом', 'Логотипі бар сағат', 'Clocks with your logo'],
 'sv6_p': ['Настенные часы из дерева с логотипом компании. Хороший корпоративный подарок.',
           'Компания логотипі бар ағаш қабырға сағаты. Тамаша корпоративтік сыйлық.',
           'Wooden wall clocks with your company logo. A great corporate gift.'],
 'sv_more': ['Узнать подробнее', 'Толығырақ', 'Learn more'],
 'calc_kicker': ['Расчёт стоимости', 'Баға есебі', 'Price estimate'],
 'calc_h_a': ['Узнайте цену', 'Бағасын', 'Get a price'],
 'calc_h_b': ['за 1 минуту', '1 минутта біліңіз', 'in 1 minute'],
 'calc_sub': ['Выберите параметры, и менеджер пришлёт точную цену и визуализацию в WhatsApp.', 'Параметрлерді таңдаңыз, менеджер нақты бағаны және визуализацияны WhatsApp-қа жібереді.', 'Choose the options and our manager will send you the exact price and a mock-up on WhatsApp.'],
 'q1': ['Что нужно?', 'Не қажет?', 'What do you need?'],
 'q1_panel': ['Панель', 'Панель', 'Panel'],
 'q1_other': ['Другое', 'Басқа', 'Other'],
 'q2': ['Размер', 'Өлшемі', 'Size'],
 's_small': ['маленькая', 'кіші', 'small'], 's_mid': ['средняя', 'орташа', 'medium'], 's_big': ['большая', 'үлкен', 'large'], 's_own': ['под стену', 'қабырғаға сай', 'to fit your wall'],
 'q3': ['Подсветка', 'Подсветка', 'Backlight'],
 'l_yes': ['С подсветкой', 'Подсветкамен', 'With backlight'], 'l_no': ['Без подсветки', 'Подсветкасыз', 'Without backlight'], 'l_help': ['Подскажите', 'Кеңес беріңіз', 'Advise me'],
 'q4': ['Оплата', 'Төлем', 'Payment'],
 'p_kaspi': ['Kaspi рассрочка', 'Kaspi бөліп төлеу', 'Kaspi installments'], 'p_now': ['Сразу', 'Бірден', 'In full'], 'p_corp': ['Для юрлица', 'Заңды тұлға', 'Company invoice'],
 'res_h': ['Ваш расчёт', 'Сіздің есебіңіз', 'Your request'],
 'res_gift': ['Бесплатно покажем карту на фото вашей стены', 'Картаны қабырғаңыздың фотосында тегін көрсетеміз', 'We will show the map on a photo of your wall for free'],
 'res_btn': ['Узнать цену в WhatsApp', 'WhatsApp-та бағасын білу', 'Get the price on WhatsApp'],
 'res_alt': ['или свяжитесь:', 'немесе хабарласыңыз:', 'or contact us:'],
 'geo_kicker': ['География', 'География', 'Coverage'],
 'geo_h_a': ['Работаем', 'Бүкіл Қазақстан', 'We work'],
 'geo_h_b': ['по всему Казахстану', 'бойынша жұмыс істейміз', 'all over Kazakhstan'],
 'geo_sub': ['Доставляем в любой город, район и село Казахстана и организуем установку на месте: Астана, Алматы, Шымкент, Караганда, Актобе, Атырау и все остальные города.', 'Қазақстанның кез келген қаласына, ауданы мен ауылына жеткіземіз және орнында орнатамыз: Астана, Алматы, Шымкент, Қарағанды, Ақтөбе, Атырау және барлық басқа қалалар.', 'We deliver to any city, town or village in Kazakhstan and arrange installation on site: Astana, Almaty, Shymkent, Karaganda, Aktobe, Atyrau and every other city.'],
 'geo_card_a': ['Доставка и установка', 'Жеткізу және орнату', 'Delivery & installation'],
 'geo_default_city': ['по всему Казахстану', 'бүкіл Қазақстан бойынша', 'across Kazakhstan'],
 'geo_l1': ['Надёжная упаковка и доставка до двери', 'Сенімді орау және есікке дейін жеткізу', 'Safe packaging and door-to-door delivery'],
 'geo_l2': ['Монтажник установит карту на стену', 'Монтажшы картаны қабырғаға орнатады', 'An installer mounts the map on your wall'],
 'geo_l3': ['Или установка самостоятельно: инструкция и помощь по видеозвонку', 'Немесе өзіңіз орнатасыз: нұсқаулық және бейнеқоңырау арқылы көмек', 'Or DIY: instructions and help over a video call'],
 'geo_l4': ['Все крепления в комплекте', 'Барлық бекіткіштер жинақта', 'All fixings included'],
 'geo_btn': ['Уточнить сроки для моего города', 'Қалама жеткізу мерзімін білу', 'Check timing for my city'],
 'works_h_b': ['у клиентов', 'клиенттерде', 'at our clients'],
 'why_kicker': ['Почему ECOMAPS', 'Неге ECOMAPS', 'Why ECOMAPS'],
 'why_h_a': ['Почему', 'Неге', 'Why'],
 'why_h_b': ['выбирают нас', 'бізді таңдайды', 'clients choose us'],
 'why1_h': ['рабочих дней', 'жұмыс күні', 'working days'],
 'why1_p': ['Изготовление после согласования дизайна: резка, гравировка, печать, сборка.', 'Дизайн келісілгеннен кейін дайындау: кесу, гравировка, басып шығару, құрастыру.', 'Production after design approval: cutting, engraving, printing, assembly.'],
 'why2_h': ['Сделано в Казахстане', 'Қазақстанда жасалған', 'Made in Kazakhstan'],
 'why2_p': ['Собственное производство в Астане, индустриальный сертификат НПП «Атамекен».', 'Астанадағы өз өндірісіміз, «Атамекен» ҰКП индустриялық сертификаты.', 'Our own production in Astana, industrial certificate of NCE “Atameken”.'],
 'why3_h': ['Зарегистрированный бренд', 'Тіркелген бренд', 'Registered brand'],
 'why3_p': ['ECOMAPS — товарный знак № 102817. Покупайте оригинал, а не копию.', 'ECOMAPS — № 102817 тауар таңбасы. Көшірмені емес, түпнұсқаны алыңыз.', 'ECOMAPS is trademark No. 102817. Buy the original, not a copy.'],
 'why4_h': ['Достояние отрасли 2023', 'Сала мақтанышы 2023', 'Industry Pride 2023'],
 'why4_p': ['По итогам аналитики Национального информационно-аналитического центра.', 'Ұлттық ақпараттық-талдау орталығының талдауы нәтижесінде.', 'Based on the analysis of the National Information and Analytical Center.'],
 'how_kicker': ['Как заказать', 'Қалай тапсырыс беруге болады', 'How to order'],
 'how_h_a': ['От заявки до стены', 'Өтінімнен қабырғаға дейін', 'From request to wall'],
 'how_h_b': ['за 4 шага', '4 қадамда', 'in 4 steps'],
 'st1_h': ['Заявка', 'Өтінім', 'Request'], 'st1_p': ['Пишете в WhatsApp, присылаете фото и размер стены.', 'WhatsApp-қа жазып, қабырғаның фотосы мен өлшемін жібересіз.', 'Message us on WhatsApp with a photo and the size of your wall.'],
 'st2_h': ['Визуализация', 'Визуализация', 'Mock-up'], 'st2_p': ['Бесплатно показываем карту на вашей стене. Согласуем язык, расцветку и размер.', 'Картаны қабырғаңызда тегін көрсетеміз. Тілін, түсін және өлшемін келісеміз.', 'We show the map on your wall for free and agree on language, colours and size.'],
 'st3_h': ['Производство', 'Өндіріс', 'Production'], 'st3_p': ['Около 8 рабочих дней. Контроль качества каждой детали.', 'Шамамен 8 жұмыс күні. Әр бөлшектің сапасын тексереміз.', 'About 8 working days, with quality control of every piece.'],
 'st4_h': ['Доставка и монтаж', 'Жеткізу және орнату', 'Delivery & installation'], 'st4_p': ['В любой город Казахстана, а также в Россию, ОАЭ и другие страны. Монтажник или установка по инструкции.', 'Қазақстанның кез келген қаласына, сондай-ақ Ресейге, БАӘ-ге және басқа елдерге. Монтажшы немесе нұсқаулық бойынша орнату.', 'To any city in Kazakhstan, as well as Russia, the UAE and other countries. Professional or DIY installation.'],
 'pay2': ['Kaspi Магазин', 'Kaspi Дүкен', 'Kaspi Shop'], 'pay3': ['Безнал для юрлиц', 'Заңды тұлғаларға қолма-қолсыз', 'Bank transfer for companies'],
 'faq_kicker': ['Вопрос — ответ', 'Сұрақ — жауап', 'Q & A'],
 'faq_h_a': ['Частые', 'Жиі қойылатын', 'Frequently asked'],
 'faq_h_b': ['вопросы', 'сұрақтар', 'questions'],
 'f1q': ['Сколько стоит карта?', 'Карта қанша тұрады?', 'How much does a map cost?'],
 'f1a': ['Цена зависит от модели, размера, расцветки и подсветки. Заполните расчёт выше или напишите в WhatsApp, и менеджер посчитает стоимость.', 'Баға модельге, өлшемге, түске және подсветкаға байланысты. Жоғарыдағы есепті толтырыңыз немесе WhatsApp-қа жазыңыз, менеджер бағасын есептейді.', 'It depends on the model, size, colours and backlight. Fill in the form above or message us on WhatsApp and we will calculate it.'],
 'f2q': ['Сколько времени занимает изготовление?', 'Дайындау қанша уақыт алады?', 'How long does production take?'],
 'f2a': ['Около 8 рабочих дней после согласования дизайна. Сроки индивидуальных заказов обговариваем отдельно.', 'Дизайн келісілгеннен кейін шамамен 8 жұмыс күні. Жеке тапсырыстардың мерзімі бөлек келісіледі.', 'About 8 working days after design approval. Custom orders are scheduled individually.'],
 'f3q': ['Есть ли доставка и установка в моём городе?', 'Менің қалама жеткізу және орнату бар ма?', 'Do you deliver and install in my city?'],
 'f3a': ['Да. Доставляем по всему Казахстану в города, районы и сёла, а также в Россию, ОАЭ и другие страны. Установку организуем на месте или поможем установить самостоятельно по видеозвонку.', 'Иә. Бүкіл Қазақстан бойынша қалаларға, аудандар мен ауылдарға, сондай-ақ Ресейге, БАӘ-ге және басқа елдерге жеткіземіз. Орнатуды орнында ұйымдастырамыз немесе бейнеқоңырау арқылы өзіңіз орнатуға көмектесеміз.', 'Yes. We deliver across Kazakhstan, to cities, towns and villages, as well as to Russia, the UAE and other countries. We arrange installation on site or guide you through DIY installation by video call.'],
 'f4q': ['Делаете ли вы что-то кроме карт?', 'Картадан басқа не жасайсыздар?', 'Do you make anything besides maps?'],
 'f4a': ['Да: панели, картины, зеркала, неоновые вывески, часы с логотипом и оформление интерьеров детских садов, школ и офисов под ключ.', 'Иә: панельдер, суреттер, айналар, неон маңдайшалар, логотипі бар сағаттар және балабақша, мектеп пен кеңселерді толық безендіру.', 'Yes: wall panels, paintings, mirrors, neon signs, branded clocks and turnkey interior design for kindergartens, schools and offices.'],
 'f5q': ['Можно в рассрочку?', 'Бөліп төлеуге бола ма?', 'Can I pay in installments?'],
 'f5a': ['Да: Kaspi Red, рассрочка 0-0-12 и 0-0-24. Для компаний работаем по безналу и через госзакупки.', 'Иә: Kaspi Red, 0-0-12 және 0-0-24 бөліп төлеу. Компаниялармен қолма-қолсыз және мемлекеттік сатып алу арқылы жұмыс істейміз.', 'Yes: Kaspi Red, 0-0-12 and 0-0-24 installments. Companies can pay by bank transfer or via public procurement.'],
 'f6q': ['Где посмотреть карты вживую?', 'Карталарды қайдан көруге болады?', 'Where can I see the maps in person?'],
 'f6a': ['В шоуруме в Астане: ул. Сарайшык, 7/1, Есильский район. Перед визитом напишите нам в WhatsApp', 'Астанадағы шоурумда: Сарайшық көшесі, 7/1, Есіл ауданы. Келер алдында WhatsApp-қа жазыңыз', 'At our showroom in Astana: 7/1 Saraishyk St, Yesil district. Please message us on WhatsApp before visiting'],
 'slogan': ['Весь мир перед тобой', 'Бүкіл әлем алдыңда', 'The whole world before you'],
 'final_h': ['Покажем вашу карту на вашей стене. Бесплатно.', 'Картаңызды өз қабырғаңызда тегін көрсетеміз.', 'We will show your map on your wall. For free.'],
 'final_p': ['Пришлите фото стены в WhatsApp, и мы сделаем визуализацию с ценой. Доставка и установка в любом городе Казахстана.', 'Қабырғаның фотосын WhatsApp-қа жіберіңіз, біз бағасымен бірге визуализация жасаймыз. Қазақстанның кез келген қаласына жеткізу және орнату.', 'Send a photo of your wall on WhatsApp and we will make a mock-up with the price. Delivery and installation anywhere in Kazakhstan.'],
 'final_btn': ['Получить визуализацию', 'Визуализация алу', 'Get a mock-up'],
 'foot_tag': ['Лидер продаж интерьерных карт в Казахстане', 'Қазақстандағы интерьер карталары сатылымының көшбасшысы', 'Kazakhstan’s best-selling interior maps'],
 'foot_addr': ['Шоурум: Астана, ул. Сарайшык, 7/1', 'Шоурум: Астана, Сарайшық к-сі, 7/1', 'Showroom: 7/1 Saraishyk St, Astana'],
 'sheet_h': ['Как вам удобнее?', 'Сізге қалай ыңғайлы?', 'How would you like to contact us?'],
 'sheet_wa': ['WhatsApp: чат или звонок', 'WhatsApp: чат немесе қоңырау', 'WhatsApp: chat or call'],
 'sheet_hint': ['Откроется чат с менеджером. Чтобы позвонить, нажмите 📞 вверху чата.', 'Менеджермен чат ашылады. Қоңырау шалу үшін чаттың жоғарғы жағындағы 📞 басыңыз.', 'A chat with our manager will open. To call, tap 📞 at the top of the chat.'],
 'sheet_call': ['Обычный звонок', 'Қарапайым қоңырау', 'Regular phone call'],
 'tab_world_s': ['Карты мира', 'Әлем карталары', 'World maps'],
 'tab_kz_s': ['Карты РК', 'ҚР карталары', 'KZ maps'],
 'tab_biz_s': ['Для бизнеса', 'Бизнеске', 'Business'],
 'chip_maps': ['Карты с логотипом', 'Логотипі бар карталар', 'Maps with your logo'],
 'svcb_h_a': ['Панели, зеркала', 'Панельдер, айналар', 'Panels, mirrors'],
 'svcb_h_b': ['и картины', 'және суреттер', 'and artwork'],
 'mb_label': ['Разделы сайта', 'Сайт бөлімдері', 'Site sections'],
 'lb_want': ['Хочу такую', 'Осындай қалаймын', 'I want this'],
 'nav_trust': ['О нас', 'Біз туралы', 'About us'],
 'cat_sub': ['Три направления, у каждого своя страница с моделями, работами и расчётом цены.', 'Үш бағыт, әрқайсысының модельдері, жұмыстары және баға есебі бар өз беті бар.', 'Three lines, each with its own page of models, projects and pricing.'],
 'models_h': ['Популярные модели', 'Танымал модельдер', 'Popular models'],
 'rel_kicker': ['Наша разработка', 'Біздің әзірлеме', 'Our own development'],
 'rel_h_a': ['Рельефная карта', 'Қазақстанның', 'Relief map'],
 'rel_h_b': ['Казахстана', 'рельефті картасы', 'of Kazakhstan'],
 'rel_p': ['Объёмная карта, где горы, степи и впадины переданы в дереве и цвете: от низменностей Прикаспия до хребтов Алтая и Тянь-Шаня. Мы разработали её сами, и в Казахстане такую карту больше никто не делает.',
           'Таулар, далалар мен ойпаттар ағаш пен түс арқылы берілген көлемді карта: Каспий маңы ойпатынан Алтай мен Тянь-Шань жоталарына дейін. Біз оны өзіміз әзірледік, Қазақстанда мұндай картаны басқа ешкім жасамайды.',
           'A three-dimensional map where mountains, steppes and depressions are shaped in wood and colour, from the Caspian lowlands to the Altai and Tian Shan ranges. We developed it ourselves, and no one else in Kazakhstan makes a map like this.'],
 'rel_l1': ['Собственная разработка ECOMAPS, аналогов в Казахстане нет', 'ECOMAPS-тің өз әзірлемесі, Қазақстанда баламасы жоқ', 'Developed by ECOMAPS, no equivalent in Kazakhstan'],
 'rel_l2': ['Новые границы областей и подписи городов', 'Облыстардың жаңа шекаралары және қала атаулары', 'New regional borders and city names'],
 'rel_l3': ['Контурная подсветка', 'Контурлы подсветка', 'Edge backlight'],
 'rel_l4': ['Для кабинета руководителя, госучреждения или в подарок', 'Басшы кабинетіне, мемлекеттік мекемеге немесе сыйлыққа', 'For an executive office, a public institution or as a gift'],
 'rel_btn': ['Узнать цену рельефной карты', 'Рельефті картаның бағасын білу', 'Get a price for the relief map'],
 'rel_alt1': ['Рельефная карта РК сбоку: объём гор и контурная подсветка', 'ҚР рельефті картасы бүйірінен: таулардың көлемі және контурлы подсветка', 'Side view of the Kazakhstan relief map: carved mountains and edge backlight'],
 'rel_alt2': ['Рельеф Абайской области и Восточного Казахстана с подсветкой', 'Абай облысы мен Шығыс Қазақстанның подсветкасы бар рельефі', 'Backlit relief of the Abai and East Kazakhstan regions'],
 'rel_alt3': ['Восточный Казахстан на рельефной карте: Алтай, Өскемен, Зайсан', 'Рельефті картадағы Шығыс Қазақстан: Алтай, Өскемен, Зайсан', 'East Kazakhstan on the relief map: Altai, Oskemen, Zaisan'],
 'rel_alt': ['Рельеф карты Казахстана крупным планом', 'Қазақстан картасының рельефі жақыннан', 'Close-up of the Kazakhstan relief map'],
 'gift_kicker': ['Для бизнеса', 'Бизнес үшін', 'For business'],
 'gift_h_a': ['Логотип компании', 'Компания логотипі', 'Your company logo'],
 'gift_h_b': ['в подарок', 'сыйлыққа', 'for free'],
 'gift_p': ['Заказываете карту для офиса, и мы бесплатно делаем ваш логотип из того же материала и устанавливаем рядом. Так это выглядит у наших клиентов:', 'Кеңсеге карта тапсырыс бересіз, ал біз логотипіңізді сол материалдан тегін жасап, қасына орнатамыз. Клиенттерімізде бұл былай көрінеді:', 'Order a map for your office and we make your logo in the same material for free and mount it next to the map. Here is how it looks at our clients:'],
 'indiv_h': ['Индивидуальные работы', 'Жеке жұмыстар', 'Custom projects'],
 'new_lbl': ['Новинка', 'Жаңа', 'New'],
 'q1_relief': ['Рельефная карта РК', 'ҚР рельефті картасы', 'Relief KZ map'],
 'calc_note': ['Оплата: рассрочка Kaspi 0-0-12 и 0-0-24, Kaspi Red, безнал для юрлиц и госзакупки через omarket.kz.', 'Төлем: Kaspi 0-0-12 және 0-0-24 бөліп төлеу, Kaspi Red, заңды тұлғаларға қолма-қолсыз және omarket.kz арқылы мемлекеттік сатып алу.', 'Payment: Kaspi 0-0-12 and 0-0-24 installments, Kaspi Red, bank transfer for companies and public procurement via omarket.kz.'],
 'works_h_world': ['Карты мира', 'Әлем карталары', 'World maps'],
 'works_h_kz': ['Карты Казахстана', 'Қазақстан карталары', 'Kazakhstan maps'],
 'works_h_biz': ['Проекты для бизнеса', 'Бизнеске арналған жобалар', 'Business projects'],
 'cert_h': ['Зарегистрированный товарный знак № 102817', '№ 102817 тіркелген тауар таңбасы', 'Registered trademark No. 102817'],
 'cert_p': ['Свидетельство Национального института интеллектуальной собственности РК, действует до 18.10.2034. Покупайте оригинал, а не копию.', 'ҚР Ұлттық зияткерлік меншік институтының куәлігі, 18.10.2034 дейін жарамды. Көшірмені емес, түпнұсқаны алыңыз.', 'Certificate of the National Institute of Intellectual Property of Kazakhstan, valid until 18.10.2034. Buy the original, not a copy.'],
 'cert_open': ['Открыть документ', 'Құжатты ашу', 'Open the document'],
 'buy_h': ['Купить онлайн', 'Онлайн сатып алу', 'Buy online'],
 'buy_p': ['Наши карты есть в Kaspi Магазине (с рассрочкой) и на omarket.kz для госзакупок.', 'Карталарымыз Kaspi Дүкенде (бөліп төлеумен) және мемлекеттік сатып алу үшін omarket.kz-те бар.', 'Our maps are available in the Kaspi Shop (with installments) and on omarket.kz for public procurement.'],
 'shop': ['Магазин', 'Дүкен', 'Shop'],
 'gz': ['госзакупки', 'мемлекеттік сатып алу', 'public procurement'],
 'company': ['ТОО «ECOMAPS», БИН 231240016904', '«ECOMAPS» ЖШС, БСН 231240016904', 'ECOMAPS LLP, BIN 231240016904'],
 'tm_line': ['ECOMAPS® — товарный знак № 102817', 'ECOMAPS® — № 102817 тауар таңбасы', 'ECOMAPS® — trademark No. 102817'],
}

# ---------- Английская версия — для покупателей из ОАЭ, Катара и других стран ----------
# (без Kaspi, госзакупок и доставки «по городам Казахстана»)
EN = {
 'title': 'Wooden backlit world map — UAE & Qatar delivery | ECOMAPS',
 'desc': 'Handmade multi-layer wooden world maps with backlight: 13 colours, labels in 3 languages, made in 8 working days. Shipped to the UAE, Qatar and worldwide.',
 'phone_sub': 'WhatsApp · worldwide',
 'hero_lead': 'A multi-layer wooden world map with backlight, the centrepiece of a living room, study, office or majlis. Handmade in Kazakhstan and shipped to the UAE, Qatar and worldwide.',
 'check1': 'Delivery to the UAE, Qatar and worldwide',
 'check3': 'Free mock-up on a photo of your wall',
 'stat3b': 'UAE · Qatar', 'stat3': 'and worldwide delivery',
 'biz_p': 'Wall panels, Instagram mirrors and artwork in your brand style that clients photograph and remember, plus world maps with your logo. We work with companies and issue invoices.',
 'biz_l3': 'Delivery abroad and bank transfer for companies',
 'calc_note': 'Your manager will send the price together with the delivery cost to your country.',
 'geo_kicker': 'Delivery', 'geo_h_a': 'We ship', 'geo_h_b': 'worldwide',
 'geo_sub': 'We deliver to the UAE (Dubai, Abu Dhabi, Sharjah and all the Emirates), Qatar and other countries. Your manager will confirm the delivery cost and timing for your address before you pay.',
 'geo_card_a': 'Delivery', 'geo_default_city': 'to the UAE and Qatar',
 'geo_l2': 'Step-by-step installation instructions',
 'geo_l3': 'Help over a video call if you need it',
 'geo_btn': 'Check delivery to my city',
 'st4_h': 'Delivery', 'st4_p': 'We ship to the UAE, Qatar and other countries. You install the map with our instructions and video-call support.',
 'f3q': 'Do you deliver to the UAE and Qatar?',
 'f3a': 'Yes. We ship from our workshop in Kazakhstan to the UAE, Qatar and other countries. Your manager confirms the delivery cost and timing for your address before you pay. Installation is simple: instructions and all fixings are included, and we can help over a video call.',
 'f5q': 'How can I pay?',
 'f5a': 'By international bank transfer against an invoice, for both companies and private buyers. Your manager will send you the invoice.',
 'final_p': 'Send a photo of your wall on WhatsApp and we will make a mock-up with the price, including delivery to your city.',
 'foot_tag': 'Handmade wooden maps from Kazakhstan, shipped worldwide',
 'pay3': 'International bank transfer (invoice)',
}
for _k, _v in EN.items(): T[_k][2] = _v
import urllib.parse as _up
EN_WA = 'https://wa.me/77064299895?text=' + _up.quote("Hello! I'm interested in a wooden world map (from ecomaps.kz/en).")

JS = {
 'cap': {
  'g1': ['Карта мира с подсветкой', 'Подсветкасы бар әлем картасы', 'Backlit world map'],
  'physical': ['Физическая карта мира', 'Әлемнің физикалық картасы', 'Physical world map'],
  'kids': ['Светлая карта для детской', 'Балалар бөлмесіне ашық түсті карта', 'Light map for a kids’ room'],
  'g7': ['Карта мира с флагами', 'Жалаулары бар әлем картасы', 'World map with flags'],
  'hero': ['Карта мира в гостиной', 'Қонақ бөлмедегі әлем картасы', 'World map in a living room'],
  'g2': ['Карта мира в офисе', 'Кеңседегі әлем картасы', 'World map in an office'],
  'g3': ['Подсветка крупным планом', 'Подсветка жақыннан', 'Backlight close-up'],
  'g4': ['Кабинет руководителя', 'Басшы кабинеті', 'Director’s office'],
  'g5': ['Холодная подсветка', 'Суық подсветка', 'Cool backlight'],
  'g6': ['Рабочий кабинет', 'Жұмыс кабинеті', 'Study'],
  'g8': ['Светлая карта с подсветкой', 'Подсветкасы бар ашық карта', 'Light backlit map'],
  'light': ['Тёплая подсветка', 'Жылы подсветка', 'Warm backlight'],
  'world': ['Карта мира в квартире', 'Пәтердегі әлем картасы', 'World map in an apartment'],
  'detail': ['Каждая страна — отдельная деталь', 'Әр ел — жеке бөлшек', 'Every country is a separate piece'],
  'install': ['Монтаж карты', 'Картаны орнату', 'Installation'],
  'kazakhstan': ['Карта РК с новыми областями', 'Жаңа облыстары бар ҚР картасы', 'Kazakhstan map with new regions'],
  'kz/k-navy': ['Ночная карта РК с подсветкой', 'Подсветкасы бар түнгі ҚР картасы', 'Night-style backlit Kazakhstan map'],
  'kz/k-phys': ['Физическая карта Казахстана', 'Қазақстанның физикалық картасы', 'Physical map of Kazakhstan'],
  'kz/k-phys2': ['Физическая карта РК с подсветкой', 'Подсветкасы бар ҚР физикалық картасы', 'Backlit physical map of Kazakhstan'],
  'kz/k-dark': ['Карта РК в переговорной', 'Келіссөз бөлмесіндегі ҚР картасы', 'Kazakhstan map in a meeting room'],
  'kz/k-reception': ['Карта РК на ресепшене', 'Ресепшендегі ҚР картасы', 'Kazakhstan map at a reception'],
  'relief/r3019': ['Рельефная 3D-карта РК', 'ҚР рельефті 3D картасы', '3D relief map of Kazakhstan'],
  'relief/r3018': ['Рельефная карта Казахстана', 'Қазақстанның рельефті картасы', 'Relief map of Kazakhstan'],
  'irere': ['Карта РК с логотипом IRERE education', 'IRERE education логотипі бар ҚР картасы', 'Kazakhstan map with IRERE education logo'],
  'office': ['Карта РК и логотип INTANT', 'ҚР картасы және INTANT логотипі', 'Kazakhstan map and INTANT logo'],
  'tab-kz': ['Карта РК в фирменных цветах', 'Фирмалық түстердегі ҚР картасы', 'Kazakhstan map in brand colours'],
  'gift/la': ['Логотип над картой РК в офисе', 'Кеңседегі ҚР картасының үстіндегі логотип', 'Logo above a Kazakhstan map in an office'],
  'gift/intant': ['INTANT: карта и логотип на ресепшене', 'INTANT: ресепшендегі карта мен логотип', 'INTANT: map and logo at the reception'],
  'gift/irere2': ['IRERE education: логотип и карта', 'IRERE education: логотип пен карта', 'IRERE education: logo and map'],
  'gift/clock': ['Часы с логотипом INTANT', 'INTANT логотипі бар сағат', 'Clock with the INTANT logo'],
  'gift/shezhire': ['Шежіре — родословное древо', 'Шежіре — ата-тек ағашы', 'Shezhire family tree'],
  'gift/autopapa': ['Брендированная картина AUTO PAPA', 'AUTO PAPA брендтелген суреті', 'Branded artwork for AUTO PAPA'],
  'mirrors/m1': ['Instagram-зеркало для салона', 'Салонға арналған Instagram-айна', 'Instagram mirror for a salon'],
  'mirrors/m3': ['Instagram-зеркало с подсветкой', 'Подсветкасы бар Instagram-айна', 'Backlit Instagram mirror'],
  'services/poster': ['Брендированная картина для автосалона', 'Автосалонға брендтелген сурет', 'Branded artwork for a car dealer'],
  'services/interior2': ['Оформление детского сада', 'Балабақшаны безендіру', 'Kindergarten interior'],
  'panels/school-mural': ['Панно для школы', 'Мектепке арналған панно', 'School wall art'],
 'services/panels': ['Декор-панель «Робот»', '«Робот» декор-панелі', '“Robot” wall panel'],
  'services/painting': ['Картина в раме для офиса', 'Кеңсеге арналған жақтаудағы сурет', 'Framed artwork for an office'],
  'panels/fairies': ['Панель с подсветкой «Феи»', '«Перілер» подсветкалы панелі', 'Backlit “Fairies” panel'],
  'panels/space-corridor': ['Оформление коридора «Космос»', '«Ғарыш» дәлізін безендіру', '“Space” corridor design'],
  'panels/kids-robot': ['Панель для детского центра', 'Балалар орталығына арналған панель', 'Panel for a kids’ centre'],
  'panels/planets': ['Панель «Планеты»', '«Планеталар» панелі', '“Planets” panel'],
  'mirrors/m4': ['Instagram-зеркало для школы', 'Мектепке арналған Instagram-айна', 'Instagram mirror for a school'],
 },
 'cities': [
  ['Астана','Алматы','Шымкент','Караганда','Актобе','Атырау','Актау','Павлодар','Усть-Каменогорск','Семей','Костанай','Кызылорда','Тараз','Уральск','Петропавловск','Туркестан','Кокшетау','Талдыкорган','Жезказган','Экибастуз','Другой город'],
  ['Астана','Алматы','Шымкент','Қарағанды','Ақтөбе','Атырау','Ақтау','Павлодар','Өскемен','Семей','Қостанай','Қызылорда','Тараз','Орал','Петропавл','Түркістан','Көкшетау','Талдықорған','Жезқазған','Екібастұз','Басқа қала'],
  ['Astana','Almaty','Shymkent','Karaganda','Aktobe','Atyrau','Aktau','Pavlodar','Oskemen','Semey','Kostanay','Kyzylorda','Taraz','Oral','Petropavl','Turkistan','Kokshetau','Taldykorgan','Zhezkazgan','Ekibastuz','Other city'],
 ],
 'anyCity': ['в вашем городе', 'сіздің қалаңызда', 'in your city'],
}

# Аналитика: Яндекс Метрика уже есть (тот же счётчик, что на /whatsapp).
# Meta Pixel: создайте в Meta Events Manager и впишите ID сюда, затем пересоберите.
YM_ID = '103848088'
META_PIXEL_ID = '576043711342731'
OAI_PIXEL_ID = 'DipQq4rYeV9NBQEsWQdgFW'  # OpenAI Ads (реклама в ChatGPT)

import hashlib
VER = hashlib.md5(open(os.path.join(ROOT, 'assets', 'style.css'), 'rb').read()).hexdigest()[:8]

IMGV = hashlib.md5(b''.join(open(os.path.join(dp, f), 'rb').read() for dp, _, fs in sorted(os.walk(os.path.join(ROOT, 'img'))) for f in sorted(fs))).hexdigest()[:8]

LANGS = [('ru', 'ru', ''), ('kk', 'kk', 'kz/'), ('en', 'en', 'en/')]
LABEL = {'ru': 'RU', 'kk': 'ҚАЗ', 'en': 'EN'}
PAGES = [('world', ''), ('kz', 'kazakhstan/'), ('biz', 'business/')]
HERO = {'world': 'hero-wide.jpg', 'kz': 'hero-kz.jpg', 'biz': 'hero-biz.jpg'}

# Тексты, которые отличаются на трёх страницах (мир / Казахстан / бизнес)
PT = {
 'kz': {
  'title': ['Карта Казахстана из дерева с подсветкой — ECOMAPS', 'Подсветкасы бар ағаш Қазақстан картасы — ECOMAPS', 'Wooden backlit map of Kazakhstan — ECOMAPS'],
  'desc': ['Деревянная карта Казахстана с новыми областями и рельефная 3D-карта РК — наша разработка. Логотип в подарок, доставка и монтаж по всему Казахстану.', 'Жаңа облыстары бар ағаш Қазақстан картасы және ҚР рельефті 3D картасы. Логотип сыйлыққа, бүкіл Қазақстан бойынша жеткізу және орнату.', ''],
  'og_title': ['ECOMAPS — карта Казахстана из дерева', 'ECOMAPS — ағаштан жасалған Қазақстан картасы', 'ECOMAPS — wooden map of Kazakhstan'],
  'h1k': ['', '', ''],
  'h1a': ['Карта Казахстана', 'Қазақстан картасы', 'Map of Kazakhstan'],
  'h1b': ['из дерева', 'ағаштан', 'in wood'],
  'hero_lead': ['Новые границы областей, подсветка, логотип компании и рельефная 3D-карта РК, которую в Казахстане делаем только мы.', 'Облыстардың жаңа шекаралары, подсветка, компания логотипі және Қазақстанда тек біз жасайтын ҚР рельефті 3D картасы.', 'New regional borders, backlight, your company logo and a 3D relief map of Kazakhstan that only we make.'],
  'cat_h_a': ['Выберите', 'Қазақстан картасын', 'Choose'],
  'cat_h_b': ['карту Казахстана', 'таңдаңыз', 'your Kazakhstan map'],
  'hero_alt': ['Рельефная карта Казахстана с подсветкой', 'Подсветкасы бар Қазақстанның рельефті картасы', 'Backlit relief map of Kazakhstan'],
 },
 'biz': {
  'title': ['Декор для бизнеса: панели, зеркала, картины — ECOMAPS', 'Бизнеске декор: панельдер, айналар, суреттер — ECOMAPS', 'Business décor: panels, mirrors, artwork — ECOMAPS'],
  'desc': ['Декор-панели, Instagram-зеркала, брендированные картины и карты с логотипом для офисов, салонов и школ. Своё производство, монтаж по Казахстану.', 'Кеңсе, салон және мектепке декор-панельдер, Instagram-айналар, брендтелген суреттер мен логотипі бар карталар. Өз өндірісіміз, бүкіл ҚР бойынша орнату.', ''],
  'og_title': ['ECOMAPS — декор для бизнеса', 'ECOMAPS — бизнеске арналған декор', 'ECOMAPS — décor for business'],
  'h1k': ['Декор-панели, Instagram-зеркала и картины для бизнеса', 'Бизнеске арналған декор-панельдер, Instagram-айналар және суреттер', 'Wall panels, Instagram mirrors and artwork for business'],
  'h1a': ['Декор, который', 'Сізді есте', 'Décor that makes'],
  'h1b': ['запоминают', 'қалдыратын декор', 'you memorable'],
  'hero_lead': ['Декор-панели, Instagram-зеркала и картины в фирменном стиле для офисов, салонов, школ и кафе. Своё производство и монтаж по всему Казахстану.', 'Кеңсе, салон, мектеп және кафеге арналған фирмалық стильдегі декор-панельдер, Instagram-айналар және суреттер. Өз өндірісіміз және бүкіл Қазақстан бойынша орнату.', 'Wall panels, Instagram mirrors and artwork in your brand style for offices, salons, schools and cafés. Own production and installation across Kazakhstan.'],
  'hero_alt': ['Декор-панель, Instagram-зеркало и картина', 'Декор-панель, Instagram-айна және сурет', 'Wall panel, Instagram mirror and artwork'],
  'cat_h_a': ['Что сделаем', 'Бизнесіңіз үшін', 'What we make'],
  'cat_h_b': ['для бизнеса', 'не жасаймыз', 'for business'],
  'badge': ['Логотип компании в подарок к заказу', 'Тапсырысқа компания логотипі сыйлыққа', 'Your company logo free with your order'],
 },
}
PT['kz']['desc'][2] = 'Wooden maps of Kazakhstan with the new regions and a 3D relief map we developed ourselves. Free company logo, shipping to the UAE, Qatar and worldwide.'
PT['biz']['desc'][2] = 'Wall panels, Instagram mirrors, branded artwork and maps with your logo for offices, salons and schools. Made in Kazakhstan, shipped worldwide.'
PT['biz']['hero_lead'][2] = 'Wall panels, Instagram mirrors and artwork in your brand style for offices, salons, schools and cafés. Own production in Kazakhstan, delivery to the UAE, Qatar and worldwide.'

# Kaspi и omarket показываем только на русской и казахской версиях
OMARKET = 'https://omarket.kz/catalog/ecc_uchebnoe_oborudovanie/ecc_demonstracionnye_materialy/nastennye_karty/dekorativnaia-karta-mira-ecomaps-km-nastennaia-100x70x2-sm.html'
KASPI = 'https://l.kaspi.kz/shop/HHgEF6jwWSDbpnh'
def pay_html(code, v):
    corp = f'<a class="js-wa" href="https://ecomaps.kz/whatsapp" data-place="pay-corp">{esc(v["pay3"])} ↗</a>'
    if code == 'en': return f'<div class="pay">{corp}</div>'
    return (f'<div class="pay"><span><b>Kaspi</b> Red · 0-0-12 · 0-0-24</span><a href="{KASPI}" target="_blank" rel="noopener" data-track="outbound" data-to="kaspi">{esc(v["pay2"])} ↗</a>'
            f'{corp}<a href="{OMARKET}" target="_blank" rel="noopener" data-track="outbound" data-to="omarket">omarket.kz ↗</a></div>')
def shop_links(code, v):
    if code == 'en': return ''
    return (f'<a href="{KASPI}" target="_blank" rel="noopener" data-track="outbound" data-to="kaspi">Kaspi {esc(v["shop"])}</a>\n'
            f'      <a href="{OMARKET}" target="_blank" rel="noopener" data-track="outbound" data-to="omarket">omarket.kz</a>')

CALC = {
 'world': [['Карта мира', 'Әлем картасы', 'World map'], ['Карта Казахстана', 'Қазақстан картасы', 'Kazakhstan map'], ['Рельефная карта РК', 'ҚР рельефті картасы', 'Relief KZ map'], ['Другое', 'Басқа', 'Other']],
 'biz': [['Декор-панель', 'Декор-панель', 'Wall panel'], ['Instagram-зеркало', 'Instagram-айна', 'Instagram mirror'], ['Картина', 'Сурет', 'Artwork'], ['Карта с логотипом', 'Логотипі бар карта', 'Map with logo']],
}
CALC['world'] = [['Классическая', 'Классикалық', 'Classic'], ['Физическая', 'Физикалық', 'Physical'], ['С флагами', 'Жалаулармен', 'With flags'], ['Своя расцветка', 'Өз түсіңіз', 'Custom colours']]
CALC['kz'] = [['Карта РК', 'ҚР картасы', 'Kazakhstan map'], ['Рельефная 3D', 'Рельефті 3D', '3D relief'], ['С логотипом', 'Логотиппен', 'With logo'], ['Другое', 'Басқа', 'Other']]
CALC_DEF = {'world': 0, 'kz': 0, 'biz': 0}

def esc(s): return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')

# ---------- Свои вопросы и текст на каждой странице (чтобы страницы не дублировали друг друга) ----------
# Пустая строка = вопрос не показываем на этом языке (на EN нет госзакупок и Kaspi).
FQ = {
 'k1q': ['На карте новые области?', 'Картада жаңа облыстар бар ма?', 'Does the map show the new regions?'],
 'k1a': ['Да. Карта соответствует актуальному делению РК, включая Абайскую, Жетысускую и Улытаускую области, созданные в 2022 году.', 'Иә. Карта ҚР-дың қазіргі әкімшілік бөлінісіне сай, 2022 жылы құрылған Абай, Жетісу және Ұлытау облыстары да бар.', 'Yes. The map follows the current administrative division of Kazakhstan, including the Abai, Zhetysu and Ulytau regions created in 2022.'],
 'k2q': ['Чем рельефная карта отличается от обычной?', 'Рельефті картаның қарапайым картадан айырмашылығы неде?', 'How is the relief map different from the regular one?'],
 'k2a': ['Обычная карта собирается из плоских деталей. В рельефной горы, степи и впадины вырезаны фрезой на станке с ЧПУ, поэтому объёмно видны Алтай, Тянь-Шань и низменности Прикаспия.', 'Қарапайым карта жалпақ бөлшектерден құрастырылады. Рельефті картада таулар, далалар мен ойпаттар ЦББ станогында фрезамен ойылады, сондықтан Алтай, Тянь-Шань және Каспий маңы ойпаты көлемді көрінеді.', 'The regular map is assembled from flat pieces. On the relief map, mountains, steppes and lowlands are carved on a CNC router, so the Altai, the Tien Shan and the Caspian lowland stand out in 3D.'],
 'k3q': ['На каком языке надписи?', 'Жазулар қай тілде?', 'What language are the labels in?'],
 'k3a': ['На казахском, русском или английском — на ваш выбор.', 'Қазақ, орыс немесе ағылшын тілінде — өзіңіз таңдайсыз.', 'Kazakh, Russian or English, whichever you choose.'],
 'k4q': ['Можно сделать карту в цветах компании и с логотипом?', 'Картаны компания түстерінде және логотиппен жасауға бола ма?', 'Can the map be made in our brand colours with our logo?'],
 'k4a': ['Да. Области окрашиваем разными оттенками или в фирменных цветах, а логотип к заказу карты для офиса делаем в подарок.', 'Иә. Облыстарды әртүрлі реңкке немесе фирмалық түстерге бояймыз, ал кеңсеге карта тапсырыс бергенде логотипті сыйлыққа жасаймыз.', 'Yes. Regions can be painted in different shades or in your brand colours, and we make your logo for free when you order a map for your office.'],
 'k5q': ['Работаете ли с госучреждениями и школами?', 'Мемлекеттік мекемелер мен мектептермен жұмыс істейсіздер ме?', ''],
 'k5a': ['Да. У нас индустриальный сертификат НПП «Атамекен» и сертификат СТ-KZ, карты есть на omarket.kz. Работаем по безналу и через госзакупки.', 'Иә. Бізде «Атамекен» ҰКП индустриялық сертификаты және СТ-KZ сертификаты бар, карталарымыз omarket.kz-те бар. Қолма-қолсыз және мемлекеттік сатып алу арқылы жұмыс істейміз.', ''],
 'b1q': ['Что такое Instagram-зеркало?', 'Instagram-айна деген не?', 'What is an Instagram mirror?'],
 'b1a': ['Зеркало в виде поста Instagram с вашим аккаунтом, логотипом, QR-кодом и подсветкой. Его ставят как фотозону в салоне, кофейне, магазине или офисе.', 'Аккаунтыңыз, логотип, QR-код және подсветкасы бар Instagram жазбасы түріндегі айна. Оны салонда, кофеханада, дүкенде немесе кеңседе фотоаймақ ретінде қояды.', 'A mirror styled as an Instagram post with your account, logo, QR code and backlight. It works as a photo zone in a salon, café, shop or office.'],
 'b2q': ['Можно заранее увидеть, как декор будет смотреться у нас?', 'Декордың бізде қалай көрінетінін алдын ала көруге бола ма?', 'Can we see how the décor will look in our space?'],
 'b2a': ['Да. Пришлите фото помещения в WhatsApp, и мы бесплатно сделаем визуализацию.', 'Иә. Бөлменің фотосын WhatsApp-қа жіберіңіз, біз тегін визуализация жасаймыз.', 'Yes. Send us a photo of the room on WhatsApp and we will make a free mock-up.'],
 'b3q': ['Делаете ли по нашему дизайну?', 'Біздің дизайн бойынша жасайсыздар ма?', 'Can you work from our own design?'],
 'b3a': ['Да. Есть больше 20 готовых шаблонов панелей, но можем сделать по вашему макету или в фирменном стиле компании.', 'Иә. 20-дан астам дайын панель үлгісі бар, бірақ сіздің макетіңіз бойынша немесе компанияның фирмалық стилінде жасай аламыз.', 'Yes. We have over 20 ready panel templates, and we can also work from your artwork or in your corporate style.'],
 'b4q': ['Работаете ли с юрлицами и госзакупками?', 'Заңды тұлғалармен және мемлекеттік сатып алу арқылы жұмыс істейсіздер ме?', 'Do you work with companies?'],
 'b4a': ['Да: безнал по счёту, госзакупки и omarket.kz. У нас индустриальный сертификат НПП «Атамекен» и сертификат СТ-KZ.', 'Иә: шот бойынша қолма-қолсыз төлем, мемлекеттік сатып алу және omarket.kz. Бізде «Атамекен» ҰКП индустриялық сертификаты және СТ-KZ сертификаты бар.', 'Yes. We issue invoices for international bank transfer and ship to your country.'],
}
FAQ_SET = {'world': ['f1', 'f2', 'f3', 'f4', 'f5', 'f6'],
           'kz':    ['k1', 'k2', 'k3', 'k4', 'k5', 'f3'],
           'biz':   ['b1', 'b2', 'b3', 'b4', 'f2', 'f3']}

ABOUT = {
 'kz': {
  'h': ['Деревянная карта Казахстана на стену', 'Қабырғаға арналған ағаш Қазақстан картасы', 'A wooden map of Kazakhstan for your wall'],
  'p': [
   ['Карту Казахстана ECOMAPS делаем на своём производстве в Астане. Изображение печатаем, ламинируем, переносим на HDF и вырезаем лазером, поэтому каждая область — отдельная деталь, а границы совпадают с актуальной административной картой.',
    'Для кабинетов руководителей, акиматов и школ делаем рельефную 3D-карту: горы и впадины фрезеруем на станке с ЧПУ по MDF. Карту можно сделать в фирменных цветах, добавить логотип, подсветку и надписи на казахском, русском или английском языке.',
    'Доставляем и устанавливаем по всему Казахстану. Для организаций работаем по безналу и через госзакупки.'],
   ['ECOMAPS Қазақстан картасын Астанадағы өз өндірісімізде жасаймыз. Суретті басып шығарып, ламинациялап, HDF-ке түсіреміз де лазермен кесеміз, сондықтан әр облыс — жеке бөлшек, ал шекаралар қазіргі әкімшілік картаға сай келеді.',
    'Басшылар кабинеттеріне, әкімдіктер мен мектептерге рельефті 3D карта жасаймыз: таулар мен ойпаттарды MDF-ке ЦББ станогында фрезалаймыз. Картаны фирмалық түстерде жасап, логотип, подсветка және қазақ, орыс немесе ағылшын тіліндегі жазулар қосуға болады.',
    'Бүкіл Қазақстан бойынша жеткізіп, орнатамыз. Ұйымдармен қолма-қолсыз және мемлекеттік сатып алу арқылы жұмыс істейміз.'],
   ['We make ECOMAPS maps of Kazakhstan at our own workshop in Astana. The image is printed, laminated, mounted on HDF and laser-cut, so every region is a separate piece and the borders match the current administrative map.',
    'For executive offices and schools we also make a 3D relief map, with mountains and lowlands carved into MDF on a CNC router. The map can be made in your brand colours, with your logo, backlight and labels in Kazakh, Russian or English.',
    'We ship to the UAE, Qatar and worldwide, with installation instructions and video-call support.'],
  ],
 },
 'biz': {
  'h': ['Декор для офиса, салона и школы', 'Кеңсе, салон және мектепке арналған декор', 'Décor for offices, salons and schools'],
  'p': [
   ['ECOMAPS делает интерьерный декор под фирменный стиль: многоуровневые панели из дерева, HDF и MDF, Instagram-зеркала с подсветкой, брендированные картины, карты мира и Казахстана с логотипом компании. Режем, гравируем, печатаем и собираем сами в Астане.',
    'Среди наших заказчиков — офисы и ресепшены, салоны, автосалоны, школы, детские сады и детские центры. До заказа бесплатно показываем декор на фото вашего помещения.',
    'Работаем с юрлицами по безналу и через госзакупки, доставляем и монтируем по всему Казахстану. К заказу карты для офиса логотип компании делаем в подарок.'],
   ['ECOMAPS фирмалық стильге сай интерьер декорын жасайды: ағаш, HDF және MDF-тен көп деңгейлі панельдер, подсветкасы бар Instagram-айналар, брендтелген суреттер, компания логотипі бар әлем және Қазақстан карталары. Астанада өзіміз кесеміз, гравировка жасаймыз, басып шығарамыз және құрастырамыз.',
    'Тапсырыс берушілеріміздің арасында кеңселер мен ресепшендер, салондар, автосалондар, мектептер, балабақшалар және балалар орталықтары бар. Тапсырысқа дейін декорды бөлмеңіздің фотосында тегін көрсетеміз.',
    'Заңды тұлғалармен қолма-қолсыз және мемлекеттік сатып алу арқылы жұмыс істейміз, бүкіл Қазақстан бойынша жеткізіп, орнатамыз. Кеңсеге карта тапсырыс берсеңіз, компания логотипін сыйлыққа жасаймыз.'],
   ['ECOMAPS makes interior décor in your corporate style: multi-layer panels in wood, HDF and MDF, backlit Instagram mirrors, branded artwork, and world and Kazakhstan maps with your company logo. We cut, engrave, print and assemble everything ourselves in Astana.',
    'Our clients include offices and receptions, salons, car dealerships, schools, kindergartens and kids’ centres. Before you order, we show the décor on a photo of your space for free.',
    'We work with companies by invoice and ship to the UAE, Qatar and worldwide. When you order a map for your office, we make your company logo for free.'],
  ],
 },
}
ABOUT_KICKER = ['О продукции', 'Өнім туралы', 'About']

def faq_items(mode, i, v):
    out = []
    for q in FAQ_SET[mode]:
        qq, aa = (FQ[q + 'q'][i], FQ[q + 'a'][i]) if q + 'q' in FQ else (v[q + 'q'], v[q + 'a'])
        if qq: out.append((q, qq, aa))
    return out

def faq_html(mode, i, v):
    rows = []
    for q, qq, aa in faq_items(mode, i, v):
        extra = ' (<a href="https://2gis.kz/astana/geo/70000001057229459" target="_blank" rel="noopener">2GIS</a>)' if q == 'f6' else ''
        rows.append(f'      <details><summary><h3>{esc(qq)}</h3></summary><p>{esc(aa)}{extra}</p></details>')
    return '\n'.join(rows)

def about_html(mode, i):
    if mode not in ABOUT: return ''
    a = ABOUT[mode]
    ps = ''.join(f'<p>{esc(x)}</p>' for x in a['p'][i])
    return (f'<section class="about-sec" id="about">\n  <div class="wrap">\n    <span class="kicker">{esc(ABOUT_KICKER[i])}</span>\n'
            f'    <h2>{esc(a["h"][i])}</h2>\n    <div class="about-tx">{ps}</div>\n  </div>\n</section>\n')

def strip_modes(html, mode):
    """Убирает из HTML блоки других страниц (data-m без текущего режима), а не прячет их стилями:
    поисковик видит только текст этой страницы."""
    pos = 0
    while True:
        m = re.compile(r'<(\w+)\b[^>]*\sdata-m="([^"]+)"[^>]*>').search(html, pos)
        if not m: return html
        if mode in m.group(2).split():
            pos = m.end(); continue
        tag = m.group(1); depth = 1; k = m.end()
        tok = re.compile(r'<(/?)' + tag + r'\b[^>]*>')
        while depth:
            t = tok.search(html, k)
            depth += -1 if t.group(1) else 1; k = t.end()
        html = html[:m.start()] + html[k:]
        pos = m.start()

def h1_html(v):
    if v.get('h1k'):  # ключевая фраза — в H1, слоган — отдельной строкой
        return (f'<h1 class="reveal h1-key">{esc(v["h1k"])}</h1>\n'
                f'    <p class="h1s reveal">{esc(v["h1a"])} <em>{esc(v["h1b"])}</em></p>')
    return f'<h1 class="reveal">{esc(v["h1a"])} <em>{esc(v["h1b"])}</em></h1>'
RAW = ('oai_pixel', 'ver', 'langlinks', 'jsdata', 'P', 'path', 'htmllang', 'ym_id', 'meta_pixel', 'hreflangs', 'calc_types',
       'href_world', 'href_kz', 'href_biz', 'mode', 'hero_img', 'hero_webp', 'h1_html', 'faq_html', 'about_html', 'jsonld', 'h1k_html', 'pay_html', 'shop_links')

# ---------- SEO: разметка schema.org (компания, товар, вопросы) ----------
STORE_ID = 'https://ecomaps.kz/#store'
def jsonld(mode, i, path, v):
    url = 'https://ecomaps.kz/' + path
    store = {'@type': ['Store', 'Organization'], '@id': STORE_ID, 'name': 'ECOMAPS', 'legalName': 'ТОО «ECOMAPS»',
             'url': 'https://ecomaps.kz/', 'logo': 'https://ecomaps.kz/img/ads/logo-square.png', 'image': 'https://ecomaps.kz/img/hero-wide.jpg',
             'telephone': '+77762979276', 'priceRange': '₸₸',
             'address': {'@type': 'PostalAddress', 'streetAddress': 'ул. Сарайшык, 7/1', 'addressLocality': 'Астана', 'addressCountry': 'KZ'},
             'areaServed': ([{'@type': 'Country', 'name': n} for n in ('Kazakhstan', 'United Arab Emirates', 'Qatar')] if LANGS[i][0] == 'en' else {'@type': 'Country', 'name': 'Kazakhstan'}),
             'sameAs': ['https://www.instagram.com/ecomaps.kz/', 'https://2gis.kz/astana/geo/70000001057229459', 'https://l.kaspi.kz/shop/HHgEF6jwWSDbpnh']}
    page = {'@type': 'WebPage', '@id': url + '#page', 'url': url, 'name': v['title'], 'description': v['desc'],
            'inLanguage': LANGS[i][1], 'isPartOf': {'@type': 'WebSite', '@id': 'https://ecomaps.kz/#site', 'url': 'https://ecomaps.kz/', 'name': 'ECOMAPS'},
            'about': {'@id': STORE_ID}}
    prod = {'@type': 'Product', 'name': {'world': v['h1k'] or v['title'], 'kz': v['h1a'] + ' ' + v['h1b'], 'biz': v['h1k']}[mode],
            'description': v['hero_lead'], 'brand': {'@type': 'Brand', 'name': 'ECOMAPS'},
            'image': 'https://ecomaps.kz/img/' + HERO[mode], 'url': url}
    if mode == 'world':  # цена «от 54 000 ₸» — как в рекламе
        prod['offers'] = {'@type': 'AggregateOffer', 'priceCurrency': 'KZT', 'lowPrice': 54000, 'availability': 'https://schema.org/InStock',
                          'seller': {'@id': STORE_ID}, 'url': url}
    faq = {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': qq,
                                               'acceptedAnswer': {'@type': 'Answer', 'text': aa}} for _, qq, aa in faq_items(mode, i, v)]}
    # товар с ценой — только на странице карты мира (без цены Google считает разметку товара ошибкой)
    data = {'@context': 'https://schema.org', '@graph': [store, page] + ([prod] if mode == 'world' else []) + [faq]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'


for mode, pp in PAGES:
    for i, (code, htmllang, lp) in enumerate(LANGS):
        path = lp + pp
        P = '../' * path.count('/')
        out = tpl
        links = [f'<a href="/{l2}{pp}" hreflang="{c2}"{" class=\"on\"" if i == j else ""}>{LABEL[c2]}</a>'
                 for j, (c2, _, l2) in enumerate(LANGS)]
        hl = [f'<link rel="alternate" hreflang="{c2}" href="https://ecomaps.kz/{l2}{pp}">' for c2, _, l2 in LANGS]
        hl.append(f'<link rel="alternate" hreflang="x-default" href="https://ecomaps.kz/{pp}">')
        vals = {k: v[i] for k, v in T.items()}
        vals.update({k: v[i] for k, v in PT.get(mode, {}).items()})
        ct = ''.join(f'<button{" class=\"on\"" if n == CALC_DEF[mode] else ""}>{esc(x[i])}</button>' for n, x in enumerate(CALC[mode]))
        vals.update(oai_pixel=OAI_PIXEL_ID, ver=VER, ym_id=YM_ID, meta_pixel=META_PIXEL_ID, htmllang=htmllang, path=path, P=P, mode=mode,
                    langlinks=''.join(links), hreflangs='\n'.join(hl), calc_types=ct, hero_img=HERO[mode],
                    **{f'href_{m}': f'/{lp}{p}' for m, p in PAGES})
        vals['h1_html'] = h1_html(vals)
        vals['hero_webp'] = HERO[mode].replace('.jpg', '.webp')
        vals['faq_html'] = faq_html(mode, i, vals)
        vals['about_html'] = about_html(mode, i)
        vals['jsonld'] = jsonld(mode, i, path, vals)
        vals['pay_html'] = pay_html(code, vals)
        vals['shop_links'] = shop_links(code, vals)
        js = {'cap': {k: v[i] for k, v in JS['cap'].items()}}
        vals['jsdata'] = json.dumps(js, ensure_ascii=False)
        def sub(m):
            k = m.group(1)
            if k not in vals: raise KeyError(k)
            return vals[k] if k in RAW else esc(vals[k])
        out = re.sub(r'\{\{(\w+)\}\}', sub, out)
        out = strip_modes(out, mode)
        # версия картинок: при замене фото браузер сразу загрузит новое
        out = re.sub(r'(img/[\w/\-]+\.(?:jpg|webp|png|svg))(?!\?)', lambda m: m.group(1) + '?v=' + IMGV, out)
        out = out.replace('.webp" alt="${C[k]}"', '.webp?v=' + IMGV + '" alt="${C[k]}"')
        # Английская версия (ОАЭ, Катар): все кнопки WhatsApp — сразу на 77064299895,
        # без распределителя /whatsapp, с готовым текстом, чтобы менеджер видел, что клиент с EN-сайта.
        if code == 'en':
            # акция только для Казахстана — на EN полоску не показываем
            out = re.sub(r'\n  <div class="sale-bar".*?</script>', '', out, count=1, flags=re.S)
            out = out.replace('href="https://ecomaps.kz/whatsapp"', 'href="' + EN_WA + '"')
        dst = os.path.join(ROOT, path, 'index.html')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'w', encoding='utf-8').write(out)
        print('built', path or '/')


# ---------- SEO: robots.txt и sitemap.xml ----------
today = __import__('datetime').date.today().isoformat()
urls = []
for mode, pp in PAGES:
    alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{c}" href="https://ecomaps.kz/{l}{pp}"/>' for c, _, l in LANGS)
    alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="https://ecomaps.kz/{pp}"/>'
    for c, _, l in LANGS:
        pr = '1.0' if not (l + pp) else '0.8'
        urls.append(f'<url><loc>https://ecomaps.kz/{l}{pp}</loc><lastmod>{today}</lastmod><priority>{pr}</priority>{alts}</url>')
open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
    'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(urls) + '\n</urlset>\n')
open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8').write(
    'User-agent: *\nAllow: /\n\n'
    'Host: https://ecomaps.kz\nSitemap: https://ecomaps.kz/sitemap.xml\n')
print('built sitemap.xml, robots.txt')
