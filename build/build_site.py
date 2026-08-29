# -*- coding: utf-8 -*-
"""從 data/data.json 重建整個前台網站。

    python3 build/build_site.py

依序做四件事：把後台資料轉成前台資料、比對 Drive 照片、同步缺少的照片、
產生 index.html。GitHub Actions 和本機跑的是同一支。
"""
import os, subprocess, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)


def step(title, args):
    print('\n── %s ' % title + '─' * max(0, 46 - len(title)))
    r = subprocess.run([sys.executable] + args, cwd=BASE)
    if r.returncode != 0:
        sys.exit('「%s」失敗，建置中止。' % title)


step('後台資料 → 前台資料', ['prep.py',
                             os.path.join(ROOT, 'data', 'data.json'),
                             os.path.join(BASE, 'items.json')])
step('比對 Drive 照片', ['map_photos.py'])
step('同步照片檔', ['photos_sync.py'])
step('產生照片對照表', ['photos_json.py'])
step('產生 index.html', ['build.py', 'photos-files.json',
                          os.path.join(ROOT, 'index.html')])
print('\n完成。')
