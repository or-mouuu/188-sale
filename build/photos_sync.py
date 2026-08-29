# -*- coding: utf-8 -*-
"""依 photomap.json 把 Drive 照片同步成網站要用的兩種尺寸。

只處理「還沒有的」照片，並刪掉 Drive 已移除的孤兒檔，所以每次跑都很快。
macOS 與 GitHub Actions 共用這一支（不依賴 sips）。

    python3 photos_sync.py            # 同步 photos/t 與 photos/f
    python3 photos_sync.py --inline   # 另外產生 inline/（給 Claude artifact 內嵌用）
"""
import io, json, os, sys, urllib.request

from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
DL = 'https://drive.google.com/uc?export=download&id='

# (資料夾, 最長邊, JPEG 品質)
SIZES = [('photos/t', 560, 48), ('photos/f', 1600, 72)]
INLINE = ('inline', 760, 45)


def wanted_ids():
    pmap = json.load(open(os.path.join(BASE, 'photomap.json')))
    seen, out = set(), []
    for ids in pmap.values():
        for i in ids:
            if i not in seen:
                seen.add(i)
                out.append(i)
    return out


def fetch(file_id):
    req = urllib.request.Request(DL + file_id, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def write_sizes(raw, file_id, targets):
    im = Image.open(io.BytesIO(raw))
    im = im.convert('RGB')
    for folder, longest, quality in targets:
        out = os.path.join(ROOT, folder, file_id + '.jpg')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        c = im.copy()
        c.thumbnail((longest, longest), Image.LANCZOS)
        c.save(out, 'JPEG', quality=quality, optimize=True, progressive=True)


def main():
    sizes = SIZES + ([INLINE] if '--inline' in sys.argv else [])
    ids = wanted_ids()
    keep = set(ids)

    added = failed = 0
    for file_id in ids:
        missing = [s for s in sizes
                   if not os.path.exists(os.path.join(ROOT, s[0], file_id + '.jpg'))]
        if not missing:
            continue
        try:
            write_sizes(fetch(file_id), file_id, missing)
            added += 1
            print('  + %s（%s）' % (file_id, '、'.join(s[0] for s in missing)))
        except Exception as e:                      # 單張失敗不該讓整個建置停擺
            failed += 1
            print('  ! %s 取得失敗：%s' % (file_id, e))

    removed = 0
    for folder, _, _ in sizes:
        d = os.path.join(ROOT, folder)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith('.jpg') and f[:-4] not in keep:
                os.remove(os.path.join(d, f))
                removed += 1

    print('照片同步完成：需要 %d 張，新增 %d、刪除孤兒 %d、失敗 %d'
          % (len(ids), added, removed, failed))
    if failed:
        sys.exit('有照片抓不下來，先確認 Drive 資料夾仍是「知道連結的人可檢視」。')


if __name__ == '__main__':
    main()
