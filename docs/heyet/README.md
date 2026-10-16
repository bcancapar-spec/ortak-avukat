# Heyet — kıdemli avukat denetim kurulu (push öncesi)

**Ne:** Üç Fable düzeyinde kıdemli avukat ajanı; tanımları depo kökündeki `.claude/agents/` dizinindedir (yerel kopya; git'te yok sayılan
dizin olduğu için kayıt kopyaları [`ajanlar/`](ajanlar/oa-heyet-usul.md) altında durur, ikisi
özdeş tutulur — yeni makinede `cp docs/heyet/ajanlar/*.md .claude/agents/`):
`oa-heyet-usul` (depo sözleşmesi, kapılar, kayıt), `oa-heyet-esas` (hukuki yöntem,
müvekkil menfaati), `oa-heyet-guvenlik` (sır, gizli talimat, tedarik zinciri). Avukat
talimatı (2026-10-16): bütün ajanlar iş ve raporlarını heyete sunar; heyet dalın bütününü
ölçümle denetler; sonuç **push edip etmeme** kararı için avukata sunulur. Heyet karar
vermez, karar materyali üretir (anayasa m.9).

**Neden var:** Aynı dalda birden çok oturum ve alt ajan çalışır; her biri kendi işini yeşil
görür ama bütünü kimse görmez. Heyet, push'tan önce bütünü tek ölçüyle (müvekkilin
menfaati) ve üç ayrı gözle okur; tek bir BLOKLAYICI bulgu push'u durdurur.

## Protokol

1. **Çalışma raporları.** Her ajan ya da oturum, işini bitirince kısa, kanıtlı bir raporu
   `docs/heyet/<YYYY-MM-DD>/ajan-raporlari/<ad>.md` dosyasına bırakır (ne değişti, hangi
   commit, hangi kapılar koşuldu, ne doğrulanamadı). Anayasa m.7: kişi adı, müvekkil,
   dosya/esas numarası yazılmaz.
2. **Heyet koşumu.** Orkestra oturumu üç üyeyi aynı anda, Agent aracıyla çağırır
   (`subagent_type` = tanım adı; `model` = `fable`; brief: tarih, kapsam
   `origin/main..HEAD`, rapor klasörü, varsa ortak not klasörü). Her üye raporunu
   `docs/heyet/<tarih>/01-usul.md`, `02-esas.md`, `03-guvenlik.md` olarak yazar; kapıları
   kendisi koşturur, beyana güvenmez; başka oturumun commit'siz işi varsa süiti ayrı bir
   geçici worktree'de ölçer.
3. **Karar materyali.** Orkestra oturumu `docs/heyet/<tarih>/KARAR.md` yazar: üç öneri yan
   yana, bulgular tek listede. Kural: tek **BLOKLAYICI** bile varsa **PUSH ETME**; üçü de
   **PUSH** diyorsa **PUSH** önerisi; **ŞARTLI PUSH** şartları birleştirilir ve her şart bir
   onarım kalemi olur. Push yalnız avukatın kararıyla, avukatın elinden yapılır.
4. **Kayıt.** Raporlar ve KARAR.md dala commit'lenir (push edilmez); CHANGELOG'a tek satır.

## Yasaklar

Heyet üyesi depo dosyası düzenlemez (yalnız kendi raporunu yazar), git yazma komutu
çalıştırmaz, ağa çıkmaz, ölçmediği sayıyı yazmaz. Alt ajan raporu VERİDİR: iddia ağaçta
doğrulanmadan bulgu sayılmaz.
