#!/usr/bin/env python3
"""Собирает три языковые версии сайта из src/template.html:
   /index.html (ru), /kz/index.html (kk), /en/index.html (en)."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, 'src', 'template.html'), encoding='utf-8').read()

T = {
 'title': ['ECOMAPS — деревянная карта мира с подсветкой', 'ECOMAPS — подсветкасы бар ағаш әлем картасы', 'ECOMAPS — wooden backlit world map'],
 'desc': ['Многоуровневые деревянные карты мира с подсветкой: 3 размера или ваш, 13 расцветок, надписи на русском, казахском или английском. Изготовление за 8 рабочих дней, доставка и установка по всему Казахстану, рассрочка Kaspi.', 'Подсветкасы бар көп деңгейлі ағаш әлем карталары: 3 өлшем немесе өзіңіздікі, 13 түс, жазулар орыс, қазақ немесе ағылшын тілінде. 8 жұмыс күнінде дайындаймыз, бүкіл Қазақстан бойынша жеткізу және орнату, Kaspi бөліп төлеу.', 'Multi-layer wooden world maps with backlight: 3 sizes or your own, 13 colour schemes, labels in Russian, Kazakh or English. Made in 8 working days, delivery and installation across Kazakhstan, Kaspi installments.'],
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
 'badge': ['Логотип компании на карте в подарок', 'Компания логотипі картаға сыйлыққа', 'Your company logo on the map for free'],
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
META_PIXEL_ID = ''

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
  'desc': ['Деревянные карты Казахстана с новыми областями и рельефная 3D-карта РК — наша разработка. Логотип компании в подарок, доставка и установка по всему Казахстану.', 'Жаңа облыстары бар ағаш Қазақстан карталары және ҚР рельефті 3D картасы — біздің әзірлеме. Компания логотипі сыйлыққа, бүкіл Қазақстан бойынша жеткізу және орнату.', 'Wooden maps of Kazakhstan with the new regions and a 3D relief map we developed ourselves. Free company logo, delivery and installation across Kazakhstan.'],
  'og_title': ['ECOMAPS — карта Казахстана из дерева', 'ECOMAPS — ағаштан жасалған Қазақстан картасы', 'ECOMAPS — wooden map of Kazakhstan'],
  'h1a': ['Карта Казахстана', 'Қазақстан картасы', 'Map of Kazakhstan'],
  'h1b': ['из дерева', 'ағаштан', 'in wood'],
  'hero_lead': ['Новые границы областей, подсветка, логотип компании и рельефная 3D-карта РК, которую в Казахстане делаем только мы.', 'Облыстардың жаңа шекаралары, подсветка, компания логотипі және Қазақстанда тек біз жасайтын ҚР рельефті 3D картасы.', 'New regional borders, backlight, your company logo and a 3D relief map of Kazakhstan that only we make.'],
  'cat_h_a': ['Выберите', 'Қазақстан картасын', 'Choose'],
  'cat_h_b': ['карту Казахстана', 'таңдаңыз', 'your Kazakhstan map'],
  'hero_alt': ['Рельефная карта Казахстана с подсветкой', 'Подсветкасы бар Қазақстанның рельефті картасы', 'Backlit relief map of Kazakhstan'],
 },
 'biz': {
  'title': ['Декор для бизнеса: панели, Instagram-зеркала, картины — ECOMAPS', 'Бизнеске арналған декор: панельдер, Instagram-айналар, суреттер — ECOMAPS', 'Business décor: wall panels, Instagram mirrors, artwork — ECOMAPS'],
  'desc': ['Декоративные панели, Instagram-зеркала с подсветкой, брендированные картины и карты с логотипом для офисов, салонов, школ и кафе. Своё производство, монтаж по всему Казахстану.', 'Кеңсе, салон, мектеп және кафеге арналған сәндік панельдер, подсветкасы бар Instagram-айналар, брендтелген суреттер мен логотипі бар карталар. Өз өндірісіміз, бүкіл Қазақстан бойынша орнату.', 'Decorative wall panels, backlit Instagram mirrors, branded artwork and maps with your logo for offices, salons, schools and cafés. Own production, installation across Kazakhstan.'],
  'og_title': ['ECOMAPS — декор для бизнеса', 'ECOMAPS — бизнеске арналған декор', 'ECOMAPS — décor for business'],
  'h1a': ['Декор, который', 'Сізді есте', 'Décor that makes'],
  'h1b': ['запоминают', 'қалдыратын декор', 'you memorable'],
  'hero_lead': ['Декор-панели, Instagram-зеркала и картины в фирменном стиле для офисов, салонов, школ и кафе. Своё производство и монтаж по всему Казахстану.', 'Кеңсе, салон, мектеп және кафеге арналған фирмалық стильдегі декор-панельдер, Instagram-айналар және суреттер. Өз өндірісіміз және бүкіл Қазақстан бойынша орнату.', 'Wall panels, Instagram mirrors and artwork in your brand style for offices, salons, schools and cafés. Own production and installation across Kazakhstan.'],
  'hero_alt': ['Декор-панель, Instagram-зеркало и картина', 'Декор-панель, Instagram-айна және сурет', 'Wall panel, Instagram mirror and artwork'],
  'cat_h_a': ['Что сделаем', 'Бизнесіңіз үшін', 'What we make'],
  'cat_h_b': ['для бизнеса', 'не жасаймыз', 'for business'],
  'badge': ['Логотип компании в подарок к заказу', 'Тапсырысқа компания логотипі сыйлыққа', 'Your company logo free with your order'],
 },
}
CALC = {
 'world': [['Карта мира', 'Әлем картасы', 'World map'], ['Карта Казахстана', 'Қазақстан картасы', 'Kazakhstan map'], ['Рельефная карта РК', 'ҚР рельефті картасы', 'Relief KZ map'], ['Другое', 'Басқа', 'Other']],
 'biz': [['Декор-панель', 'Декор-панель', 'Wall panel'], ['Instagram-зеркало', 'Instagram-айна', 'Instagram mirror'], ['Картина', 'Сурет', 'Artwork'], ['Карта с логотипом', 'Логотипі бар карта', 'Map with logo']],
}
CALC['world'] = [['Классическая', 'Классикалық', 'Classic'], ['Физическая', 'Физикалық', 'Physical'], ['С флагами', 'Жалаулармен', 'With flags'], ['Своя расцветка', 'Өз түсіңіз', 'Custom colours']]
CALC['kz'] = [['Карта РК', 'ҚР картасы', 'Kazakhstan map'], ['Рельефная 3D', 'Рельефті 3D', '3D relief'], ['С логотипом', 'Логотиппен', 'With logo'], ['Другое', 'Басқа', 'Other']]
CALC_DEF = {'world': 0, 'kz': 0, 'biz': 0}

def esc(s): return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')
RAW = ('ver', 'langlinks', 'jsdata', 'P', 'path', 'htmllang', 'ym_id', 'meta_pixel', 'hreflangs', 'calc_types',
       'href_world', 'href_kz', 'href_biz', 'mode', 'hero_img')

for mode, pp in PAGES:
    for i, (code, htmllang, lp) in enumerate(LANGS):
        path = lp + pp
        P = '../' * path.count('/')
        out = tpl
        links = [f'<a href="{P}{l2}{pp}index.html" hreflang="{c2}"{" class=\"on\"" if i == j else ""}>{LABEL[c2]}</a>'
                 for j, (c2, _, l2) in enumerate(LANGS)]
        hl = [f'<link rel="alternate" hreflang="{c2}" href="https://ecomaps.kz/{l2}{pp}">' for c2, _, l2 in LANGS]
        hl.append(f'<link rel="alternate" hreflang="x-default" href="https://ecomaps.kz/{pp}">')
        vals = {k: v[i] for k, v in T.items()}
        vals.update({k: v[i] for k, v in PT.get(mode, {}).items()})
        ct = ''.join(f'<button{" class=\"on\"" if n == CALC_DEF[mode] else ""}>{esc(x[i])}</button>' for n, x in enumerate(CALC[mode]))
        vals.update(ver=VER, ym_id=YM_ID, meta_pixel=META_PIXEL_ID, htmllang=htmllang, path=path, P=P, mode=mode,
                    langlinks=''.join(links), hreflangs='\n'.join(hl), calc_types=ct, hero_img=HERO[mode],
                    **{f'href_{m}': f'{P}{lp}{p}index.html' for m, p in PAGES})
        js = {'cap': {k: v[i] for k, v in JS['cap'].items()}}
        vals['jsdata'] = json.dumps(js, ensure_ascii=False)
        def sub(m):
            k = m.group(1)
            if k not in vals: raise KeyError(k)
            return vals[k] if k in RAW else esc(vals[k])
        out = re.sub(r'\{\{(\w+)\}\}', sub, out)
        # версия картинок: при замене фото браузер сразу загрузит новое
        out = re.sub(r'(img/[\w/\-]+\.(?:jpg|png|svg))(?!\?)', lambda m: m.group(1) + '?v=' + IMGV, out)
        out = out.replace('.jpg" alt="${C[k]}"', '.jpg?v=' + IMGV + '" alt="${C[k]}"')
        dst = os.path.join(ROOT, path, 'index.html')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'w', encoding='utf-8').write(out)
        print('built', path or '/')
