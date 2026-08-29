# -*- coding: utf-8 -*-
"""產生兩份照片對照表：Artifact 用的內嵌 base64，與自架站用的檔案路徑。"""
import base64, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
pmap = json.load(open(os.path.join(BASE, 'photomap.json')))

inline, files, missing = {}, {}, []
for item_id, ids in pmap.items():
    ins, fs = [], []
    for i in ids:
        p_in = os.path.join(BASE, 'inline', i + '.jpg')
        p_t  = os.path.join(BASE, 'photos', 't', i + '.jpg')
        p_f  = os.path.join(BASE, 'photos', 'f', i + '.jpg')
        if not (os.path.exists(p_in) and os.path.exists(p_t) and os.path.exists(p_f)):
            missing.append(i); continue
        with open(p_in, 'rb') as fh:
            ins.append('data:image/jpeg;base64,' + base64.b64encode(fh.read()).decode())
        fs.append({'t': 'photos/t/%s.jpg' % i, 'f': 'photos/f/%s.jpg' % i})
    if ins:
        inline[item_id] = ins
        files[item_id] = fs

json.dump(inline, open(os.path.join(BASE, 'photos-inline.json'), 'w'), separators=(',', ':'))
json.dump(files, open(os.path.join(BASE, 'photos-files.json'), 'w'), separators=(',', ':'))
print('商品 %d 件、照片 %d 張' % (len(inline), sum(len(v) for v in inline.values())))
print('內嵌表 %.2f MB' % (os.path.getsize(os.path.join(BASE, 'photos-inline.json')) / 1048576))
if missing:
    print('缺檔:', missing)
