# -*- coding: utf-8 -*-
"""建立「商品 id → 照片檔案 id 清單」。
以後台的 Drive 連結為準；後台沒填連結的，再用品名去比對母資料夾裡未被認領的項目。"""
import json, html, os, re, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = '1vdIQlWOaWGTyM2M1WwWyyHIpYoAiBikS'
src = json.load(open(os.path.join(BASE, 'data.json'), encoding='utf-8'))

FILE_RE = re.compile(r'/file/d/([A-Za-z0-9_-]{20,})')
FOLDER_RE = re.compile(r'/folders/([A-Za-z0-9_-]{20,})')
ENTRY_RE = re.compile(
    r'id="entry-([A-Za-z0-9_-]+)".*?class="flip-entry-(icon|thumb)".*?flip-entry-title">([^<]*)<',
    re.S)

_cache = {}
def listing(fid):
    """回傳資料夾內容 [(id, 'folder'|'file', 名稱)]，依 Drive 顯示順序。"""
    if fid in _cache:
        return _cache[fid]
    page = subprocess.run(
        ['curl', '-sL', '--max-time', '60',
         'https://drive.google.com/embeddedfolderview?id=' + fid + '#list'],
        capture_output=True, text=True).stdout
    out = [(i, 'folder' if kind == 'icon' else 'file', html.unescape(name))
           for i, kind, name in ENTRY_RE.findall(page)]
    _cache[fid] = out
    return out

# 品名與 Drive 資料夾名稱兜不起來的，直接指定（資料夾名 → 商品 id）
MANUAL = {'單人床組': 1, '黑色抽屜櫃': 11, '無印紙板層櫃': 12}

COVER_MARK = ('封面', 'cover')

def cover_first(files, want):
    """把要當列表預覽圖的那張排到第一個。files 是 [(id, 名稱)]。"""
    def score(name):
        low = name.lower()
        if want and want.lower() in low:      # 後台「列表預覽圖」欄位指定的檔名優先
            return 0
        if name.startswith('*'):
            return 1
        if any(k in low for k in COVER_MARK):
            return 1
        return 2
    return [f[0] for f in sorted(files, key=lambda f: score(f[1]))]


def norm(s):
    """比對品名用：去掉空白與各種標點，方便『Karimoku 雜誌架』對上『Karimoku雜誌架』。"""
    return re.sub(r'[\s　（）()×x✕・，,。.\-—/]', '', s).lower()

root = listing(ROOT)
claimed = set()
mapping, notes = {}, []

# 第一輪：後台已經填了 Drive 連結的，直接採用
for it in src['items']:
    url = (it.get('url') or '').strip()
    if not url:
        continue
    m = FILE_RE.search(url)
    if m:
        mapping[str(it['id'])] = [m.group(1)]
        claimed.add(m.group(1))
        continue
    m = FOLDER_RE.search(url)
    if not m:
        notes.append('#%d %s：連結格式看不懂 %s' % (it['id'], it['n'], url)); continue
    fid = m.group(1)
    claimed.add(fid)
    ids = cover_first([(e[0], e[2]) for e in listing(fid) if e[1] == 'file'],
                      (it.get('cover') or '').strip())
    if ids:
        mapping[str(it['id'])] = ids
        if len(ids) != it.get('ph'):
            notes.append('#%d %s：後台記 %d 張，實際 %d 張'
                         % (it['id'], it['n'], it.get('ph', 0), len(ids)))
    else:
        notes.append('#%d %s：資料夾是空的' % (it['id'], it['n']))

leftover = [e for e in root if e[0] not in claimed]

# 第二輪：照片被搬進同名資料夾，但後台連結還指著原本那張單檔 —— 自動改用整個資料夾
for it in src['items']:
    key = str(it['id'])
    cur = mapping.get(key)
    if not cur:
        continue
    target = norm(it['n'])
    for e in list(leftover):
        if e[1] != 'folder' or norm(e[2]) != target:
            continue
        kids = [(x[0], x[2]) for x in listing(e[0]) if x[1] == 'file']
        if not set(cur).issubset({k[0] for k in kids}):
            continue          # 資料夾裡沒有現在這張，不能確定是同一件，不動它
        leftover.remove(e)
        mapping[key] = cover_first(kids, (it.get('cover') or '').strip())
        notes.append('#%d %s：照片已搬進「%s」資料夾，改用整個資料夾共 %d 張'
                     % (it['id'], it['n'], e[2], len(kids)))
        break

# 第三輪：後台沒填連結的商品，用品名比對母資料夾裡沒被認領的項目
for it in src['items']:
    if str(it['id']) in mapping:
        continue
    target = norm(it['n'])
    hit = None
    for e in leftover:
        n = norm(e[2].rsplit('.', 1)[0])
        if n == target or target in n or n in target:
            hit = e; break
    if not hit:
        continue
    leftover.remove(hit)
    ids = ([hit[0]] if hit[1] == 'file'
           else cover_first([(x[0], x[2]) for x in listing(hit[0]) if x[1] == 'file'],
                            (it.get('cover') or '').strip()))
    if ids:
        mapping[str(it['id'])] = ids
        notes.append('#%d %s：後台沒連結，用品名對上「%s」共 %d 張'
                     % (it['id'], it['n'], hit[2], len(ids)))

# 第四輪：手動指定
for e in list(leftover):
    tid = MANUAL.get(e[2].rsplit('.', 1)[0])
    if tid is None:
        continue
    leftover.remove(e)
    ids = [e[0]] if e[1] == 'file' else [x[0] for x in listing(e[0]) if x[1] == 'file']
    if not ids:
        continue
    mapping.setdefault(str(tid), []).extend(ids)
    notes.append('#%d：手動指定「%s」共 %d 張' % (tid, e[2], len(ids)))

json.dump(mapping, open(os.path.join(BASE, 'photomap.json'), 'w'), indent=1)
print('對應到 %d 件商品、共 %d 張照片'
      % (len(mapping), sum(len(v) for v in mapping.values())))
print('母資料夾仍未認領：%d 項 %s'
      % (len(leftover), [e[2] for e in leftover]))
print('\n--- 記錄 ---')
for n in notes:
    print(' ' + n)
