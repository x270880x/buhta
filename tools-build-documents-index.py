#!/usr/bin/env python3
"""Строит ДОКУМЕНТЫ-ИНДЕКС.md и documents-index.csv: файл на диске → объект → запись реестра."""
import json, re, os, csv, collections

REPO = os.path.expanduser('~/Documents/Проекты/Buhta-кадастровая карта')
OCR = '/private/tmp/claude-501/-Users-splitcam-Documents---------SplitCam-SplitCam-Android/00f91029-3fed-45ac-8a27-a8efeed3296b/scratchpad/ocr/index.json'
ARCHIVE = os.path.expanduser('~/Documents/Земля и недвижимость/Бухта (Бирючий)')

docs = json.load(open(OCR))
html = open(os.path.join(REPO, 'rosreestr_registry.html'), encoding='utf-8').read()
recs = json.loads(re.search(r'const records = (\[.*?\]);', html, re.S).group(1))
council = json.load(open(os.path.join(REPO, 'councils/2320355400.json'), encoding='utf-8'))

# --- индексы базы карты
base = {}
for p in council['parcels']:
    if p.get('cadrf'):
        base[p['cadrf']] = ('участок', p['c'], p.get('fias', ''), p.get('o', ''))
    for b in (p.get('blds') or []):
        if b.get('cad'):
            base[b['cad']] = ('здание', p['c'], p.get('fias', ''), p.get('o', ''))

def norm_kuvd(x):
    return re.sub(r'/\d+$', '', (x or '').strip())

reg_by_cad = collections.defaultdict(list)
reg_by_kuvd = collections.defaultdict(list)
for x in recs:
    if x.get('cad_rf'):
        reg_by_cad[x['cad_rf']].append(x)
    if x.get('kuvd'):
        reg_by_kuvd[norm_kuvd(x['kuvd'])].append(x)

# --- имя файла архива часто содержит кадастр: 96-01-0005445-299
def cad_from_name(name):
    m = re.search(r'\b(9[46])-(\d{2})-(\d{6,7})-(\d{1,5})\b', name)
    return f'{m.group(1)}:{m.group(2)}:{m.group(3)}:{m.group(4)}' if m else ''

rows = []
for d in docs:
    if d.get('error'):
        rows.append({'файл': d.get('file', ''), 'папка': d.get('loc', ''), 'проблема': d['error']})
        continue
    cad = d.get('cad_rf') or cad_from_name(d.get('file', ''))
    name_cad = cad_from_name(d.get('file', ''))
    if name_cad and name_cad in (d.get('cad_all') or []):
        cad = name_cad
    kuvd = norm_kuvd(d.get('kuvd'))
    linked = reg_by_cad.get(cad, []) or reg_by_kuvd.get(kuvd, [])
    b = base.get(cad)
    rows.append({
        'файл': d.get('file', ''),
        'папка': d.get('loc', ''),
        'кадастр_рф': cad,
        'кадастр_укр': (b[1] if b else d.get('cad_uk', '')),
        'тип_объекта': d.get('obj_type', '') or (b[0] if b else ''),
        'адрес': d.get('address', '') or (b[2] if b else ''),
        'владелец': (b[3] if b else d.get('owner', '')),
        'кувд': kuvd,
        'вид_документа': d.get('doc_kind', ''),
        'право': d.get('right', ''),
        'номер_записи': d.get('reg_num', ''),
        'дата_составления': d.get('compiled', ''),
        'в_реестре': 'да' if linked else 'нет',
        'статус_в_реестре': '; '.join(sorted({x.get('status', '') for x in linked})) if linked else '',
        'на_карте': 'да' if b else 'нет',
        'размер_мб': round(d.get('size', 0) / 1e6, 2),
        'путь': os.path.relpath(d.get('path', ''), os.path.expanduser('~')),
    })

rows.sort(key=lambda r: (r.get('кадастр_рф', ''), r.get('файл', '')))

csv_path = os.path.join(REPO, 'documents-index.csv')
cols = ['кадастр_рф', 'кадастр_укр', 'тип_объекта', 'адрес', 'владелец', 'кувд', 'вид_документа',
        'право', 'номер_записи', 'статус_в_реестре', 'в_реестре', 'на_карте', 'дата_составления',
        'файл', 'папка', 'путь', 'размер_мб', 'проблема']
with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore')
    w.writeheader()
    w.writerows(rows)

# --- сводка
have_cad = [r for r in rows if r.get('кадастр_рф')]
no_cad = [r for r in rows if not r.get('кадастр_рф')]
not_in_reg = [r for r in rows if r.get('кадастр_рф') and r.get('в_реестре') == 'нет']
not_on_map = [r for r in rows if r.get('кадастр_рф') and r.get('на_карте') == 'нет']
bycad = collections.defaultdict(list)
for r in have_cad:
    bycad[r['кадастр_рф']].append(r)

md = [
    '# Документы Бухты — индекс для поиска',
    '',
    f'Сгенерирован 29.07.2026 автоматически (OCR по архиву). Файлов: **{len(rows)}**, '
    f'из них с распознанным кадастром — {len(have_cad)}, уникальных объектов — {len(bycad)}.',
    '',
    '**Где лежат документы:** `~/Documents/Земля и недвижимость/Бухта (Бирючий)/`. '
    'В репозитории (`sources/`) — только 9 ранних выписок. Копии в `~/Downloads` и '
    '`~/Desktop/Выписки Росреестр - с.Бухта` — дубли (сверено по md5).',
    '',
    'Машиночитаемая версия со всеми полями — `documents-index.csv` рядом.',
    '',
    '## Как искать',
    '',
    '- по кадастру РФ — таблица ниже отсортирована по нему;',
    '- по адресу или владельцу — поиском по этой странице;',
    '- по номеру КУВД — в `documents-index.csv`, колонка `кувд`.',
    '',
    '## Проблемные места',
    '',
    f'- файлов без распознанного кадастра: **{len(no_cad)}** (декларации, витяги ДРРП, часть уведомлений);',
    f'- документов, которых нет в `rosreestr_registry.html`: **{len(not_in_reg)}**;',
    f'- кадастров, которых нет в базе карты `councils/`: **{len(not_on_map)}**.',
    '',
    '## Объекты',
    '',
    '| Кадастр РФ | Тип | Адрес | Владелец (карта) | Документов | Статус по реестру |',
    '|---|---|---|---|---:|---|',
]
for cad in sorted(bycad):
    rs = bycad[cad]
    r0 = max(rs, key=lambda r: len(r.get('адрес', '')))
    statuses = sorted({s for r in rs if r.get('статус_в_реестре') for s in r['статус_в_реестре'].split('; ')})
    addr = (r0.get('адрес', '') or '')[:70]
    md.append(f"| `{cad}` | {r0.get('тип_объекта','')} | {addr} | {r0.get('владелец','')} | {len(rs)} | {', '.join(statuses)} |")

md += ['', '## Файлы без кадастра', '', '| Файл | Папка |', '|---|---|']
for r in sorted(no_cad, key=lambda r: r.get('папка', '')):
    md.append(f"| {r.get('файл','')} | {r.get('папка','')} |")

open(os.path.join(REPO, 'ДОКУМЕНТЫ-ИНДЕКС.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print(f'файлов: {len(rows)}, с кадастром: {len(have_cad)}, объектов: {len(bycad)}')
print(f'нет в реестре: {len(not_in_reg)}, нет на карте: {len(not_on_map)}, без кадастра: {len(no_cad)}')
