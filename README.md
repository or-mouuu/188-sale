# 青年路搬家二手拍

買家看的商品展示頁，加上一個可以自己發佈的後台。

- **前台**：<https://or-mouuu.github.io/188-sale/>
- **後台**：<https://or-mouuu.github.io/188-sale/admin/>
- 65 件商品，131 張照片

## 怎麼更新

1. 開後台，改資料（也可以在 Drive 對應資料夾裡加照片）
2. 按右上角 **發佈到前台**
3. 等約兩分鐘，網站就更新好了

按下發佈時，後台把 `data/data.json` 寫回這個 repo；GitHub Actions 接手重跑
整條管線——比對 Drive 照片、把新照片抓下來轉成 JPG、產生 `index.html`——
再 commit 回來，GitHub Pages 自動部署。**你的電腦不需要做任何事。**

第一次開後台會要你設一組密碼，並貼上 GitHub token（權限只要這個 repo 的
Contents: Read and write）。token 會用這組密碼加密（AES-GCM，金鑰用
PBKDF2 從密碼導出）後才存進瀏覽器，密碼本身不會被存下來。之後每次開後台
要輸入密碼解鎖，同一個分頁內不用重打。

**這道鎖的界線要講清楚**：後台網址是公開的，頁面原始碼也是公開的，所以
密碼擋得住路過的人，擋不住懂技術的人繞過畫面。真正有效的防護是權杖被加密
存放——沒有密碼就解不開、也就發佈不了。另外 `data/data.json` 在公開 repo
上任何人都讀得到，這點不會因為有密碼而改變。

## 三個欄位怎麼影響前台

- **已售出**：打開開關，這件就不會出現在前台。
- **商品參考網址**：填了前台詳細頁會出現「看這件商品的原始頁面」。
- **列表預覽圖**：決定列表卡片顯示哪張照片。判斷順序寫在
  `build/map_photos.py` 的 `cover_first()`：先找檔名含這個欄位指定字串的，
  再找檔名開頭是 `*` 或含「封面」／`cover` 的，都沒有就用資料夾裡的第一張。

## 資料夾

```
data/data.json    唯一的資料正本，後台發佈時改寫這裡
index.html        前台（由 Actions 產生，不要手改）
photos/t, photos/f  列表縮圖 560px、詳細頁大圖 1600px（由 Actions 產生）
admin/index.html  後台
build/            重建管線
.github/workflows/build.yml   自動重建
```

## 本機重建

```bash
pip install Pillow pillow-heif
python3 build/build_site.py
```

管線做四件事：`prep.py` 把後台資料轉成前台資料（順便**濾掉備註欄裡的內部
註記**，黑名單在 `INTERNAL`）、`map_photos.py` 比對 Drive 照片、
`photos_sync.py` 只抓缺少的照片、`build.py` 把 `build/shop.html` 樣板
和資料組成 `index.html`。

## 前提與注意事項

- **Drive 資料夾必須維持「知道連結的人可檢視」**，否則 Actions 抓不到照片。
- Drive 資料夾名稱和品名對不起來的，寫在 `map_photos.py` 的 `MANUAL`。
- **`data/data.json` 是公開的**，任何人都讀得到。內部提醒不要寫進備註欄。
- 照片搬進同名資料夾後，管線會自動改用整個資料夾，不用回頭改後台的連結。

## Claude artifact 版

`build/shop.html` 也可以產生照片內嵌的單一檔案版（給 Claude artifact 用）：

```bash
python3 build/photos_sync.py --inline
python3 build/photos_json.py
python3 build/build.py photos-inline.json ../artifact.html
```

那份要手動發佈，不會跟著自動更新。
