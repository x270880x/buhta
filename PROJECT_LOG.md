# Бухта — кадастровая карта · ЛОГ ПРОЕКТА

**Сайт:** https://x270880x.github.io/buhta/
**Репозиторий:** x270880x/buhta (GitHub Pages, ветка main)
**Источник данных:** traidoptmarketnew/kadastr-nyzhni-sirohozy (офиц. кадастр ДЗК Украины) + Excel «кадастровые_бирючий апрель 2026»

---

## Session log — 2026-07-10 (buildings model → `blds`, v5.2)

Здания переведены со строковых полей на массив: `building` + `bcadrf` + `brr` → **`blds: [{lit, area, cad, rr}]`**
(29 участков + 3 `unbound` дома). Дома А, Б, В — отдельные элементы массива и отдельные дома в статистике.

- `buildingsBlock(data)` в index.html рисует блок «🏠 Здания (N)»: у здания с `rr` литера и кадастр зелёные (#2ecc71) + значок «🟢 РР ХО».
- `bldCads(p)` — все кадастры зданий участка одной строкой, используется поиском.
- `computeStats()`: `const houses = ps.flatMap(p => p.blds || []).concat(ub)` → всего домов **40**, с РР ХО — **7**.

Дома с подтверждённой регистрацией права: **дом 12** (уч. 0041), **49 А/Б/В** (уч. 0297), **46 А/Б/В** (`unbound`).
48 А/Б, 51 А/Б, 43 А имеют кадастры РФ, но в их выписках **нет раздела о правах** → не зелёные, лежат в `pending[]` (registrations.json).

⚠️ Грабли миграции: площади вида `"51 (стр. А 16,6 м²; Б 64,19 м²)"` нельзя резать по запятой — «16,6» превращается в «16».
Разделитель — `;`, если в строке есть `м²`.

---

## Session log — 2026-07-02 (Skrypnyk family table, v2.1)

Пользователь дал 2 скриншота-таблицы (35 строк) по семье Скрипник. Правила разбора:
привязка ТОЛЬКО по укр. кадастру + адрес из той же строки (РФ-номера игнорируем);
«Владимир» = Скрипник В.В., «Саша» = Скрипник А.В., «Саша + Яша» = «Яков + Скрипник А.В.».
- **Владельцы уточнены** по файлу (0400 Яков→В.В.+Лиля, 0415 Васильева→В.В., 0411 В.В.→А.В.+Вероника и др.)
- **Новое поле `nm`** (название объекта: «пасека левый», «Тенистый», «Озеро», «Прачка»…) — 35 участков; попап и поиск показывают/ищут его
- **Новые адреса+здания:** 0170 (Алмазная 55, Крикун), 0415 (Набережная 73, Бирюк бар), 0056 (166, Выдай), 0055 (164, Варешнюк), 0054 (165, Дудка), здание 169/3 у 0137 (Бирючий 1)
- Пасеки: пользователь подтвердил «верь файлу» → 0386=ЗУ 33 (средний), 0389=ЗУ 32 (правый) — адреса переставлены (v2.2).
- Docx «Таблица ФИАС (45 шт)(1)» лежит в корне untracked — по нему решение отложено; 40/45 позиций уже в базе, 5 без привязки (пост. 338/340/341/366/374).
- **Стартовый вид + границы (v2.3–2.5):** полоса от левого края 11:003:0002 до правого края 11:003:0059 (правый якорь сменён с 0069 на 0059 по указанию пользователя). Старт = полоса+~1 см, максимальный зум-аут (minZoom, динамический) = полоса+3 см с каждой стороны; собственный экранный ограничитель CLAMP (drag/moveend/zoomend, инерция выключена) — Leaflet maxBounds не учитывает bearing 60°, поэтому рамка держится вручную в контейнерных координатах. Всё адаптивно, пересчёт при resize.

## Session log — 2026-07-03 (выписки Росреестра ХО, зелёные флажки, поиск; v4.0–4.1)

- 0324 → Ирина Бирюкова, Утлюкская ЗУ 20 (v4.0).
- **8 выписок Росреестра по Херсонской обл.** (сканы, читал через pymupdf→PNG): право
  собственности Моршнева С.А. зарегистрировано. Новое поле **rr='да'** → **зелёный флажок**
  (вместо красного): 0041 (Набережная 12, РФ :271 + дом 126,4 м² РФ 96:01:0005579:2137 —
  ЗУ 12 наконец привязан, это 0041, не 0042!), 0119 (Набережная 14, РФ :186),
  0304 (Набережная 47, РФ :272), 0310 (Алмазная 43, РФ :36 + зд. РФ :270).
- **Здания Набережной 46 ЖДУТ привязки**: стр. А = 96:01:0005445:262 (275,6 м², адм-хоз
  корпус, 2 эт., 2016), стр. Б = :263 (139,1 м²), стр. В = :264 (52,1 м²); ЗУ 46 = РФ :254
  (из docx). Какой укр. участок = Набережная 46 — неизвестно; кандидат 0283 (Моршнев,
  0.2755 га, Улыбка Фортуны, 54 м от ЗУ 47=0304) — НЕ применять без подтверждения.
- **Поиск**: фрагменты кадастров от 3 цифр; при пустом результате авто-конверсия
  неправильной раскладки (латиница→кириллица, «vjhiytd»→«моршнев»).
- Выпадающий список поиска — 7 позиций (480px), «Последние просмотренные» отступают вниз (v4.2).
- **Флажки участков-контейнеров** (0310, 0412…): точка флажка теперь ищется внутри своего
  участка ВНЕ чужих полигонов (раньше центроид 0310 падал на вложенный 0212 → флажок «не там»).
- **`zaddr`** — старые запорожские адреса из докс-таблицы ФИАС добавлены 41 участку;
  в UI НЕ выводятся (по просьбе пользователя — хранить скрыто), в поиск не входят (v4.3).

## Session log — 2026-07-02, вечер (hover + стабильность, v3.8–3.9)

- **Hover-баг** (жалоба: при наведении на 0341 светился и окружающий 0412, «большой» не кликался):
  причина — reorderByArea на каждом mouseout перетасовывал все 524 полигона под курсором,
  браузер слал ложные mouseover контейнеру → подсветка залипала. Фикс: контейнеры при
  наведении НЕ поднимаем (только мелкие без вложенных), полную пересортировку на mouseout
  убрали, добавлен глобальный HOVERED — подсвечен максимум один участок.
- **Критично, «отравление» карты:** если контейнер карты 0×0 в момент fitStartView (фоновая
  вкладка) — minZoom становился NaN, после чего ЛЮБОЙ setView/panBy/fitBounds валил Leaflet
  («Attempted to load an infinite number of tiles», zoom=null, карта мертва до F5). Фикс:
  fitStartView ждёт ненулевой размер (retry 250мс) + isFinite-guard перед setMinZoom.
- **fitBounds с leaflet-rotate:** анимированный fitBounds молча не срабатывает (зум не
  меняется). Прыжок из поиска к участку теперь с {animate:false} — работает (зум 18).
- clampView не дёргается во время анимации зума (map._animatingZoom).

## Session log — 2026-06-10 (mobile + header hierarchy)

Сегодняшняя сессия — целиком про UI без правки данных:
- **3-строчная шапка** (Херсонская обл. / Генический р-н / **с. Бухта**) с
  иерархией: обл/р-н мелким серым, «с. Бухта» крупнее и жирным белым.
- **Мобильная версия:** компактная шапка, левый сайдбар скрыт за ☰,
  правые контролы (Схема + ЕГРН-фильтр) скрыты за ⚙. Открытый panel
  показывает backdrop-overlay, тап по нему сворачивает. Кнопки ☰/⚙
  позиционированы сразу под шапкой, зум-кнопки следуют ниже.
- **Карта:** небольшая возня с дефолтным вьюпортом — поднимал на ~3 см
  вверх, потом вернул назад с компенсацией зумом (16.2 → 16.3, +10%).

## Что это
Интерактивная кадастровая карта на Leaflet (одностраничный index.html, без бэкенда).
Покрытие: остров/коса **Бирючий**, с. Бухта, Генический район, Херсонская обл.
Кварталы: `2320355400:12:001` (Бирючий) + `2320355400:11:003`.

## Структура репо
- `index.html` — вся карта (Leaflet + leaflet-rotate, встроенный manifest советов)
- `councils/2320355400.json` — метаданные участков (владелец, площадь, массив, ЕГРН, РФ-номер…)
- `parcels/2320355400.geojson` — геометрия участков (полигоны)
- `robots.txt` — запрет индексации

## Поля участка (councils JSON)
- `c` — кадастр (укр), `a` — площадь (га), `o` — владелец, `ot` — форма собственности
- `zn` — массив/посёлок, `st` — статус (р/с/с+, сырое из Excel), `pd` — п/д (Excel)
- `cadrf` — кадастровый номер РФ, `egrn` — оформлен в ЕГРН (да)
- `ct` — целевое назначение (ВРИ), `ad` — адрес

## Цветовая легенда
- 🔵 голубой (синяя→жёлтая обводка) — оформлен в ЕГРН (РФ)
- 🩷 ярко-розовый — государственная собственность (Державна власність)
- 🟢 салатовый — остальные (частные/коммунальные)
- крупные участки (>0.2 га) — слабая заливка (вложенные просвечивают)

## Ключевой функционал
- Поворот карты (bearing 60°, коса горизонтально), старт zoom 16.3 на Бирючем
- Фильтр ЕГРН (Все / Только с ЕГРН / Без ЕГРН) — справа, пересчитывает шапку
- Поиск по кадастру/ФИО
- Попап: кадастр+копи, площадь, массив, владелец, РФ-номер+копи, ✓ЕГРН, форма собств.
- «Последние просмотренные» (слева, 10 шт, localStorage) — с РФ-номером
- Клик по наложенным участкам — открывает самый мелкий (геометрический hit-test)
- Наведение на контейнер — подсветка+подъём вложенных участков
- 3-строчная шапка: обл/р-н (мелким серым) + «с. Бухта» (крупным белым жирным)
- **Мобильная версия:** компактная шапка, бургер ☰ (левая панель) и ⚙ (схема+ЕГРН-фильтр)
  скрывают сайдбары; карта на весь экран; backdrop-overlay по тапу сворачивает панель;
  кнопки ☰/⚙ позиционированы сразу под шапкой, зум-кнопки следуют ниже

## Текущее состояние (2026-06-10)
- участков в базе: 524 (полигонов на карте: 522)
- оформлено в ЕГРН: 54 (7.26 га)
- государственных: 8
- стартовый зум: 16.3, центр на Бирючем; bearing 60° (коса горизонтально)
- индексация поисковиками: запрещена (`robots.txt` + `<meta name="robots" content="noindex">`)

### ЕГРН по владельцам
- 15 — Скрипник В.В., Скрипник А.В.
- 13 — Громов О.
- 10 — Моршнев Станислав
- 7 — Яков Кацович и ко.
- 3 — Громов Леонід Іванович
- 2 — (нет)
- 1 — Крикунов А.С.
- 1 — Александр Нагорный
- 1 — Громов Олег Леонідович
- 1 — Громова Валентина Миколаївна

## Полная история коммитов (новые сверху)
- 2026-06-10 12:42 — map: remove 3cm up-pan (back down) + zoom 16.2→16.3 (+10%)
- 2026-06-10 12:31 — map: pan view ~3cm up on every load (content higher, more sea below)
- 2026-06-10 12:21 — mobile: move ☰/⚙ buttons right under header (top 46→15px), zoom follows
- 2026-06-10 12:18 — header: hierarchy — обл/р-н smaller & grey, с. Бухта larger (+20%) bold white
- 2026-06-10 12:08 — mobile: hide toggle button when its panel is open; add backdrop overlay (tap to collapse)
- 2026-06-10 12:04 — mobile: -30% header text, compact header (raises map), move ☰/⚙ closer under header
- 2026-06-10 11:59 — mobile: collapse right controls (схема+ЕГРН) behind ⚙ button; move zoom below burger
- 2026-06-10 11:54 — ui: 3-line header (обл/р-н/село) + mobile version (burger panel, compact header, full-screen map)
- 2026-06-09 22:29 — owner: fix 'Алекасндр и Ирина Нагорные' → 'Александр Нагорный'
- 2026-06-09 22:27 — docs: add PROJECT_LOG.md — full project overview, data schema, color legend, EGRN breakdown, commit history
- 2026-06-09 22:22 — 12:001:0080 (З.Берег): ЕГРН 96:01:0005445:31 + owner → Крикунов А.С.
- 2026-06-09 21:16 — recent-viewed: show РФ cadnum (blue) when present
- 2026-06-09 21:02 — hover container: lift + white-outline all nested parcels (visible & clickable on top)
- 2026-06-09 20:52 — style: uniform blue fill for ALL ЕГРН parcels (0.42) regardless of size
- 2026-06-09 20:42 — click: open smallest parcel under point (geometric hit-test) — fixes overlapping/nested parcels not clickable
- 2026-06-09 20:31 — style: large container parcels get faint fill so nested parcels show through
- 2026-06-09 20:26 — owner: revert 0238 back to Яков Кацович и ко. (keep ЕГРН)
- 2026-06-09 20:23 — owner: 16 parcels → Скрипник В.В., Скрипник А.В. (+confirm ЕГРН)
- 2026-06-09 19:51 — fix: restore z-order on mouseout — hovering a container no longer covers nested parcels
- 2026-06-09 19:45 — ЕГРН batch: 16 Скрипники/Яков parcels (280-298, 43, 44)
- 2026-06-09 19:43 — fix: z-order parcels by area (big below, small above) so nested parcels are clickable
- 2026-06-09 16:17 — seo: title/description → 'Бухта — кадастровая карта'
- 2026-06-09 16:15 — seo: title/description → 'Кадастровая карта. БУХТА'; block indexing (robots.txt + meta)
- 2026-06-09 15:59 — ЕГРН batch: 20 Громов parcels
- 2026-06-09 14:40 — style: government parcels brighter pink (#ff4d94, opacity 0.45)
- 2026-06-09 14:19 — style: yellow outlines everywhere (ЕГРН keeps blue fill but yellow border too)
- 2026-06-09 14:17 — 0412: add ЕГРН + РФ cadnum 96:01:0005445:43
- 2026-06-09 14:16 — fix: remove 8 inner-ring artifacts from 0412 (clean highlight); copy ✓ as matched-size SVG
- 2026-06-09 13:29 — copy button: black bg, yellow border, yellow icon outline
- 2026-06-09 13:27 — copy: stopPropagation so popup stays open; green ✓ feedback on copy
- 2026-06-09 13:25 — ЕГРН batch: 10 parcels (0296-0304, 0119, 0299-0302, 0310)
- 2026-06-09 13:14 — egrn filter: update header count + area to match filtered set (with declension)
- 2026-06-09 13:09 — recent-viewed: show full info (area/массив/владелец/✓ЕГРН), increase 5→10
- 2026-06-09 13:06 — 11:003:0069 (Гольфстрим): add ЕГРН + РФ 96:01:0005445:5
- 2026-06-09 13:03 — ЕГРН: 0250→...:25, 0399→...:275
- 2026-06-09 13:02 — 0137: add ЕГРН + РФ cadnum 96:01:0005445:232
- 2026-06-09 13:01 — 0325: add ЕГРН + РФ cadnum 96:01:0005445:274
- 2026-06-09 12:59 — 0130: add ЕГРН + РФ cadnum 96:01:0005445:42
- 2026-06-09 12:57 — 0289: add ЕГРН + РФ cadnum 96:01:0005445:29
- 2026-06-09 12:56 — copy button: classic copy icon (square-in-square SVG) on bright accent bg
- 2026-06-09 12:50 — parcels: thinner outlines for all (yellow 1.1→0.6, blue ЕГРН 1.3→0.8)
- 2026-06-09 12:47 — parcels: halve outline width (yellow 2.2→1.1, blue ЕГРН 2.6→1.3)
- 2026-06-09 12:35 — egrn control: thinner buttons, same 158px width as layers control
- 2026-06-09 12:20 — style: ЕГРН parcels → blue outline + light-blue fill; gov → pink; remove temp green filter highlight
- 2026-06-09 10:27 — egrn filter: move to topright control near layers; green highlight for ЕГРН parcels; rename OSM→Схема
- 2026-06-09 10:18 — popup: 'кадастровый номер РФ' → 'кадастровый РФ'
- 2026-06-09 10:17 — fix: ЕГРН filter was hidden by minimal-UI CSS rule — exclude it via :has
- 2026-06-09 10:13 — popup: add copy buttons next to UA cadnum and РФ cadnum
- 2026-06-09 10:10 — owner: 12:001:0404 Киров → Чернышук Андрей
- 2026-06-09 10:07 — feature: ЕГРН filter (Все / Только с ЕГРН / Без ЕГРН) in left panel
- 2026-06-09 10:01 — 0399: add РФ cadnum 96:01:0005445:275 + ЕГРН
- 2026-06-09 09:58 — owner: 'Яков Кацович и компаньоны (...)' → 'Яков Кацович и ко.' (all)
- 2026-06-09 09:50 — popup: remove статус row (р/с/с+); keep raw st in data
- 2026-06-09 09:47 — popup: add 'кадастровый номер РФ' and 'оформлен ЕГРН' rows (shown when filled)
- 2026-06-09 09:32 — owner: 12:001:0402 Киров → Чернышук Андрей
- 2026-06-09 09:31 — owner: set 0054/0055/0056 → Скрипник В.В.
- 2026-06-09 09:21 — data: merge April-2026 Excel info; restore 45 parcels with owner data
- 2026-06-09 08:57 — Revert "parcels: shift all 477 features +5m NNE (right)"
- 2026-06-09 08:53 — parcels: shift all 477 features +5m NNE (right)
- 2026-06-09 08:51 — parcels: shift all 477 features 5m NNE (right at bearing 60)
- 2026-06-09 08:48 — parcels: convert last MultiPolygon→Polygon; hover bringToFront so full outline highlights
- 2026-06-09 08:45 — parcels: restore original coordinates from source (undo all shifts)
- 2026-06-09 08:38 — parcels: shift all 477 features 100m NNE (right at bearing 60)
- 2026-06-09 02:05 — parcels: shift all 477 features 80m SSW (left at bearing 60)
- 2026-06-09 01:58 — parcel 11:003:0267: remove 7 inner-ring artifacts, keep solid outline
- 2026-06-09 01:53 — parcels: shift all 477 features 80m SSW (left at bearing 60)
- 2026-06-09 01:52 — remove 25 more artifacts (<100m²) → 477 parcels
- 2026-06-09 01:51 — parcels: shift all 502 features 40m NNE (right at bearing 60)
- 2026-06-09 01:48 — ui: narrow left panel by 1cm (280→242px, media 220→182px)
- 2026-06-09 01:46 — parcels: shift all 502 features 40m NNE (right at bearing 60)
- 2026-06-09 01:45 — remove 29 tiny artifacts (<50m²); move recent-viewed block to bottom of left panel
- 2026-06-09 01:41 — ui: recent-viewed panel (last 5, localStorage) + zoom 16.3 → 16.2 (-5%)
- 2026-06-09 01:38 — ui: remove '/компания' from search label; decline 'участок' by count
- 2026-06-09 01:36 — header: stats inline (number + label same line) + size +20%
- 2026-06-09 01:34 — parcels: shift all 531 features 20m SSW (screen-left at bearing 60)
- 2026-06-09 01:32 — map: zoom 16.2 → 16.3 (+10%)
- 2026-06-09 01:30 — parcels: shift all 531 features 10m NNE (screen-right at bearing 60)
- 2026-06-09 01:28 — map: zoom 16.1 → 16.2 (+10%)
- 2026-06-09 01:27 — search: remove placeholder example
- 2026-06-09 01:25 — header: stats text +15% (values 12→14px, labels 10→12px)
- 2026-06-09 01:24 — popup: text -20% (area 17→14px, ownership 15→12px)
- 2026-06-09 01:23 — style: Державна власність → light pink (#ffc4d6); blue override for :11:003:0002 kept
- 2026-06-09 01:21 — parcels: shift all 531 features 5m SSW (screen-left at bearing 60)
- 2026-06-09 01:16 — map: shift 100m NW (pan up) + fillOpacity 0.35 → 0.18 (very transparent fill)
- 2026-06-09 01:14 — parcels: bright thick yellow borders + transparent fill (map visible through)
- 2026-06-09 01:11 — map: shift another 120m SSW to (46.2261, 35.2394)
- 2026-06-09 01:08 — map: shift SSW 150m to (46.2270, 35.2402)
- 2026-06-09 01:03 — map: zoom 15.8 → 16.1 (+20%) + shift SSW 100m
- 2026-06-09 01:01 — map: zoom 15.7 → 15.8 (+10%)
- 2026-06-09 00:59 — map: shift back 200m SSW (left) to (46.2290, 35.2418)
- 2026-06-09 00:54 — map: shift NNE 200m + zoom 15.6 → 15.7 (+10%)
- 2026-06-09 00:53 — map: zoom 15.5 → 15.6 (+10%) + zoomSnap 0.1 for fine control
- 2026-06-09 00:50 — map: zoom 17 → 15.5 (-1.5) + enable fractional zoomSnap 0.5
- 2026-06-09 00:47 — map: zoom 16 → 17 (2x closer) + back-step ~75m NNE
- 2026-06-09 00:46 — map: step back ~75m NNE (~5cm)
- 2026-06-09 00:45 — map: pan another ~225m SSW (~15cm)
- 2026-06-09 00:43 — map: pan another 30m SSW
- 2026-06-09 00:41 — map: pan another ~75m SSW
- 2026-06-09 00:39 — map: pan opposite direction (SSW) — center to (46.231, 35.2435)
- 2026-06-09 00:34 — map: shift center another ~75m NNE (right by ~5cm)
- 2026-06-09 00:32 — map: shift center NNE ~150m (pan view right by ~10cm at typical screen)
- 2026-06-09 00:28 — map: default zoom 14 → 16 (~4x closer)
- 2026-06-09 00:26 — map: bearing 60 (peninsula horizontal at this zoom/center) + explicit setBearing fallback
- 2026-06-09 00:12 — map: default view zoom 14 at (46.232, 35.245) — matches user's preferred framing
- 2026-06-08 23:47 — polygons: solid fill + layer-wide CSS opacity → uniform shade across overlaps
- 2026-06-08 23:45 — popup: area 11→17px (bold), ownership 10→15px
- 2026-06-08 23:41 — popup: keep only area in subtitle; translate ownership to RU; remove basket button
- 2026-06-08 23:37 — remove giant national park parcel 12:001:0452; reduce fillOpacity to 0.22
- 2026-06-08 23:34 — style: only 11:003:0002 light blue, all others light salad green
- 2026-06-08 23:31 — ui: hide yellow council marker circle
- 2026-06-08 23:30 — marker: remove count number; header: show real participation/area totals
- 2026-06-08 23:27 — style: all parcels green except Державна власність (blue)
- 2026-06-08 23:21 — fix: STATS/FILTERS fallbacks — autoload was blocked by undefined STATS in renderSidebar
- 2026-06-08 23:15 — polygons: always visible — thicker accent border, toggle disabled
- 2026-06-08 23:10 — add 137 parcels from квартал 11:003 (total 532, 9796 га)
- 2026-06-08 23:07 — map: recenter on Бирючий 12:001 polygons centroid (46.2513, 35.2517)
- 2026-06-08 23:03 — manifest: add Бирючий 12:001 (395 parcels, 9734.8 га) + auto-load on start
- 2026-06-08 23:02 — import 395 parcels of квартал 12:001 (Бирючий) from source
- 2026-06-08 22:50 — header: hide 'сельсоветов' stat
- 2026-06-08 22:49 — map: bearing 95° (compensate spit tilt) + shift up to expose sea below
- 2026-06-08 22:36 — ui: minimal sidebar — title 'Бухта' + only cadastr search
- 2026-06-08 22:34 — map: add leaflet-rotate plugin, bearing 90° (peninsula horizontal)
- 2026-06-08 22:30 — ui: remove right sidebar — map fills full width
- 2026-06-08 22:26 — map: recenter to Бирючий микрорайон (46.235, 35.246)
- 2026-06-08 22:17 — map: recenter to Бирючий peninsula middle (46.175, 35.210)
- 2026-06-08 22:14 — map: zoom 14 → 15 (2x closer)
- 2026-06-08 22:12 — map: zoom 13 → 14 (2x closer)
- 2026-06-08 22:09 — wipe all data — keep bare map
- 2026-06-08 22:04 — map: start zoomed to Бирючий + auto-load Кирилівка parcels
- 2026-06-08 21:53 — import 495 parcels from 008 KML (Бирючий / Кирилівка + Генічеськ)
- 2026-05-16 20:37 — detail panel: cadnum click navigates to parcel on map (not kadastr.live)