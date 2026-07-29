#!/usr/bin/env python3
"""Собирает events.json — хронологию по каждому участку из всех источников проекта.

Источники: rosreestr_registry.html (документы), registrations.json (права и кадучёт),
kuvd.json (номера заявлений), councils/2320355400.json (постановления, статусы).
Ключ — украинский кадастр участка; здания привязываются к своему участку.
"""
import json, re, os, collections

REPO = os.path.dirname(os.path.abspath(__file__))
J = lambda n: json.load(open(os.path.join(REPO, n), encoding='utf-8'))

council = J('councils/2320355400.json')
regs = J('registrations.json')
kuvd = J('kuvd.json')
html = open(os.path.join(REPO, 'rosreestr_registry.html'), encoding='utf-8').read()
recs = json.loads(re.search(r'const records = (\[.*?\]);', html, re.S).group(1))

# --- привязка кадастра РФ → (укр. участок, что это за объект)
by_cad = {}
by_addr = {}
for p in council['parcels']:
    if p.get('cadrf'):
        by_cad[p['cadrf']] = (p['c'], 'участок', '')
    for b in (p.get('blds') or []):
        if b.get('cad'):
            by_cad[b['cad']] = (p['c'], 'здание', b.get('lit', ''))
    f = p.get('fias') or ''
    m = re.match(r'улица\s+(\S+),\s*(?:земельный участок|дом|здание)\s*(.+)$', f)
    if m:
        by_addr[(m.group(1).lower(), m.group(2).strip().lower())] = p['c']

def strip_lit(num):
    n = re.sub(r'\s*(строение|лит\.?)\s*[абвАБВ]\s*$', '', str(num or ''), flags=re.I)
    return n.strip().lower()

def locate(x):
    """Документ → (укр. участок, тип объекта, литера)."""
    c = x.get('cad_rf')
    if c and c in by_cad:
        return by_cad[c]
    st, num = (x.get('street') or '').lower(), strip_lit(x.get('number'))
    uk = by_addr.get((st, num))
    if uk:
        return (uk, 'здание' if x.get('object_type') == 'Здание' else 'участок',
                str(x.get('number') or '') if x.get('object_type') == 'Здание' else '')
    return (None, '', '')

def dnum(s):
    m = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', s or '')
    return int(m.group(3) + m.group(2) + m.group(1)) if m else None

def dstr(s):
    m = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', s or '')
    return f'{m.group(1)}.{m.group(2)}.{m.group(3)}' if m else ''

MONTHS = {'января':'01','февраля':'02','марта':'03','апреля':'04','мая':'05','июня':'06',
          'июля':'07','августа':'08','сентября':'09','октября':'10','ноября':'11','декабря':'12'}

def apply_date(details):
    """Дата подачи заявления из формулировки «по заявлению от 26.06.2026 №…»."""
    m = re.search(r'заявлени[юя]\s+от\s+(\d{1,2})[.\s]+(\d{2}|[а-я]+)[.\s]+(\d{4})', details or '', re.I)
    if not m:
        return ''
    dd, mm, yy = m.group(1).zfill(2), m.group(2), m.group(3)
    mm = MONTHS.get(mm.lower(), mm).zfill(2)
    return f'{dd}.{mm}.{yy}'

events = collections.defaultdict(list)

def add(uk, date, kind, title, sub='', obj='участок', lit='', src=''):
    if not uk:
        return
    events[uk].append({'d': dstr(date), 'n': dnum(date) or 0, 'k': kind,
                       't': title, 's': sub, 'o': obj, 'lit': lit, 'src': src})

# 1. Постановление о присвоении адреса РФ
for p in council['parcels']:
    if p.get('post'):
        add(p['c'], p['post'], 'addr', 'Постановление о присвоении адреса РФ',
            f"№ {re.sub(r'\\s*от\\s*\\d.*$', '', p['post'])}", src='councils')

# 2. Документы реестра
KIND = {'Приостановка': ('stop', 'Приостановка регистрации'),
        'Отказ': ('deny', 'Отказ Росреестра'),
        'Возврат': ('return', 'Возврат без рассмотрения'),
        'Сведения внесены': ('mvv', 'Адрес внесён в ЕГРН'),
        'Право зарегистрировано': ('right', 'Право зарегистрировано'),
        'Только кадастровый учёт': ('cad', 'Кадастровый учёт (право не зарегистрировано)')}
for x in recs:
    uk, obj, lit = locate(x)
    if not uk:
        continue
    kind, title = KIND.get(x.get('status') or '', ('doc', x.get('status') or 'Документ'))
    ad = apply_date(x.get('details'))
    if ad and x.get('kuvd'):
        add(uk, ad, 'apply', 'Заявление подано в Росреестр', x['kuvd'], obj, lit, x['file'])
    date = x.get('date_decision') or x.get('date_right') or x.get('date_cadastre') or x.get('date_vypiska')
    sub = ' · '.join(filter(None, [x.get('kuvd', ''), x.get('cad_rf', ''),
                                   (x.get('details') or '')[:150]]))
    add(uk, date, kind, title, sub, obj, lit, x['file'])

# 3. Регистрации права (номер записи) и кадучёт из registrations.json
for o in regs['owners']:
    for it in o['items']:
        uk = by_cad.get(it.get('cad', ''), (None, '', ''))[0]
        if not uk:
            continue
        obj = 'здание' if it.get('kind') == 'здание' else 'участок'
        add(uk, it.get('date', ''), 'right', 'Право зарегистрировано в ЕГРН',
            ' · '.join(filter(None, [it.get('right', ''), it.get('reg', ''), it.get('cad', '')])),
            obj, '', 'registrations.json')
for x in regs.get('pending', []):
    uk = by_cad.get(x.get('cad', ''), (None, '', ''))[0]
    if uk:
        add(uk, x.get('date', ''), 'cad', 'Кадастровый учёт (право не зарегистрировано)',
            x.get('cad', ''), 'участок', '', 'registrations.json')

# 4. Приостановки/отказы из полей участка (если такого события ещё нет)
for p in council['parcels']:
    if p.get('dst') in ('stop', 'deny'):
        have = any(e['k'] == p['dst'] and e['d'] == dstr(p.get('ddate')) for e in events.get(p['c'], []))
        if not have:
            add(p['c'], p.get('ddate', ''), p['dst'],
                'Приостановка регистрации' if p['dst'] == 'stop' else 'Отказ Росреестра',
                ' · '.join(filter(None, [p.get('dkuvd', ''),
                                         f"до {p['duntil']}" if p.get('duntil') else '',
                                         (p.get('dwhy') or '')[:150]])), src='councils')

# --- сортировка, дедупликация, актуальный статус
# addr/apply — вехи, не статусы: постановление об адресе (июнь) не должно перебивать
# регистрацию права (март). Статус объекта считаем по статусным событиям.
ORDER = {'apply': 0, 'addr': 1, 'cad': 2, 'mvv': 3, 'stop': 4, 'return': 5, 'deny': 6, 'right': 7}
STATUS_KINDS = ('right', 'mvv', 'cad', 'stop', 'deny', 'return')
RANK = {'right': 5, 'mvv': 4, 'cad': 3, 'stop': 2, 'deny': 2, 'return': 2}
out = {}
for uk, evs in events.items():
    # Дедупликация: одно событие часто приходит из двух источников (реестр документов и
    # registrations.json). Схлопываем по дате + виду + кадастру объекта, склеивая описания.
    def cad_of(e):
        m = re.search(r'9[46]:\d{2}:\d{6,7}:\d{1,5}', e['s'] or '')
        return m.group(0) if m else (e['lit'] or e['o'])
    merged = {}
    for e in sorted(evs, key=lambda e: (e['n'] or 99999999, ORDER.get(e['k'], 9))):
        key = (e['d'], e['k'], cad_of(e))
        if key in merged:
            prev = merged[key]
            extra = [part.strip() for part in e['s'].split(' · ')
                     if part.strip() and part.strip() not in prev['s']]
            # из второго источника берём только то, чего нет: номер записи о праве, доля и т.п.
            keep = [x for x in extra if not x.startswith(('Херсонская', 'Российская'))][:2]
            if keep:
                prev['s'] = ' · '.join(filter(None, [prev['s'], *keep]))[:300]
            if not prev['lit'] and e['lit']:
                prev['lit'] = e['lit']
            continue
        merged[key] = dict(e)
    uniq = list(merged.values())
    dated = [e for e in uniq if e['n']]
    st = [e for e in dated if e['k'] in STATUS_KINDS]
    # фактическое состояние — сильнейшее из достигнутых (право > адрес внесён > кадучёт > стоп/отказ)
    best = max(st, key=lambda e: (RANK.get(e['k'], 0), e['n'])) if st else None
    # последнее событие по времени — для хронологии и предупреждений
    last = max(dated, key=lambda e: (e['n'], ORDER.get(e['k'], 0))) if dated else None
    # отрицательное решение ПОСЛЕ достижения статуса — повод перепроверить
    warn = None
    if best and best['k'] in ('right', 'mvv'):
        later = [e for e in st if e['k'] in ('stop', 'deny', 'return') and e['n'] > best['n']]
        if later:
            w = max(later, key=lambda e: e['n'])
            warn = {'d': w['d'], 'k': w['k'], 't': w['t'], 's': w['s'][:120]}
    out[uk] = {'events': uniq,
               'status': {'d': best['d'], 'k': best['k'], 't': best['t']} if best else None,
               'last': {'d': last['d'], 'k': last['k'], 't': last['t']} if last else None,
               'warn': warn}

json.dump({'_generated': '2026-07-29', 'objects': out},
          open(os.path.join(REPO, 'events.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))

NAMES = {'right': 'право зарегистрировано', 'cad': 'только кадастровый учёт', 'mvv': 'адрес внесён',
         'stop': 'приостановка', 'deny': 'отказ', 'return': 'возврат', 'addr': 'есть адрес РФ',
         'apply': 'заявление подано'}
stat = collections.Counter(v['status']['k'] for v in out.values() if v['status'])
nostat = sum(1 for v in out.values() if not v['status'])
print(f'участков с историей: {len(out)}; событий всего: {sum(len(v["events"]) for v in out.values())}')
print('\nфактическое состояние участка (сильнейшее достигнутое):')
for k, n in stat.most_common():
    print(f'   {NAMES.get(k, k):32s} {n}')
print(f'   {"только адрес/заявление, статуса нет":32s} {nostat}')
warns = [(uk, v) for uk, v in out.items() if v.get('warn')]
print(f'\nучастков, где ПОСЛЕ права/адреса пришло отрицательное решение: {len(warns)}')
for uk, v in warns[:12]:
    print(f"   {uk} | было {NAMES.get(v['status']['k'])} {v['status']['d']} → {v['warn']['t']} {v['warn']['d']}")
