# -*- coding: utf-8 -*-
"""把後台盤點資料轉成前台商品資料：拆價格、抽商品網址、濾掉內部註記。"""
import json, re, sys

SRC = sys.argv[1]; OUT = sys.argv[2]

# note 裡屬於「給自己看的盤點指示」，不可對買家顯示
INTERNAL = ['清單未列', '請補', '⚠️', '清單列於', '建議', '需確認', '照片有',
            '僅 1 張', '單價最高', '可補上', '照片與拆機', '此處卻', '外觀相近', '清單寫', '資料夾']
URL_RE = re.compile(r'https?://\S+')
MONEY_RE = re.compile(r'^\s*([\d,]+)\s*(?:（(.*)）)?\s*$')
BUY_RE = re.compile(r'^\s*([\d,]+)\s*(?:（([^）]*)）)?\s*$')

def money(raw):
    """回傳 (數字或 None, 附註或 None)。"""
    raw = (raw or '').strip()
    if not raw:
        return None, None
    m = MONEY_RE.match(raw)
    if m:
        return int(m.group(1).replace(',', '')), (m.group(2) or None)
    # 純附註，例如「（含於床組合售）」
    return None, raw.strip('（）()')

def clean_note(raw):
    """逐行、逐句丟掉內部註記，回傳 (對外備註, 商品網址list)。換行保留。"""
    raw = (raw or '').strip()
    if not raw:
        return '', []
    urls = URL_RE.findall(raw)
    text = URL_RE.sub('', raw)
    lines = []
    for line in text.split('\n'):
        parts = [p.strip(' 　;；,') for p in re.split(r'[；　]', line)]
        keep = [p for p in parts if p and not any(k in p for k in INTERNAL)]
        if keep:
            lines.append('；'.join(keep))
    return '\n'.join(lines), urls

src = json.load(open(SRC, encoding='utf-8'))
out = []
sold = 0
for it in src['items']:
    if it.get('sold'):          # 後台標成已售出的，前台不顯示
        sold += 1
        continue
    price, price_note = money(it.get('sell'))
    orig, orig_when = money(it.get('buy'))
    note, urls = clean_note(it.get('note'))
    # 後台之後新增的商品網址欄位（link / l）優先，其次才是從 note 撈到的
    link = (it.get('link') or it.get('l') or (urls[0] if urls else '')).strip()
    out.append({
        'id': it['id'],
        'cat': it['c'],
        'name': it['n'],
        'model': (it.get('m') or '').strip(),
        'size': '' if (it.get('s') or '').strip() in ('', '無') else it['s'].strip(),
        'price': price,
        'priceNote': price_note or '',
        'orig': orig if orig else None,
        'origWhen': orig_when or '',
        'when': (it.get('when') or '').strip(),
        'note': note,
        'link': link,
        'nPhoto': it.get('ph', 0),
    })

json.dump({'cats': src['cats'], 'updated': src['updated'], 'items': out},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- 驗收輸出 ---
print('件數:', len(out), '（已售出未上架:', sold, '件）')
print('有售價:', sum(1 for i in out if i['price'] is not None),
      '| 免費:', sum(1 for i in out if i['price'] == 0),
      '| 未定價:', sum(1 for i in out if i['price'] is None))
print('有商品網址:', sum(1 for i in out if i['link']))
print('\n--- 保留下來的對外備註 ---')
for i in out:
    if i['note']:
        print(' ', i['name'], '::', i['note'])
print('\n--- 價格附註 ---')
for i in out:
    if i['priceNote']:
        print(' ', i['name'], ':: price=', i['price'], '| note=', i['priceNote'])
