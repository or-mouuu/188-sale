# -*- coding: utf-8 -*-
"""把商品資料與照片注入 shop.html 樣板。

用法：
    python3 build.py photos-inline.json index.html      # Artifact 用：照片內嵌 base64
    python3 build.py photos-files.json  site/index.html # 自架站用：照片是獨立檔案
    python3 build.py -                  index.html      # 不放照片
照片對照表的值是 <img src> 會直接用的字串，所以兩種模式共用同一份樣板。
"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
photos_arg = sys.argv[1] if len(sys.argv) > 1 else '-'
dest = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, 'index.html')
if not os.path.isabs(dest):
    dest = os.path.join(BASE, dest)

tpl = open(os.path.join(BASE, 'shop.html'), encoding='utf-8').read()
data = open(os.path.join(BASE, 'items.json'), encoding='utf-8').read()
if photos_arg == '-':
    photos = '{}'
else:
    path = photos_arg if os.path.isabs(photos_arg) else os.path.join(BASE, photos_arg)
    photos = open(path, encoding='utf-8').read()

# JSON 放進 <script type="application/json"> 只需要防止標籤被提前關閉
def safe(s):
    return s.replace('</', '<\\/')

out = tpl.replace('__DATA__', safe(data)).replace('__PHOTOS__', safe(photos))
os.makedirs(os.path.dirname(dest), exist_ok=True)
open(dest, 'w', encoding='utf-8').write(out)

pmap = json.loads(photos)
size = len(out.encode('utf-8')) / 1048576
print('已產生 %s' % dest)
print('  頁面大小 %.2f MB' % size)
print('  商品 %d 件，其中 %d 件有照片，共 %d 張'
      % (len(json.loads(data)['items']), len(pmap), sum(len(v) for v in pmap.values())))
if size > 15:
    print('  ⚠️ 超過 Artifact 的 16MB 上限，需要再壓')
