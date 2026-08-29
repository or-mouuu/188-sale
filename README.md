# 青年路搬家二手拍 · 前台

買家看的商品展示頁。列表看照片／品名／售價，點開有詳細資訊 pop-up，
選好的商品加進「想買清單」後一鍵複製，貼給賣家聯繫。網站不收錢、不結帳。

- 65 件商品，56 件有照片（共 113 張）
- 資料來源：後台盤點工具 <https://claude.ai/code/artifact/dde24bcb-dc5e-44cd-acb8-c44b247b2d6f>
- 線上版（照片內嵌、單一檔案）：<https://claude.ai/code/artifact/e9dfb950-06d0-4a8b-b129-eaf990cc14bb>

後台也有一份離線副本在 `admin/`（`test.html` 是帶假 API 的本機測試版，
線上正本在 <https://claude.ai/code/artifact/dde24bcb-dc5e-44cd-acb8-c44b247b2d6f>）。

## 這個資料夾怎麼用

`index.html` + `photos/` 就是完整的靜態網站，不需要後端。直接部署：

```bash
npx netlify-cli deploy --dir . --prod
```

或推上 GitHub 後開 Pages（Settings → Pages → Deploy from a branch → root）。

本機預覽：

```bash
python3 -m http.server 8791 --directory /Users/mou/qingnian-secondhand
```

## 要改東西的話

**聯絡方式**（目前是待填的 placeholder）在 `index.html` 裡，
搜尋 `▼▼ 聯絡方式` 就會看到，把「（待填：LINE ID 或 IG 帳號）」換掉。
`build/shop.html` 樣板裡也有同一段，一起改才不會被下次重建蓋掉。

**商品資料**改完後台後，重跑一次 `build/` 裡的流程：

```bash
cd /Users/mou/qingnian-secondhand/build
python3 prep.py data.json items.json      # 後台資料 → 前台資料（需先匯出 data.json）
python3 map_photos.py                     # 商品 → Drive 照片對照表
python3 photos_json.py                    # 產生內嵌版與檔案版照片表
python3 build.py photos-files.json ../index.html
```

`prep.py` 會做兩件重要的事：把售價／原價字串拆成數字，以及**濾掉備註欄裡的內部盤點註記**
（「照片有、清單未列」「規格欄請補數量」「⚠️…需確認」這類給自己看的話）。
黑名單在 `prep.py` 的 `INTERNAL`，新增內部用語時記得補進去。

## 後台的三個欄位怎麼影響前台

- **已售出**（`sold`）：後台編輯視窗最上面的開關。打開之後 `prep.py` 會直接跳過這件，
  前台就看不到它了。後台自己仍然看得到，只是變成灰色、不再計入待補統計。
- **商品參考網址**（`link`）：填了前台詳細頁就會出現「看這件商品的原始頁面」。
  目前 3 筆（微波爐、烤箱、貓用體重計）是從舊的備註欄搬過來的。
- **列表預覽圖**（`cover`）：決定列表卡片顯示哪一張照片。判斷順序寫在
  `map_photos.py` 的 `cover_first()`：先找檔名含 `cover` 欄位指定字串的，
  再找檔名開頭是 `*` 或含「封面」／`cover` 的，都沒有就用資料夾裡的第一張。

後台還可以再補的是一個獨立的「對外備註」欄位——現在靠關鍵字過濾內部註記，不夠可靠。

## 已知狀況

- 65 件裡有 40 件沒定價，前台顯示「價格洽談」，不計入小計。
- 電腦椅、洗衣機、蘆筍鍋、十八紙椅凳在後台標為「待確認」，目前照樣上架。
- Drive 資料夾名稱和品名對不起來的，寫在 `map_photos.py` 的 `MANUAL`
  （單人床組→#1、黑色抽屜櫃→#11、無印紙板層櫃→#12）。新增這類資料夾時要補進去。
- 照片原檔是 HEIC，已轉成 JPEG：`photos/t/` 是列表縮圖（560px），
  `photos/f/` 是詳細頁大圖（1600px）。
