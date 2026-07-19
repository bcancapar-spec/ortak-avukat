# Kurulum Senkronu — repo ≠ çalışan araç (Fable K1)

> **Sorun:** Bu depo (`~/.claude/plug-in/ortak-avukat-main`) **kaynaktır**. Claude'un
> fiilen çalıştırdığı **kurulu** eklenti başka yerdedir ve **bayat**: PATH'te
> `~/.claude/plugins/cache/ortak-avukat/ortak-avukat/**0.3.20**/` görünüyor ve skill
> listesinde **hem `ortak-avukat:oa-*` hem `anthropic-skills:oa-*`** aileleri (ikisi de
> `oa-arsiv`'li, eski doktrinli) var. **Bu depodaki iyileştirmeler, kurulu araca kadar
> reinstall yapılmadan yansımaz.**

## Senkron adımları

### 1. Kaynağı sürümle (bu oturumda yapıldı)
```bash
cd ~/.claude/plug-in/ortak-avukat-main
git init && git add -A && git commit -m "v0.5.0"
```

### 2. GitHub'a it (marketplace kurulumu için)
```bash
gh repo create ortak-avukat --private --source=. --push
# veya: git remote add origin <url> && git push -u origin main
```

### 3. Claude Code'da yeniden kur (bu komutları SEN çalıştırırsın — ben interaktif /plugin koşamam)
```
/plugin marketplace add <github-kullanıcı>/ortak-avukat
/plugin install ortak-avukat@ortak-avukat
```
Alternatif: `releases` altındaki `.plugin` dosyasını sohbete bırakıp onayla.

### 4. BAYAT / MÜKERRER kopyaları kaldır (kritik)
- Eski `ortak-avukat@0.3.20` cache'i: `~/.claude/plugins/cache/ortak-avukat/ortak-avukat/0.3.20/` (yeni sürüm kurulunca `/plugin` yönetiminden eski sürümü kaldır).
- **Mükerrer `anthropic-skills:oa-*` ailesi:** skill listesinde ikinci bir kopya olarak görünüyor — `/plugin` yönetiminden kaldır ki iki farklı (biri bayat) aile aynı anda tetiklenmesin.

### 5. Doğrula
Reinstall sonrası skill listesinde: **tek** `ortak-avukat` ailesi · **`oa-arsiv` YOK** · 20 skill · v0.5.0. `oa-arsiv` hâlâ görünüyorsa bayat kopya kalmıştır.

## Neden önemli
`aile_dogrula`/`pytest` **depoyu** denetler; ama Claude **kurulu kopyayı** çalıştırır.
Senkron yapılmadan, bu oturumdaki hiçbir düzeltme (Windows çökme onarımı, gizlilik
m.6 genişletmesi, kunye_teyit deliği, İYUK m.8/3 fix...) masandaki araçta **yok**.

---
© 2026 Av. Bayram Can Çapar — FSEK. İzinsiz çoğaltma/dağıtma/türev yasaktır.
