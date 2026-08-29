# -*- coding: utf-8 -*-
"""產生兩份照片對照表：Artifact 用的內嵌 base64，與自架站用的檔案路徑。"""
import base64, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
pmap = json.load(open(os.path.join(BASE, 'photomap.json')))

ROOT = os.path.dirname(BASE)
inline, files, missing = {}, {}, []
for item_id, ids in pmap.items():
    ins, fs = [], []
    for i in ids:
        p_in = os.path.join(ROOT, 'inline', i + '.jpg')
        p_t  = os.path.join(ROOT, 'photos', 't', i + '.jpg')
        p_f  = os.path.join(ROOT, 'photos', 'f', i + '.jpg')
        if not (os.path.exists(p_t) and os.path.exists(p_f)):
            missing.append(i); continue
        # inline 只有本機建 Claude artifact 時才需要，CI 上沒有就跳過
        if os.path.exists(p_in):
            with open(p_in, 'rb') as fh:
                ins.append('data:image/jpeg;base64,' + base64.b64encode(fh.read()).decode())
        fs.append({'t': 'photos/t/%s.jpg' % i, 'f': 'photos/f/%s.jpg' % i})
    if fs:
        files[item_id] = fs
        if ins:
            inline[item_id] = ins

json.dump(files, open(os.path.join(BASE, 'photos-files.json'), 'w'), separators=(',', ':'))
print('商品 %d 件、照片 %d 張' % (len(files), sum(len(v) for v in files.values())))
if inline:
    json.dump(inline, open(os.path.join(BASE, 'photos-inline.json'), 'w'), separators=(',', ':'))
    print('內嵌表 %.2f MB' % (os.path.getsize(os.path.join(BASE, 'photos-inline.json')) / 1048576))
if missing:
    print('缺檔:', missing)
