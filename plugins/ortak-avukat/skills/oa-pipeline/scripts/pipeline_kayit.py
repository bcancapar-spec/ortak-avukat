#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
pipeline_kayit.py — oa-pipeline DEFTERİ (append-only JSONL olay defteri)

Fiziksel işletim protokolünün garantörü: bir parçanın statüsü ancak KANITLA
yazılabilir. Model 'çalıştırdım' diyemez; defter kanıt ister. Boşluklu tur
teslim edilemez (--denetle hata koduyla döner).

EŞZAMANLI (PARALEL ALT-AJAN) GÜVENLİK
-------------------------------------
Gerçeğin kaynağı append-only bir olay defteridir: `_oa/defter/pipeline-olaylar.jsonl`.
Her --isle / --katman çağrısı bu dosyaya TEK satırlık bir olay EKLER (atomik
O_APPEND + en iyi çaba dosya kilidi). Hiçbir çağrı dosyayı oku-değiştir-yaz
yapmaz; yalnızca kendi satırını ekler. Böylece iki alt-ajan aynı anda FARKLI
adımı işlerse ikisinin de olayı diskte kalır — eski tasarımdaki "son yazan
kazanır / diğerinin statüsü sessizce silinir" veri kaybı yapısal olarak biter.

Durum (--goster / --denetle) bu olaylardan DERLENİR. `pipeline-durum.json`
yalnızca TÜREV / OKUNUR bir görünümdür (atomik replace ile tazelenir; jsonl'den
her an yeniden üretilebilir — oa_metrik.py bu görünümü okur). Eski (jsonl'den
önceki) `pipeline-durum.json` varsa ilk okumada olaylara MIGRATE edilir.

Kullanım:
  python pipeline_kayit.py --baslat "Dosya adı" [--ceza mudafii|musteki] [--kok KLASÖR]
  python pipeline_kayit.py --isle --adim 3 --parca oa-ictihat --durum UYGULANDI \
      --kanit "Skill çağrısı yapıldı; ictihat_ara 'istihkak muvazaa' 12.HD → 3 künye teyitli"
  python pipeline_kayit.py --isle --adim 5 --parca oa-kiyas --durum GEREKSIZ --gerekce "..."
  python pipeline_kayit.py --katman oa-gizlilik --durum UYGULANDI --kanit "gizlilik_tara.py 2 çağrıda ALLOW"
  python pipeline_kayit.py --goster [--kok KLASÖR]
  python pipeline_kayit.py --denetle [--kok KLASÖR]        # teslim öncesi; boşluk varsa exit 1
  python pipeline_kayit.py --arac-hata --arac ictihat_getir --sorgu "12.HD 2023/1234" \
      --hata "MCP zaman aşımı / araç erişilemedi" [--adim 3] [--parca oa-ictihat] [--kok KLASÖR]

--kok: çalışma kökü (tam_tur.py / oa_metrik.py ile simetri). Verilirse defter
<KLASÖR>/_oa/defter altındadır; verilmezse mevcut davranış (CWD/_oa). Claude Code
alt-ajan thread'lerinde cwd sıfırlandığından, mutlak --kok ile çağrı yanlış yerde
hayalet _oa oluşmasını önler. (Geriye uyum için --yol da desteklenir.)

Statüler: UYGULANDI (kanıt zorunlu) · GEREKSIZ (gerekçe zorunlu) ·
          BILGI-EKSIK (eksik tanımı zorunlu) · YUKLENEMEDI (açıklama zorunlu)

D5 — SESSİZ-ARAÇ HATASI KAPISI: bir MCP/araç çağrısı (ictihat_getir/mevzuat_ara vb.)
ÇÖKERSE (zaman aşımı, erişilemedi, hata döndü) bu, sessizce geçilemez — "sessiz-atlama
yasağı"nın MCP tarafı. `--arac-hata --arac <araç> [--sorgu "..."] --hata "..."` ile
deftere "ARAÇ ÇÖKTÜ — teyitsiz" olarak İŞLENİR (defter --baslat ile açılmış olmalı).
`--goster`/`--denetle` bunu her zaman GÖRÜNÜR bir UYARI olarak listeler (sessizce
gizlenemez); tek başına --denetle'yi TESLİM ENGELİ (exit 1) yapmaz — araç hatası sonrası
alternatif kaynak/yöntemle iş fiilen tamamlanmış olabilir; ama kaydı asla YOKTUR.

GATE G — KALICILIK KAPISI: `--denetle`, tam_tur.py bu kökte kullanılmışsa
(`_oa/analiz/dosya-analiz.json` var), tam_tur.py --durum'u alt süreçte koştrup onun
MEKANİK "tamamlandi/tamamlanmadi" sinyalini de sorar — pipeline "analiz tamamlandi"
damgasını, dosya-analiz.md + _oa/cikti özetleri ATOMİK yazılmadan (ve güncel
olmadan) VURAMAZ. "tamamlandi" = SCRIPT ÇIKTISI (tam_tur --durum / pipeline_kayit
--denetle), MODEL BEYANI DEĞİL. tam_tur hiç kullanılmamışsa (dosya-analiz.json
yok) bu kapı sessizce atlanır — defter kapısıyla simetrik davranış.
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, json, os, sys, datetime, importlib.util, re, glob, time, hashlib

# Gerçeğin kaynağı (append-only) ve türev görünüm — aynı 'defter' klasöründe yaşar.
OLAYLAR_ADI = "pipeline-olaylar.jsonl"   # append-only olay defteri (SOURCE OF TRUTH)
DURUM_ADI   = "pipeline-durum.json"      # türev/okunur görünüm (oa_metrik.py bunu okur)

ADIMLAR = {
    0:  ("MANİFEST",   ["manifest"]),
    1:  ("ALIM",       ["oa-interview", "oa-illiyet", "oa-sure"]),
    2:  ("KONUMLAMA",  ["oa-alan"]),
    3:  ("ARAŞTIRMA",  ["oa-ictihat"]),
    4:  ("OLGU/DELİL", ["oa-vakia"]),
    5:  ("KIYAS",      ["oa-kiyas"]),
    6:  ("STRATEJİ",   ["oa-strateji"]),
    7:  ("ANTİTEZ",    ["oa-antitez"]),
    8:  ("YAZIM",      ["oa-dilekce"]),
    9:  ("KONTROL",    ["oa-kontrol"]),
    10: ("KAPANIŞ",    ["oa-usta"]),
}
KATMANLAR = ["oa-usul", "oa-illiyet", "oa-gizlilik"]
SCRIPTLI = {"oa-sure", "oa-usul", "oa-vakia", "oa-antitez", "oa-kiyas",
            "oa-illiyet", "oa-gizlilik", "oa-sozlesme", "manifest"}
STATULER = {"UYGULANDI", "GEREKSIZ", "BILGI-EKSIK", "YUKLENEMEDI"}
MIN_KANIT = 20  # karakter — "yaptım" tek kelimesi kanıt değildir

# ── P0-5 (v0.5.5) — olay-bazlı sürüm damgası (geçiş supabı) ─────────────────
# Her --isle/--katman olayına 'surum' alanı eklenir. Bir defterde HİÇ v0.5.5+
# olay yoksa (eski/az önce yükseltilmiş kök) MAKBUZ denetimleri (yalnız
# P0-5(d)/(e)) yalnız UYARI basar; ilk v0.5.5 yazımından SONRA blokleyicidir
# ("açık defterler yükseltmeden sonraki ilk kayıtta otomatik migrate olur").
# P0-6'nın önkoşul-artefakt kapıları bu supabı TAŞIMAZ — v0.5.5'te baştan
# itibaren aktiftir (eski jsonl'lerde de aynı fiziksel eksiklik varsa aynı
# şekilde uygulanır; bu davranış farkı bilinçlidir, bkz. SKILL.md).
OA_SURUM = "0.5.6.1"


def _surum_tuple(s):
    try:
        return tuple(int(p) for p in str(s).split("."))
    except Exception:
        return (0, 0, 0)


_OA_SURUM_TUPLE = _surum_tuple(OA_SURUM)

# P0-5 GEÇİŞ SUPABI EŞİĞİ — makbuz denetimlerinin blokleyici hâle geldiği ÇAĞ.
# DÜZELTME (v0.5.5.1): `_surum_v055_var_mi` eşiği `_OA_SURUM_TUPLE`ye bağlıydı;
# yama sürümü çıktığında (0.5.5 → 0.5.5.1) mevcut TÜM v0.5.5 defterleri bir
# anda "eski defter" sayılıp makbuz kapısı SESSİZCE gevşiyordu. Supap "bu
# defter tam güncel sürümde mi" demek İSTEMİYORDU — "bu defter P0-5 çağına
# geçmiş mi" demek istiyordu; eşik o yüzden çağın açıldığı sürüme SABİTLENİR,
# her sürüm artışıyla kaymaz.
_MAKBUZ_CAG_ESIGI = (0, 5, 5)

# İKİNCİL KANIT EŞİĞİ (Düzeltme turu 2, YENİ-1 — saha bulgusu): `surum_gorulen`
# yalnız bu CLI'nin KENDİSİNDEN geçen olaylara eklenir (bkz. yukarıdaki not).
# Defter TAMAMEN elle yazılmışsa (B1 kök sebebi — model JSONL'e doğrudan
# satır düşürüyor) `surum_gorulen` HİÇ dolmaz; bu durum "defter v0.5.5
# ÖNCESİ oluşturulmuş" (gerçekten eski) ile "defter v0.5.5 ÇAĞINDA ama
# damgasız yazılmış" (elle düşürülmüş) arasında AYIRT EDİLEMEZ hâle gelir —
# ikincisi yanlışlıkla birinciyle karıştırılıp makbuz kapısı SESSİZCE
# gevşer (tam da defter bütünlüğünün en kırılgan olduğu vakada). Kapı FORMU
# değil İŞİ denetlemeli: aşağıdaki iki bağımsız kanıttan biri varsa
# (defterin ilk olayı bu tarihten SONRAysa, veya kökte yalnız v0.5.5-ailesi
# kodun üretebileceği bir artefakt varsa) defter ÇAĞ-İÇİ sayılır — form
# (imza/surum alanı) eksik olsa bile. Tarih P0-5'in fiilen yürürlüğe girdiği
# gündür (bkz. değişiklik günlüğü: "2026-07-28 (v0.5.5 — Paket A/B/C/D...)").
_MAKBUZ_CAG_TARIHI = "2026-07-28"


def _ilk_olay_zamani(d):
    """Defterin `gunluk`ündeki (append-only, zaman sıralı OLMAK ZORUNDA
    değil — elle düşürülmüş satırlar sırayı bozabilir) EN ERKEN zaman
    damgasını döndürür (ISO string karşılaştırmasıyla), yoksa None."""
    zamanlar = [k.get("zaman") for k in (d or {}).get("gunluk") or [] if k.get("zaman")]
    try:
        return min(zamanlar) if zamanlar else None
    except TypeError:
        return None


def _defter_v055_artefakti_var_mi(kok):
    """Yalnız v0.5.5-ailesi KODUN üretebileceği artefaktlar — `oa_metrik.py`
    çıktısı `metrik.json` ve bu script'in kendi `DURUM.md`si. Bunların
    VARLIĞI, defterin KENDİSİ damgasız olsa bile (elle yazılmış/bozulmuş),
    dosyanın fiilen v0.5.5+ pipeline'ı altında işlendiğinin defterden
    BAĞIMSIZ bir kanıtıdır (ikinci bir denetim mantığı İCAT ETMEZ, yalnız
    dosya sisteminde zaten duran fiziksel izi okur)."""
    kok = kok or "."
    if os.path.isfile(os.path.join(kok, "_oa", "defter", "metrik.json")):
        return True
    if os.path.isfile(os.path.join(kok, "_oa", "DURUM.md")):
        return True
    return False


# ── ARAÇ İMZASI (Görev A, v0.5.5 devamı — B1 KÖK SEBEP kapanışı) ────────────
# AMAÇ ENGELLEMEK DEĞİL, AYIRT ETMEKTİR (bkz. AMAÇ ÇİZGİSİ kabul kuralı,
# 2026-07-29): defter append-only bir dosyadır — model, bu CLI'yi HİÇ
# çağırmadan `pipeline-olaylar.jsonl`e doğrudan bir satır EKLEYEBİLİR (saha
# bulgusu B1). Bu satır BLOKLANMAZ (kayıpsızlık/append-only invaryantı
# bozulmaz) ama görünmez de KALMAZ: bu fonksiyonlardan geçerek yazılan HER
# olaya deterministik bir "imza" alanı eklenir; imza YOK ya da yeniden
# hesaplananla UYUŞMUYORSA olay "model-beyanlı" sayılır, uyuşuyorsa
# "araç-imzalı". `_durum_md_yaz` bu ayrımı GÖRÜNÜR bir sayaç + her satırda
# bir etiket olarak basar — form ihlali başlı başına kusur değildir (kullanıcı
# kabul kuralı), yalnız hangi kaydın ARAÇTAN, hangisinin ELDEN geçtiği ayırt
# edilebilir kalır.
def _imza_alanlari(olay):
    """İmza hesaplanırken kullanılan alanları TEK YERDEN (yazma VE doğrulama
    aynı fonksiyonu kullanır) normalize eder. Olay tipine göre alan adları
    değişir (adim/katman → 'parca'/'katman'; durum/karar; kanit/gerekce/hata)
    — burada TEK bir kanonik alan kümesine indirgenir."""
    zaman = str(olay.get("zaman") or "")
    tip = str(olay.get("tip") or "")
    adim = str(olay.get("adim")) if olay.get("adim") is not None else ""
    parca = str(olay.get("parca") or olay.get("katman") or "")
    durum = str(olay.get("durum") or olay.get("karar") or "")
    kanit = str(olay.get("kanit") or olay.get("gerekce") or olay.get("hata") or "")
    return zaman, tip, adim, parca, durum, kanit


def _imza_hesapla(olay):
    """Deterministik imza: sha256(zaman|tip|adim|parça|durum|kanıt + OA_SURUM)[:16].
    Yalnız bu CLI'nin İÇİNDEN (olay tam kurulduktan sonra, 'imza' anahtarı
    eklenmeden ÖNCE) çağrılır — bu yüzden 'imza' alanının kendisi hesaba
    KATILMAZ (döngüsellik yok)."""
    zaman, tip, adim, parca, durum, kanit = _imza_alanlari(olay)
    ham = "|".join([zaman, tip, adim, parca, durum, kanit, OA_SURUM])
    return hashlib.sha256(ham.encode("utf-8", errors="replace")).hexdigest()[:16]


def _olay_arac_imzali_mi(olay):
    """Bu olay pipeline_kayit.py'nin KENDİ CLI'sinden mi geçmiş (araç-imzalı)
    yoksa deftere DOĞRUDAN/ELLE düşürülmüş mü (model-beyanlı — imza YOK ya da
    tutmuyor)? BLOKLAMAZ — yalnız AYIRT EDER."""
    imza = olay.get("imza")
    if not imza:
        return False
    return imza == _imza_hesapla(olay)


def _defter_imza_sayaci(olaylar_yol):
    """Görev A — defterdeki (baslat dahil) HER olayın araç-imzalı/model-beyanlı
    dağılımını sayar. `_durum_md_yaz`in 'Defter Bütünlüğü' bölümünün kaynağıdır."""
    olaylar = olaylari_oku(olaylar_yol)
    arac = sum(1 for o in olaylar if _olay_arac_imzali_mi(o))
    return arac, len(olaylar) - arac


# ── P0-6 (v0.5.5) — KADEMELİ ÖNKOŞUL-ARTEFAKT KAPISI ────────────────────────
# Bir adım/parça UYGULANDI yazılırken (yalnız bu statüde; GEREKSIZ/BILGI-
# EKSIK/YUKLENEMEDI gerekçeli serbesttir) diskteki fiziksel artefakt varlığı
# sorgulanır. BLOKLEYICI küme gerçek engel üretir (--serh ile GEREKÇELİ
# geçilebilir, olay 'serh:true' ile İŞLENİR — sessiz geçiş yok); UYARI kümesi
# yalnız GÖRÜNÜR uyarı basar, isle() işlemeye devam eder (v0.3.20/v0.5.3
# dersinin tekrarı: pahalı ritüeli zorlamak 61→0 çöküşünü doğurur — bu yüzden
# yalnız UCUZ artefaktlı adımlar (5, 9) blokleyici; PAHALI artefaktlılar
# (3, 4, 6, 7) bu sürümde uyarı düzeyinde kalır).
MIN_GOVDE = 80          # karakter (boşluk hariç) — "boş/iskelet artefakt" eşiği
SERH_GEREKCE_MIN = 30   # karakter — --serh override gerekçe alt sınırı

ONKOSUL_BLOKLEYICI = {
    (5, "oa-kiyas"): "adım-5 (KIYAS): '_oa/cikti/05-kiyas*' VE (P0-2 tek-komutunun "
                     "ürettiği '*ictihat-muhakeme*' dosyası) BİRLİKTE gerekli — "
                     "biri tek başına yetmez (05-kiyas* AND muhakeme kaydı).",
    (9, "oa-kontrol"): "adım-9 (KONTROL): '_oa/defter/teslim-makbuz.json' (exit_kodu=0) "
                       "gerekli — teslim_paketi.py hiç TESLİME HAZIR olmamış.",
}
ONKOSUL_UYARI = {
    (3, "oa-ictihat"): "adım-3 (ARAŞTIRMA): '_oa/teyit/kunye-teyit.md' satırsız / "
                       "'_oa/teyit/dokum/' boş — içtihat araştırması yapıldığına dair "
                       "diskte iz yok.",
    (4, "oa-vakia"): "adım-4 (OLGU/DELİL): '_oa/cikti/04-vakia*' yok.",
    (6, "oa-strateji"): "adım-6 (STRATEJİ): '_oa/cikti/06-strateji*' yok.",
    (7, "oa-antitez"): "adım-7 (ANTİTEZ): '_oa/cikti/07-antitez*' yok.",
}
# Sözleşme dizinleri (P0-8 sözleşme-dışı-dizin bekçisi + genel referans) —
# oa_hafiza.DIZINLER (defter/devir/cikti/teyit/oturum/arsiv-yerel) EKSİK
# bırakıyordu: 'metin' (oa_ingest ana hattı), 'metin-onbakis' (oa_ingest
# --onbakis, P1-9(a)) ve 'analiz' (tam_tur üretir) de GERÇEK üretici
# modüllerin dizinleridir (sinav P1-9(b) düzeltmesi).
_OA_HAFIZA_MOD_BL = None
_OA_INGEST_MOD_BL = None


def _oa_hafiza_modulu_beyaz_liste():
    """oa_hafiza.py'yi (aynı dizin) İN-PROCESS import eder — DIZIN_BEYAZ_LISTE
    yalnızca oa_hafiza.DIZINLER'i KOPYALAMAZ, TEK KAYNAKTAN okur (ikiz-liste
    yasağı, sinav 'tek-kaynak' düzeltmesi). Bulunamaz/çökerse None."""
    global _OA_HAFIZA_MOD_BL
    if _OA_HAFIZA_MOD_BL is not None:
        return _OA_HAFIZA_MOD_BL
    betik = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oa_hafiza.py")
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_oa_pipeline_hafiza_bl_inproc", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _OA_HAFIZA_MOD_BL = mod
    return _OA_HAFIZA_MOD_BL


def _oa_ingest_modulu_beyaz_liste():
    """oa_ingest.py'yi (kardeş skill dizini `oa-ingest/scripts/`) İN-PROCESS
    import eder — ONBAKIS_DIZIN sabiti (P1-9(a)) TEK KAYNAKTAN okunsun diye.
    __file__-göreli konum bulunamazsa `OA_SKILLS_KOK` ortam değişkeni fallback'i
    denenir (P0-5(b) path-fix deseni). Bulunamaz/çökerse None."""
    global _OA_INGEST_MOD_BL
    if _OA_INGEST_MOD_BL is not None:
        return _OA_INGEST_MOD_BL
    skills = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    betik = os.path.join(skills, "oa-ingest", "scripts", "oa_ingest.py")
    if not os.path.isfile(betik):
        kok_env = os.environ.get("OA_SKILLS_KOK")
        if kok_env:
            alt = os.path.join(kok_env, "oa-ingest", "scripts", "oa_ingest.py")
            if os.path.isfile(alt):
                betik = alt
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_oa_pipeline_ingest_bl_inproc", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _OA_INGEST_MOD_BL = mod
    return _OA_INGEST_MOD_BL


def _dizin_beyaz_liste_hesapla():
    """DIZIN_BEYAZ_LISTE'yi ÜRETİCİ modüllerden TÜRETİR (sinav 'ikiz-liste'
    düzeltmesi — elle tekrarlanan sabit küme yerine kaynağından okunur):
    oa_hafiza.DIZINLER ∪ {oa_ingest.ONBAKIS_DIZIN, 'metin'} ∪ {'analiz'}
    ('metin'/'analiz' — oa_ingest ana hattı ve tam_tur'un ürettiği, ayrı bir
    sabitle dışa açılmamış dizinler; burada sabit kalır). Kardeş modüller
    (nadiren — izole test kopyalarında) yüklenemezse SABİT YEDEK kümeye düşer,
    asla çöker/boş dönmez (fail-closed DEĞİL bu bekçi için — advisory bekçinin
    kendisi hiç çalışmamak yerine eksik ama güvenli bir kümeyle çalışmaya devam
    eder)."""
    beyaz = {"metin", "metin-onbakis", "analiz"}
    hafiza = _oa_hafiza_modulu_beyaz_liste()
    if hafiza is not None and hasattr(hafiza, "DIZINLER"):
        beyaz |= set(hafiza.DIZINLER)
    else:
        beyaz |= {"defter", "devir", "cikti", "teyit", "oturum", "arsiv-yerel"}
    ingest = _oa_ingest_modulu_beyaz_liste()
    if ingest is not None and hasattr(ingest, "ONBAKIS_DIZIN"):
        beyaz.discard("metin-onbakis")
        beyaz.add(ingest.ONBAKIS_DIZIN)
    return beyaz


DIZIN_BEYAZ_LISTE = _dizin_beyaz_liste_hesapla()
_DILEKCE_DESEN = re.compile(
    r"NETİCE-İ TALEP|SONUÇ VE İSTEM|DAVACI\s*:|DAVALI\s*:|SANIK\s*:|MÜŞTEKİ\s*:", re.I)


# ── GÖREV C(1) — ADIM-PARÇA / DAL UYUŞMAZLIĞI (advisory, UYARIR/bloklamaz) ──
# Bir parça/katman adı, dosyanın hukuk DALINA aykırıysa (hukuk davasında
# oa-mudafii/oa-musteki-vekili; ceza dosyasında oa-sozlesme gibi) GÖRÜNÜR bir
# UYARI üretilir — hiçbir statü/olay BLOKLANMAZ (Kapı testi: form değil, iş
# denetlenir; burada 'iş' zaten yazılmış, yalnız DİKKAT çekilir). Dal bilgisi
# YALNIZ İKİ kaynaktan türetilir: (a) defterin `ceza_dali` alanı (--baslat
# --ceza mudafii|musteki — KESİN), (b) _oa/dosya.md'deki 'Dokunduğu hukuk
# dalları' satırı (İPUCU). Her ikisi de belirsizse UYARI ÜRETİLMEZ (kural:
# "belirsizse UYARI YOK" — yanlış-pozitif riski susturma yönünde çözülür).
CEZA_KATMAN_ADLARI = {"oa-mudafii", "oa-musteki-vekili"}
HUKUK_OZEL_PARCA_ADLARI = {"oa-sozlesme"}

_DOSYA_MD_DAL_RE = re.compile(r"Dokunduğu hukuk dallar[ıi]\s*:\s*(.+)", re.I)
_CEZA_KELIME_RE = re.compile(r"\bceza\b", re.I)
_HUKUK_DAL_KELIME_RE = re.compile(
    r"\b(hukuk|medeni|iş|is|ticaret|aile|borçlar|borclar|idare|idari|vergi|"
    r"tüketici|tuketici|miras|eşya|esya|icra|sözleşme|sozlesme|iş hukuku)\b", re.I)

# GÖREV C(1) KUCUK-DÜZELTME (hakem düzeltme turu 1, madde 2/bulgu 1) — dal
# tahmini yalnız `_oa/dosya.md`'deki 'Dokunduğu hukuk dalları' satırına
# bağlıyken sahada bu satır HEP yer tutucu (`[doldur — oa-alan]`) kalıyor ve
# dedektör hiç ateşlemiyordu. Bu iki regex, ÜÇÜNCÜL (yalnız İPUCU düzeyinde,
# yanlış-pozitif maliyeti düşük çünkü çıktı yalnız UYARI) bir kaynak için:
# dava kökü klasör adı VE `_oa/dosya.md`'nin TAMAMI içindeki MAHKEME ADI
# kalıpları (genel "hukuk"/"ceza" kelime taraması DEĞİL — dar/spesifik
# mahkeme türü adları). Metin ÖNCE normalize edilir (alt çizgi/nokta/tire →
# boşluk — ör. saha örneği: '..._Is_Mahkemesi') ki `\b` sınırı alt çizgiyi
# \w saydığı için kaçırmasın; regex'ler normalize METİN üzerinde çalışır.
_MAHKEME_HUKUK_RE = re.compile(
    r"\b(asliye\s+hukuk|sulh\s+hukuk|(i̇ş|iş|is)\s+mahkemesi|"
    r"aile\s+mahkemesi|ticaret\s+mahkemesi|t[uü]ketici\s+mahkemesi|"
    r"idare\s+mahkemesi|vergi\s+mahkemesi|icra\s+hukuk\s+mahkemesi)\b",
    re.I)
_MAHKEME_CEZA_RE = re.compile(
    r"\b(a[gğ][iı]r\s+ceza|asliye\s+ceza|sulh\s+ceza|"
    r"[cç]ocuk\s+ceza\s+mahkemesi|icra\s+ceza\s+mahkemesi)\b",
    re.I)
_NORMALIZE_AYIRICI_RE = re.compile(r"[_\-.]+")


def _dosya_dali_ikincil_ipucu(kok):
    """Görev C(1) KUCUK-düzeltme — `_oa/dosya.md`'deki dal satırı boş/yer-
    tutucu kaldığında dal tahmini tamamen ÖLMESİN diye İKİNCİL (yalnız İPUCU
    düzeyinde) iki kaynak daha dener: (a) dava kökü klasör adı, (b)
    `_oa/dosya.md`'nin TAMAMI (yalnız dal satırı değil) içindeki mahkeme adı
    kalıpları. Belirsizse None (uyarı hiç üretilmez — kural korunur). ASLA
    istisna fırlatmaz."""
    parcalar = []
    try:
        parcalar.append(os.path.basename(os.path.abspath(kok or ".")))
    except Exception:
        pass
    dosya_yol = os.path.join(kok or ".", "_oa", "dosya.md")
    if os.path.isfile(dosya_yol):
        try:
            with open(dosya_yol, encoding="utf-8", errors="replace") as f:
                parcalar.append(f.read())
        except OSError:
            pass
    metin = "\n".join(parcalar)
    if not metin:
        return None
    metin = _NORMALIZE_AYIRICI_RE.sub(" ", metin)
    if _MAHKEME_CEZA_RE.search(metin):
        return "ceza"
    if _MAHKEME_HUKUK_RE.search(metin):
        return "hukuk"
    return None


def _dosya_md_dal_metni(kok):
    """`_oa/dosya.md` içindeki 'Dokunduğu hukuk dalları:' satırının değerini
    döndürür (dosya yok/satır yok/doldurulmamışsa None). Bu, fiziken var olan
    bir dosyadaki sabit bir satırdır — yine de yalnız İPUCU sayılır (kesin
    hüküm ceza_dali alanınındır)."""
    dosya_yol = os.path.join(kok or ".", "_oa", "dosya.md")
    if not os.path.isfile(dosya_yol):
        return None
    try:
        with open(dosya_yol, encoding="utf-8", errors="replace") as f:
            icerik = f.read()
    except OSError:
        return None
    m = _DOSYA_MD_DAL_RE.search(icerik)
    if not m:
        return None
    deger = m.group(1).strip()
    if not deger or deger.lower().lstrip("[").startswith("doldur"):
        return None
    return deger


def _dosya_dali_tahmin(kok, ceza_dali):
    """Döner: 'ceza' | 'hukuk' | None (belirsiz). `ceza_dali` (defterin
    --baslat --ceza alanı) VARSA kesindir. Yoksa `_oa/dosya.md`'deki dal
    satırı ipucu aranır; o da yoksa ÜÇÜNCÜL kaynağa (`_dosya_dali_ikincil_
    ipucu` — klasör adı / mahkeme adı) düşülür; hiçbiri açık bir işaret
    vermiyorsa None (UYARI hiç üretilmez)."""
    if ceza_dali:
        return "ceza"
    metin = _dosya_md_dal_metni(kok)
    if metin:
        if _CEZA_KELIME_RE.search(metin):
            return "ceza"
        if _HUKUK_DAL_KELIME_RE.search(metin):
            return "hukuk"
    return _dosya_dali_ikincil_ipucu(kok)


def _dal_uyusmazlik_tek(dal, ad):
    """(dal, parça/katman adı) → mesaj|None — GÖREV C(1) çekirdek eşleşmesi."""
    if dal == "hukuk" and ad in CEZA_KATMAN_ADLARI:
        return (f"'{ad}' bir CEZA parçasıdır ama dosya HUKUK davası gibi görünüyor "
                "(ceza_dali yok + _oa/dosya.md dalı hukuk) — yanlış dosyada mı "
                "çalışılıyor, kontrol et.")
    if dal == "ceza" and ad in HUKUK_OZEL_PARCA_ADLARI:
        return (f"'{ad}' bir HUKUK/ÖZEL parçasıdır ama dosya CEZA dosyası gibi "
                "görünüyor — yanlış dosyada mı çalışılıyor, kontrol et.")
    return None


_DAL_UYARI_ATLA_DURUMLARI = (None, "BEKLIYOR", "GEREKSIZ")


def _dal_uyusmazlik_uyarilari(kok, d):
    """`d` (derlenmiş defter durumu) içindeki BEKLIYOR-OLMAYAN her adım/katman
    kaydını tarar, dal-uyumsuz olanları 'DAL UYUŞMAZLIĞI: ...' önekiyle
    listeler (--denetle/--goster/DURUM.md burada AYNI listeyi kullanır — tek
    kaynak). Dal belirsizse boş liste döner.

    KUCUK-DÜZELTME (hakem düzeltme turu 1, madde 2/bulgu 2): GEREKSIZ de
    atlama kümesine eklendi — bir hukuk dosyasında oa-mudafii/oa-musteki-
    vekili'ni (veya tersini) GEREKSIZ işaretlemek tam da BEKLENEN davranıştır,
    bunu 'yanlış dosyada mı çalışılıyor' diye uyarmak gürültü üretir ve
    gerçek uyarıyı bastırır."""
    dal = _dosya_dali_tahmin(kok, (d or {}).get("ceza_dali"))
    if dal is None:
        return []
    uyarilar = []
    for k, p in ((d or {}).get("katmanlar") or {}).items():
        if (p or {}).get("durum") in _DAL_UYARI_ATLA_DURUMLARI:
            continue
        mesaj = _dal_uyusmazlik_tek(dal, k)
        if mesaj:
            uyarilar.append(f"DAL UYUŞMAZLIĞI (katman {k}): {mesaj}")
    adimlar = (d or {}).get("adimlar") or {}
    for no in sorted(adimlar, key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
        a = adimlar[no]
        for parca, p in (a.get("parcalar") or {}).items():
            if (p or {}).get("durum") in _DAL_UYARI_ATLA_DURUMLARI:
                continue
            mesaj = _dal_uyusmazlik_tek(dal, parca)
            if mesaj:
                uyarilar.append(f"DAL UYUŞMAZLIĞI (adım {no} / {parca}): {mesaj}")
    return uyarilar


# ── GÖREV C(2) — ARTEFAKT-BEYAN AYRIMI (kendine-atıf kalıbı) ────────────────
# Önkoşul kontrolünde fiziksel artefakt bulunamadığında, kanıt metninde
# "taslağın X bölümünde" gibi KENDİNE-ATIF bir kalıp varsa (artefakt yerine
# dilekçenin/taslağın kendi bir bölümü gösterilmiş) bu ÖZEL OLARAK adlandırılır
# — saha bulgusu B4'ün tam olarak yakaladığı kaçış. Bloklama kümesi (5 ve 9)
# DEĞİŞMEZ; bu yalnız mesajı zenginleştirir (advisory metin katkısı).
_KENDINE_ATIF_RE = re.compile(
    r"(taslağ|taslak|dilekçe|dilekce)\w*.{0,60}?(bölüm|bolum|kısm|kısım|kisim)\w*",
    re.I)


def _kendine_atif_var_mi(kanit):
    return bool(kanit and _KENDINE_ATIF_RE.search(kanit))


_KENDINE_ATIF_NOTU = (" [KENDİNE-ATIF: kanıt metninde artefakt yerine dilekçe/taslak "
                       "bölümü gösterilmiş — ayrı çalışma evrakı bekleniyor.]")


def _govde_saglam_mi(yol, min_govde=MIN_GOVDE):
    """Dosya VAR + boşluk-hariç içerik >= min_govde karakter mi? ('boş/iskelet
    artefakt' kaçağını kapatır.)"""
    try:
        if not os.path.isfile(yol):
            return False
        with open(yol, encoding="utf-8", errors="replace") as f:
            icerik = f.read()
    except OSError:
        return False
    return len(re.sub(r"\s+", "", icerik)) >= min_govde


def _glob_saglam(desen):
    """Desenle eşleşen VE gövdesi sağlam olan İLK dosyanın yolunu döndürür,
    yoksa None (sıralı — deterministik)."""
    import glob as _glob
    for yol in sorted(_glob.glob(desen)):
        if _govde_saglam_mi(yol):
            return yol
    return None


def _kiyas_onkosul_saglam_mi(kok):
    cikti = os.path.join(kok or ".", "_oa", "cikti")
    kiyas = _glob_saglam(os.path.join(cikti, "05-kiyas*"))
    muhakeme = _glob_saglam(os.path.join(cikti, "*ictihat-muhakeme*"))
    if kiyas and muhakeme:
        return True, None
    eksik = []
    if not kiyas:
        eksik.append("_oa/cikti/05-kiyas* yok/boş")
    if not muhakeme:
        eksik.append("_oa/cikti/*ictihat-muhakeme* yok/boş (P0-2 tek-komutunu koş)")
    return False, " ; ".join(eksik)


def _sha256_dosya(yol):
    import hashlib
    h = hashlib.sha256()
    try:
        with open(yol, "rb") as f:
            for blok in iter(lambda: f.read(65536), b""):
                h.update(blok)
    except OSError:
        return None
    return h.hexdigest()


def _makbuz_oku(kok):
    """(makbuz:dict|None, hata:str|None) — _oa/defter/teslim-makbuz.json."""
    yol = os.path.join(kok or ".", "_oa", "defter", "teslim-makbuz.json")
    if not os.path.isfile(yol):
        return None, "_oa/defter/teslim-makbuz.json yok"
    try:
        with open(yol, encoding="utf-8") as f:
            m = json.load(f)
    except Exception as e:
        return None, f"teslim-makbuz.json okunamadı/bozuk ({e})"
    if not isinstance(m, dict):
        return None, "teslim-makbuz.json geçersiz biçimde"
    return m, None


def _makbuz_onkosul_saglam_mi(kok):
    """P0-5 DÜZELTME(a) sinav-turu — makbuzu FİİLEN TESLİM EDİLEN DOSYAYA bağlar:
    yalnız exit_kodu==0 yetmez, (1) makbuzdaki taslak diskte VAR olmalı VE
    güncel sha256'sı makbuzdaki kayıtlı sha ile EŞLEŞMELİDİR (sonradan taslağın
    elden değiştirilmesi bu kapıyı artık atlatamaz — `_makbuz_denetim_hesapla`
    ile AYNI mantık, burada da uygulanır); (2) `_oa/cikti`'daki EN YENİ
    dilekçe-şekilli dosya makbuzdaki taslakla AYNI OLMALIDIR — aksi hâlde
    BAŞKA (bayat/yanlış) bir dosya için üretilmiş makbuz, ad ne olursa olsun
    tamamen FARKLI, hiç teslim edilmemiş bir dilekçeyi adım-9 UYGULANDI için
    yetkilendirebilirdi (saha bulgusu: 'ad değiştirip kapıdan kaçma')."""
    m, hata = _makbuz_oku(kok)
    if m is None:
        return False, hata
    if m.get("exit_kodu") != 0:
        return False, "teslim-makbuz.json exit_kodu != 0 (son teslim başarısız/RED)"
    taslak = m.get("taslak_yol")
    sha_kayitli = m.get("taslak_sha256")
    if taslak and sha_kayitli:
        if not os.path.isfile(taslak):
            return False, f"teslim-makbuz.json'daki taslak artık diskte yok: {taslak}"
        guncel = _sha256_dosya(taslak)
        if guncel != sha_kayitli:
            return False, ("teslim-makbuz.json'daki taslak SONRADAN DEĞİŞTİRİLMİŞ "
                           f"(sha uyumsuz) — {taslak} (teslim_paketi.py'yi yeniden koş).")
    dilekce_uyari = _dilekce_sekilli_makbuzsuz_uyarisi(kok)
    if dilekce_uyari:
        return False, dilekce_uyari
    return True, None


_ONKOSUL_FONK = {
    (5, "oa-kiyas"): _kiyas_onkosul_saglam_mi,
    (9, "oa-kontrol"): _makbuz_onkosul_saglam_mi,
}


def _ingest_once_saglam_mi(kok):
    """İNGEST-ÖNCE (kullanıcı ilkesi): adım 1+ UYGULANDI, '_oa/metin/00-kunye.
    json' diskte YOKSA yazılamaz — evrak hiç ingest edilmeden pipeline
    adımları ilerleyemez."""
    return os.path.isfile(os.path.join(kok or ".", "_oa", "metin", "00-kunye.json"))


def _kismi_ingest_durumu(kok):
    """P1-9 KUCUK-DÜZELTME (sinav bulgusu) — (kismi:bool, n, m): `_oa/metin-
    onbakis/00-kunye.onbakis.json` VARKEN ve ana `_oa/metin/00-kunye.json`
    YOK/eksikken bu kök yalnız KISMİ (--onbakis) bir taramadan geçmiştir.
    İNGEST-ÖNCE kapısı --serh ile GEÇİLEBİLİR (≥30 kr gerekçe) — bu durumda
    kısmi-okuma gerçeği MODELİN kendi yazdığı şerh metnine bağlı kalmasın diye
    TEK KAYNAKTAN (bu fonksiyon) okunup şerh metnine + teslim makbuzuna +
    dosya-analiz.md başlığına deterministik olarak taşınır (bkz. çağıranlar).
    Kısmi durum YOKSA (False, None, None)."""
    ana_kunye = os.path.join(kok or ".", "_oa", "metin", "00-kunye.json")
    ob_kunye_yol = os.path.join(kok or ".", "_oa", "metin-onbakis", "00-kunye.onbakis.json")
    if os.path.isfile(ana_kunye) or not os.path.isfile(ob_kunye_yol):
        return False, None, None
    try:
        with open(ob_kunye_yol, encoding="utf-8") as f:
            ob = json.load(f)
    except Exception:
        return True, None, None
    if not isinstance(ob, dict):
        return True, None, None
    n = ob.get("toplam_evrak")
    m = ob.get("onbakis_toplam_kaynak")
    return True, n, m


def _onkosul_uyari_var_mi(kok, anahtar):
    if anahtar == (3, "oa-ictihat"):
        kutuk = os.path.join(kok or ".", "_oa", "teyit", "kunye-teyit.md")
        dokum = os.path.join(kok or ".", "_oa", "teyit", "dokum")
        kutuk_var = os.path.isfile(kutuk) and os.path.getsize(kutuk) > 0
        dokum_var = os.path.isdir(dokum) and any(True for _ in os.scandir(dokum))
        return kutuk_var or dokum_var
    desen_map = {(4, "oa-vakia"): "04-vakia*", (6, "oa-strateji"): "06-strateji*",
                 (7, "oa-antitez"): "07-antitez*"}
    desen = desen_map.get(anahtar)
    if not desen:
        return True
    import glob as _glob
    return bool(_glob.glob(os.path.join(kok or ".", "_oa", "cikti", desen)))


def _adim_artefakt_var_mi(kok, adim, parca):
    """Görev A — bir (adım,parça) için FİZİKSEL artefakt tanımı VARSA sorar,
    YOKSA None döner (bilinmiyor). DURUM.md dört-hâl sınıflandırmasının
    (beyan+artefakt / beyan var-artefakt yok / artefakt var-beyan yok / ikisi
    de yok) tek kaynağı — mevcut ONKOSUL_BLOKLEYICI/ONKOSUL_UYARI tanımlarını
    (P0-6) TEKRARLAMAZ, TÜRETİR (ikiz-liste yasağı). Yalnız SORGULAR —
    BLOKLAMAZ (kapı zaten `_onkosul_kontrol` içinde ayrı çalışır)."""
    anahtar = (adim, parca)
    if anahtar in ONKOSUL_BLOKLEYICI:
        fonk = _ONKOSUL_FONK.get(anahtar)
        if fonk is None:
            return None
        tamam, _eksik = fonk(kok)
        return bool(tamam)
    if anahtar in ONKOSUL_UYARI:
        return bool(_onkosul_uyari_var_mi(kok, anahtar))
    return None


def _adim_artefakt_eksik_metni(kok, adim, parca):
    """KUCUK-DÜZELTME (hakem düzeltme turu 1, madde 2/bulgu 3) — `_adim_
    artefakt_var_mi` FALSE dönerken HANGİ ayağın eksik olduğunu (05-kiyas*
    mi, muhakeme kaydı mı, teslim makbuzu mu, ...) metne çevirir; DURUM.md'nin
    '[FİZİKSEL: beyan VAR / artefakt YOK]' etiketi tek başına hangi dosyanın
    arandığını söylemiyordu (avukat mevcut dosyaları görüp etiketi 'yanlış'
    sanabiliyordu). TEK KAYNAKTAN (_ONKOSUL_FONK / ONKOSUL_UYARI, ikiz-liste
    yasağı) okur. Tanımsız/bulunamazsa None (çağıran bu durumda ek metin
    basmaz)."""
    anahtar = (adim, parca)
    fonk = _ONKOSUL_FONK.get(anahtar)
    if fonk is not None:
        _tamam, eksik = fonk(kok)
        return eksik
    return ONKOSUL_UYARI.get(anahtar)


def _fiziksel_hal(beyan_var, artefakt_var):
    """Dört hâlden birini metne çevirir; `artefakt_var` None ise (bu adım için
    artefakt tanımı yok) None döner — çağıran bu durumda satırı basmaz."""
    if artefakt_var is None:
        return None
    if beyan_var and artefakt_var:
        return "beyan+artefakt"
    if beyan_var and not artefakt_var:
        return "beyan VAR / artefakt YOK ⚠"
    if not beyan_var and artefakt_var:
        return "artefakt VAR / beyan YOK ⚠"
    return "ikisi de yok"


def _dokum_muhakeme_makbuz_sayaclari(kok):
    """Görev A — DURUM.md'nin 'Döküm / Muhakeme / Makbuz Sayaçları' bölümünün
    kaynağı: (a) `_oa/teyit/dokum/` içindeki dosya sayısı, (b) `_oa/cikti/
    *ictihat-muhakeme*` eşleşen dosya sayısı, (c) teslim makbuzu durumu
    (yok / var+exit_kodu / RED). Salt-okur, hiçbir şeyi BLOKLAMAZ."""
    kok = kok or "."
    dokum_dizin = os.path.join(kok, "_oa", "teyit", "dokum")
    dokum_n = 0
    if os.path.isdir(dokum_dizin):
        try:
            dokum_n = sum(1 for e in os.scandir(dokum_dizin) if e.is_file())
        except OSError:
            dokum_n = 0
    muhakeme_dosyalar = sorted(glob.glob(os.path.join(kok, "_oa", "cikti", "*ictihat-muhakeme*")))
    makbuz_yol = os.path.join(kok, "_oa", "defter", "teslim-makbuz.json")
    makbuz_red_yol = os.path.join(kok, "_oa", "defter", "teslim-makbuz-RED.json")
    if os.path.isfile(makbuz_yol):
        try:
            with open(makbuz_yol, encoding="utf-8") as f:
                m = json.load(f)
            makbuz_durum = f"VAR (exit_kodu={m.get('exit_kodu')})"
        except Exception:
            makbuz_durum = "VAR (okunamadı/bozuk)"
    elif os.path.isfile(makbuz_red_yol):
        makbuz_durum = "RED VAR (başarısız teslim denemesi)"
    else:
        makbuz_durum = "YOK"
    return dokum_n, len(muhakeme_dosyalar), makbuz_durum


def _onkosul_kontrol(kok, adim, parca, serh, mevcut_d=None, kanit=None):
    """P0-6 — bir (adım,parça) UYGULANDI yazılmadan ÖNCE fiziksel artefaktı
    sorgular. Döner: (izin:bool, sorun:str|None, uyari:str|None, serh_mesaj:str|False)
    — `serh_mesaj` GERÇEK bir dize İSE bu çağrı şerh ile geçildi demektir
    (`isle()` bunu olaya `serh:true`/`serh_metni` olarak işler); aksi hâlde
    `False`. `mevcut_d` — bu olay eklenmeden ÖNCEKİ derlenmiş defter durumu
    (`derle()` çıktısı); yalnız ÇAPRAZ-ADIM kontrolünde (adım-8) kullanılır.
    `serh` GEREKÇELİ (>=SERH_GEREKCE_MIN karakter) verilmişse BLOKLEYICI küme
    (ve İNGEST-ÖNCE) dahi GEÇİLİR — sessiz değil, olay 'serh:true' ile
    İŞLENİR (--denetle/--goster HER ZAMAN '⚠ ŞERHLİ UYGULANDI' basar).
    `kanit` — GÖREV C(2): artefakt bulunamayan (BLOKLEYICI/UYARI) dallarda,
    kanıt metni KENDİNE-ATIF bir kalıp taşıyorsa (bkz. `_kendine_atif_var_mi`)
    ilgili sorun/uyarı metni `_KENDINE_ATIF_NOTU` ile zenginleştirilir —
    BLOKLAMA KÜMESİ DEĞİŞMEZ, yalnız mesaj netleşir."""
    serh_gecerli = bool(serh and len(serh.strip()) >= SERH_GEREKCE_MIN)
    try:
        adim_i = int(adim)
    except (TypeError, ValueError):
        adim_i = None

    if adim_i is not None and adim_i >= 1 and not _ingest_once_saglam_mi(kok):
        sorun = ("İNGEST-ÖNCE: _oa/metin/00-kunye.json yok — evrak hiç ingest "
                 f"edilmeden adım {adim} UYGULANDI yazılamaz (önce oa_ingest koş).")
        if serh_gecerli:
            # P1-9 KUCUK-DÜZELTME (sinav bulgusu) — kısmi-okuma gerçeği (--onbakis
            # ile geçilen İNGEST-ÖNCE) modelin kendi yazdığı şerh METNİNE değil,
            # DETERMİNİSTİK bir ön-eke bağlanır: "KISMI INGEST: N/M" HER ZAMAN
            # görünür, model şerhinde bunu anmayı unutsa/atlasa BİLE.
            kismi, n, m = _kismi_ingest_durumu(kok)
            onek = f"KISMI INGEST: {n}/{m} — " if kismi and n is not None and m is not None else ""
            return True, None, None, (onek + "İNGEST-ÖNCE ŞERH ile geçildi: " + sorun)
        return False, sorun, None, False

    # P1-10 — CANLI-SENKRON KAPISI: tam_tur akışı kullanılıyorsa (dosya-analiz.
    # json var) working-memory bayatken yeni bir UYGULANDI yazılamaz.
    if adim_i is not None and adim_i >= 1:
        senkron_sorun = _canli_senkron_bayat_mi(kok)
        if senkron_sorun:
            if serh_gecerli:
                return True, None, None, ("CANLI-SENKRON ŞERH ile geçildi: " + senkron_sorun)
            return False, senkron_sorun, None, False

    anahtar = (adim_i, parca)

    # ÇAPRAZ-ADIM kontrolü: adım-8 (YAZIM/oa-dilekce) UYGULANDI iken adım-5
    # (KIYAS/oa-kiyas) hâlâ BEKLIYORSA — kıyas hiç değerlendirilmeden (ne
    # UYGULANDI ne GEREKSIZ denmeden) yazım adımına geçilmiş demektir; saha
    # bulgusu tam olarak bu sızmadır. GEREKSIZ/BILGI-EKSIK/YUKLENEMEDI dahi
    # yeterlidir (bilinçli bir karar var demektir) — yalnız BEKLIYOR (hiç
    # değerlendirilmemiş) reddedilir.
    if anahtar == (8, "oa-dilekce") and mevcut_d is not None:
        adim5 = (mevcut_d.get("adimlar", {}).get("5", {}).get("parcalar", {}) or {}).get("oa-kiyas")
        adim5_durum = (adim5 or {}).get("durum", "BEKLIYOR")
        if adim5_durum == "BEKLIYOR":
            sorun = ("adım-8 (YAZIM/oa-dilekce) UYGULANDI ama adım-5 (KIYAS/oa-kiyas) "
                     "hâlâ BEKLIYOR — kıyas hiç değerlendirilmeden (UYGULANDI/GEREKSIZ "
                     "dahi denmeden) yazım adımına geçilemez.")
            if serh_gecerli:
                return True, None, None, ("ŞERH ile geçildi: " + sorun)
            return False, sorun, None, False

    if anahtar in ONKOSUL_BLOKLEYICI:
        fonk = _ONKOSUL_FONK[anahtar]
        tamam, eksik = fonk(kok)
        if not tamam:
            sorun = ONKOSUL_BLOKLEYICI[anahtar] + " Eksik: " + (eksik or "?")
            if _kendine_atif_var_mi(kanit):
                sorun += _KENDINE_ATIF_NOTU
            if serh_gecerli:
                return True, None, None, ("ŞERH ile geçildi: " + sorun)
            return False, sorun, None, False

    if anahtar in ONKOSUL_UYARI and not _onkosul_uyari_var_mi(kok, anahtar):
        uyari_mesaj = ONKOSUL_UYARI[anahtar]
        if _kendine_atif_var_mi(kanit):
            uyari_mesaj += _KENDINE_ATIF_NOTU
        return True, None, uyari_mesaj, False

    return True, None, None, False


def simdi():
    return datetime.datetime.now().isoformat(timespec="seconds")


# --- yol çözümleme (--kok / --yol) -------------------------------------------
def _yollar(args):
    """(olaylar_jsonl, durum_json) döndür. Öncelik: açık --yol (geriye uyum:
    doğrudan durum.json yolu; jsonl aynı klasörde). Yoksa --kok/_oa/defter."""
    if getattr(args, "yol", None):
        durum_yol = args.yol
        defter = os.path.dirname(durum_yol) or "."
    else:
        defter = os.path.normpath(os.path.join(getattr(args, "kok", None) or ".",
                                               "_oa", "defter"))
        durum_yol = os.path.join(defter, DURUM_ADI)
    olaylar_yol = os.path.join(defter, OLAYLAR_ADI)
    return olaylar_yol, durum_yol


# --- append-only olay defteri (atomik) ---------------------------------------
def olay_ekle(olaylar_yol, olay):
    """Tek satırlık olayı jsonl'e ATOMİK ekle. Dosya asla oku-değiştir-yaz
    edilmez; yalnız kendi satırımız eklenir → eşzamanlı yazımlarda kimsenin
    kaydı silinemez. Tek os.write (POSIX'te PIPE_BUF altı atomik) + en iyi çaba
    kilit (POSIX fcntl / Windows msvcrt) ile yazımlar serileştirilir."""
    ust = os.path.dirname(olaylar_yol)
    if ust:
        os.makedirs(ust, exist_ok=True)
    ham = (json.dumps(olay, ensure_ascii=False) + "\n").encode("utf-8")
    fd = os.open(olaylar_yol, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    kilit = None
    try:
        try:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX); kilit = "fcntl"
        except Exception:
            try:
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1); kilit = "msvcrt"
            except Exception:
                kilit = None  # kilit yoksa tek-write atomikliğine güven
        os.write(fd, ham)
    finally:
        try:
            if kilit == "fcntl":
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
            elif kilit == "msvcrt":
                import msvcrt
                os.lseek(fd, 0, os.SEEK_SET)  # kilit 0. bayttaydı; oraya dön
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except Exception:
            pass  # her hâlde os.close tüm kilitleri bırakır
        os.close(fd)


def olaylari_oku(olaylar_yol):
    """jsonl'i satır satır oku. Bozuk/yarım satır (çok nadir eşzamanlı yazımda)
    atlanır; kalan olaylar yine derlenir (dayanıklılık)."""
    olaylar = []
    if not (os.path.exists(olaylar_yol) and os.path.getsize(olaylar_yol) > 0):
        return olaylar
    with open(olaylar_yol, encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if not satir:
                continue
            try:
                olaylar.append(json.loads(satir))
            except json.JSONDecodeError:
                continue
    return olaylar


# --- durum derleme (olaylardan) ----------------------------------------------
def _iskelet(dosya, olusturma, ceza_dali):
    d = {"dosya": dosya, "olusturma": olusturma, "ceza_dali": ceza_dali,
         "adimlar": {}, "katmanlar": {}, "gunluk": [], "arac_hatalari": []}
    for no, (ad, parcalar) in ADIMLAR.items():
        d["adimlar"][str(no)] = {
            "ad": ad,
            "parcalar": {p: {"durum": "BEKLIYOR", "kanit": None, "zaman": None, "pas_yolu": None}
                         for p in parcalar},
        }
    katmanlar = list(KATMANLAR)
    if ceza_dali:
        katmanlar.append("oa-mudafii" if ceza_dali == "mudafii" else "oa-musteki-vekili")
    for k in katmanlar:
        d["katmanlar"][k] = {"durum": "BEKLIYOR", "kanit": None, "zaman": None}
    return d


def _uygula_adim(d, o, sira=None):
    """`sira` (YENİ-3, Paket D DÜZELTME) — append-only defterdeki MONOTON olay
    indeksi; bu parçanın EN SON güncellemesinin defter sırasını taşır.
    `_avukat_karari_cozulmus_mu` beraberliksiz kıyas için bunu kullanır (saniye
    çözünürlüklü `zaman` yerine)."""
    no = str(o.get("adim"))
    a = d["adimlar"].get(no)
    if a is None:
        try:
            ad = ADIMLAR[int(no)][0]
        except Exception:
            ad = f"ADIM-{no}"
        a = d["adimlar"][no] = {"ad": ad, "parcalar": {}}
    parca = o.get("parca")
    if parca not in a["parcalar"]:
        a["parcalar"][parca] = {"durum": "BEKLIYOR", "kanit": None, "zaman": None, "pas_yolu": None}
    guncelleme = {"durum": o.get("durum"), "kanit": o.get("kanit"),
                  "zaman": o.get("zaman"), "serh": bool(o.get("serh")),
                  "serh_metni": o.get("serh_metni"), "_sira": sira,
                  "arac_imzali": _olay_arac_imzali_mi(o)}
    if o.get("pas_yolu"):
        guncelleme["pas_yolu"] = o.get("pas_yolu")  # M1 PAS PROTOKOLÜ — verilmemişse ESKİ değer KORUNUR
    a["parcalar"][parca].update(guncelleme)
    d["gunluk"].append({"zaman": o.get("zaman"), "adim": o.get("adim"),
                        "parca": parca, "durum": o.get("durum"),
                        "pas_yolu": o.get("pas_yolu")})
    if o.get("surum"):
        d.setdefault("surum_gorulen", []).append(o.get("surum"))


def _uygula_katman(d, o, sira=None):
    k = o.get("katman")
    if k not in d["katmanlar"]:
        d["katmanlar"][k] = {"durum": "BEKLIYOR", "kanit": None, "zaman": None}
    d["katmanlar"][k].update({"durum": o.get("durum"), "kanit": o.get("kanit"),
                              "zaman": o.get("zaman"), "_sira": sira,
                              "arac_imzali": _olay_arac_imzali_mi(o)})
    d["gunluk"].append({"zaman": o.get("zaman"), "katman": k, "durum": o.get("durum")})
    if o.get("surum"):
        d.setdefault("surum_gorulen", []).append(o.get("surum"))


def son_pas_yolu(d):
    """M1 PAS PROTOKOLÜ (Paket D) — `gunluk`daki (zaman sıralı, append-only)
    EN SON `pas_yolu` taşıyan olayı döndürür (yoksa None). `ajan-brif` bunu
    çağırıp bir SONRAKİ parçaya ÖNCEKİ PAS olarak 1. sıradan enjekte eder —
    'devir paketi' okumaktan daha ucuz/deterministik bir yol: pas zaten
    `_oa/cikti/`de fiziken duran bir dosyadır, bu fonksiyon yalnız ONUN
    YOLUNU söyler (içeriği KENDİSİ okumaz — tek-yazar/kayıpsızlık ihlali
    olmaz, dosya `_oa/cikti/`de kalır)."""
    for kayit in reversed((d or {}).get("gunluk") or []):
        if kayit.get("pas_yolu"):
            return kayit["pas_yolu"]
    return None


def _surum_v055_var_mi(d, kok=None):
    """P0-5 geçiş supabı: bu defterde HİÇ v0.5.5+ olay VAR mı? (bkz. OA_SURUM
    modül-üstü not — makbuz denetimleri yalnız bu True iken blokleyicidir.)
    Eşik `_MAKBUZ_CAG_ESIGI`dir, güncel sürüm DEĞİL — bkz. o sabitin notu.

    DÜZELTME (turu 2, YENİ-1): `surum_gorulen` TAMAMEN boşsa (defter hiç bu
    CLI'den geçmemiş, tümüyle elle yazılmış olabilir) tek başına "eski
    defter" sonucuna sıçramaz — iki bağımsız İKİNCİL KANIT dener (bkz.
    `_MAKBUZ_CAG_TARIHI` üstündeki not): defterin ilk olayı çağ tarihinden
    sonraysa, ya da kökte yalnız v0.5.5-ailesinin üretebileceği bir artefakt
    varsa, defter yine ÇAĞ-İÇİ sayılır. `kok` verilmezse (bazı çağrı yerleri
    yalnız `d` ile çalışır) yalnız zaman-damgası kanıtı denenir."""
    for s in (d or {}).get("surum_gorulen") or []:
        if _surum_tuple(s) >= _MAKBUZ_CAG_ESIGI:
            return True
    if not (d or {}).get("surum_gorulen"):
        ilk_zaman = _ilk_olay_zamani(d)
        if ilk_zaman and str(ilk_zaman) >= _MAKBUZ_CAG_TARIHI:
            return True
        if kok is not None and _defter_v055_artefakti_var_mi(kok):
            return True
    return False


def _uygula_arac_hata(d, o):
    """D5 — 'ARAÇ ÇÖKTÜ' olayını GÖRÜNÜR bir listeye ekler (asla üzerine yazılmaz,
    append-only). Bir MCP/araç çöküşü sessizce kaybolmasın diye ayrı bir kova."""
    d.setdefault("arac_hatalari", []).append({
        "zaman": o.get("zaman"), "arac": o.get("arac"), "sorgu": o.get("sorgu"),
        "hata": o.get("hata"), "adim": o.get("adim"), "parca": o.get("parca"),
    })
    d["gunluk"].append({"zaman": o.get("zaman"), "arac_hatasi": o.get("arac"),
                        "hata": o.get("hata")})


def _uygula_avukat_karari(d, o, sira=None):
    """M7 (Paket D, v0.5.5) — AVUKAT KARARI BEKLEYEN'in ÇÖZÜM olayı: bir
    çatal (BİLGİ-EKSİK/ŞERHLİ UYGULANDI kalemi) için avukat NİHAİ kararını
    KALICI olarak işler (append-only — önceki BEKLEYEN kaydı SİLİNMEZ,
    yalnız 'çözüldü' sayılır; kayıpsızlık invaryantı: geçmiş görünür kalır).
    `sira` (YENİ-3, Paket D DÜZELTME) — append-only defterdeki MONOTON olay
    indeksi; `_avukat_karari_cozulmus_mu` bunu zaman damgası yerine kullanır."""
    d.setdefault("avukat_kararlari", []).append({
        "zaman": o.get("zaman"), "adim": o.get("adim"), "parca": o.get("parca"),
        "katman": o.get("katman"), "karar": o.get("karar"), "gerekce": o.get("gerekce"),
        "_sira": sira,
    })
    d["gunluk"].append({"zaman": o.get("zaman"), "avukat_karari": o.get("karar"),
                        "adim": o.get("adim"), "parca": o.get("parca"), "katman": o.get("katman")})


def _zaman_once_mi(erken, gec):
    """erken < gec (KESİN ÖNCE) ise True. YENİ-3 (Paket D DÜZELTME) —
    beraberlik (`erken == gec`) artık 'önce' SAYILMAZ: `simdi()` saniye
    çözünürlüklü olduğundan iki ayrı ardışık CLI çağrısı kolayca AYNI damgayı
    alabilir; eskiden `<=` ile beraberlik 'karar sonra geldi' sayılıyor,
    bu da belirsizlikte kalemi SESSİZCE gizliyordu (fail-OPEN). Bu yalnız
    GERİYE DÖNÜK UYUM yoludur (`_sira` yoksa) — birincil kıyas artık append-
    only defterin SIRASIDIR (bkz. `_avukat_karari_cozulmus_mu`). Ayrıştırılamazsa
    (bilinmeyen biçim) yine FAIL-CLOSED: 'önce DEĞİL' döner."""
    if not erken or not gec:
        return False
    try:
        return (datetime.datetime.fromisoformat(erken)
                < datetime.datetime.fromisoformat(gec))
    except Exception:
        return False


def _avukat_karari_cozulmus_mu(kararlar, adim=None, parca=None, katman=None, zaman=None, sira=None):
    """M7 düzeltmesi (Paket D sınav bulgusu, YENİ-3 ile GÜÇLENDİRİLDİ) —
    eşleşme TEK BAŞINA yetmez: kararın, çözdüğünü iddia ettiği parça/katman
    kaydından GERÇEKTEN SONRA gelmiş olması gerekir. Gerçeğin kaynağı SANİYE
    çözünürlüklü bir zaman damgası DEĞİL, append-only defterin SIRASIdır
    (`_sira`, monoton artan olay indeksi — beraberlik YAPISAL OLARAK
    İMKÂNSIZDIR). `sira` verilmişse VE karar kaydı da bir `_sira` taşıyorsa
    kıyas SIRAYLA yapılır, `zaman` o kayıt için HİÇ kullanılmaz. `sira`
    verilmemişse veya karar eski (bu düzeltmeden önce yazılmış, `_sira`sız)
    ise geriye dönük uyum için `zaman` kıyasına düşülür — ve orada da artık
    beraberlik FAIL-CLOSED'tır (bkz. `_zaman_once_mi`, KESİN ÖNCE). Aksi
    hâlde bir karardan SONRA düşülen YENİ ve İLGİSİZ bir BİLGİ-EKSİK/ŞERHLİ
    kaydı, eski kararın gölgesinde SESSİZCE bastırılır (Paket D M7 çürütücü
    bulgusu; YENİ-3 bunun aynı-saniye beraberliğine daralmış tekrarını
    kapatır)."""
    for k in kararlar or []:
        if katman is not None:
            eslesir = (k.get("katman") == katman)
        else:
            eslesir = (str(k.get("adim")) == str(adim) and k.get("parca") == parca)
        if not eslesir:
            continue
        k_sira = k.get("_sira")
        if sira is not None and k_sira is not None:
            if k_sira <= sira:
                continue  # karar bu kalemden ÖNCE/AYNI ANDA düşmüş — çözemez
            return True
        if zaman is not None and not _zaman_once_mi(zaman, k.get("zaman")):
            continue
        return True
    return False


def _migrasyon(olaylar_yol, durum_yol):
    """jsonl yoksa/boşsa ama eski (türev-öncesi) pipeline-durum.json varsa,
    durumu olaylara BİR KEZ taşı. jsonl doluysa hiçbir şey yapmaz."""
    if os.path.exists(olaylar_yol) and os.path.getsize(olaylar_yol) > 0:
        return
    if not os.path.exists(durum_yol):
        return
    try:
        eski = json.load(open(durum_yol, encoding="utf-8"))
    except Exception:
        return
    if not isinstance(eski, dict) or "adimlar" not in eski:
        return
    baslat_olay = {"zaman": eski.get("olusturma") or simdi(), "tip": "baslat",
                   "dosya": eski.get("dosya"), "ceza_dali": eski.get("ceza_dali"),
                   "migrasyon": True}
    baslat_olay["imza"] = _imza_hesapla(baslat_olay)
    olay_ekle(olaylar_yol, baslat_olay)
    for no in sorted(eski.get("adimlar", {}),
                     key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
        a = eski["adimlar"][no]
        for parca, p in (a.get("parcalar") or {}).items():
            if isinstance(p, dict) and p.get("durum") and p["durum"] != "BEKLIYOR":
                adim_olay = {
                    "zaman": p.get("zaman") or simdi(), "tip": "adim",
                    "adim": int(no) if str(no).lstrip("-").isdigit() else no,
                    "parca": parca, "durum": p["durum"], "kanit": p.get("kanit"),
                    "migrasyon": True}
                adim_olay["imza"] = _imza_hesapla(adim_olay)
                olay_ekle(olaylar_yol, adim_olay)
    for k, p in (eski.get("katmanlar") or {}).items():
        if isinstance(p, dict) and p.get("durum") and p["durum"] != "BEKLIYOR":
            katman_olay = {
                "zaman": p.get("zaman") or simdi(), "tip": "katman",
                "katman": k, "durum": p["durum"], "kanit": p.get("kanit"),
                "migrasyon": True}
            katman_olay["imza"] = _imza_hesapla(katman_olay)
            olay_ekle(olaylar_yol, katman_olay)


def derle(olaylar_yol, durum_yol=None):
    """Olay defterinden durumu DERLE (gerçeğin kaynağı jsonl). durum_yol
    verilirse önce eski görünüm migrate edilir. Defter yoksa None döner."""
    if durum_yol is not None:
        _migrasyon(olaylar_yol, durum_yol)
    olaylar = olaylari_oku(olaylar_yol)
    if not olaylar:
        return None
    d = None
    # YENİ-3 (Paket D DÜZELTME) — `sira`: defterdeki (append-only, jsonl
    # satır sırası) MONOTON olay indeksi. `_avukat_karari_cozulmus_mu` bunu
    # saniye çözünürlüklü `zaman` YERİNE kullanır — beraberlik yapısal olarak
    # imkânsız hâle gelir (her satır benzersiz bir `sira` alır).
    for sira, o in enumerate(olaylar):
        tip = o.get("tip")
        if tip == "baslat":
            if d is None:
                d = _iskelet(o.get("dosya"), o.get("zaman"), o.get("ceza_dali"))
            elif o.get("dosya"):
                d["dosya"] = o["dosya"]  # sonraki baslat yalnız kimliği tazeler
        elif tip == "adim":
            if d is None:
                d = _iskelet(None, o.get("zaman"), None)
            _uygula_adim(d, o, sira)
        elif tip == "katman":
            if d is None:
                d = _iskelet(None, o.get("zaman"), None)
            _uygula_katman(d, o, sira)
        elif tip == "arac-hatasi":
            if d is None:
                d = _iskelet(None, o.get("zaman"), None)
            _uygula_arac_hata(d, o)
        elif tip == "avukat-karari":
            if d is None:
                d = _iskelet(None, o.get("zaman"), None)
            _uygula_avukat_karari(d, o, sira)
    return d


def _durum_yaz(durum_yol, d):
    """Türev görünümü ATOMİK yaz (tmp + os.replace). jsonl'den yeniden
    üretilebilir olduğundan bu dosyanın racy olması veri kaybı yaratmaz."""
    ust = os.path.dirname(durum_yol)
    if ust:
        os.makedirs(ust, exist_ok=True)
    tmp = f"{durum_yol}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(tmp, durum_yol)


# --- kanıt disiplini (değişmedi) ---------------------------------------------
def dogrula_statu(args):
    if args.durum not in STATULER:
        sys.exit(f"HATA: geçersiz durum '{args.durum}'. Geçerli: {sorted(STATULER)}")
    if args.durum == "UYGULANDI":
        if not args.kanit or len(args.kanit.strip()) < MIN_KANIT:
            sys.exit("RET: UYGULANDI kanıtsız yazılamaz. --kanit ile fiilî işlemi "
                     f"(çağrı/script/MCP: araç+sorgu+sonuç) en az {MIN_KANIT} karakterle belgele.")
        return args.kanit.strip()
    if args.durum == "GEREKSIZ":
        if not args.gerekce:
            sys.exit("RET: GEREKSIZ gerekçesiz yazılamaz (--gerekce).")
        return "GEREKÇE: " + args.gerekce.strip()
    if args.durum == "BILGI-EKSIK":
        if not args.eksik:
            sys.exit("RET: BILGI-EKSIK, eksik bilgi tanımlanmadan yazılamaz (--eksik).")
        return "EKSİK: " + args.eksik.strip()
    if args.durum == "YUKLENEMEDI":
        if not args.kanit:
            sys.exit("RET: YUKLENEMEDI açıklamasız yazılamaz (--kanit ile neden + elden nasıl yürütüldüğü).")
        return "YÜKLENEMEDİ: " + args.kanit.strip()


def _defter_var(olaylar_yol, durum_yol):
    """--baslat yapılmış mı? (migrasyon dahil) — --isle/--katman ön-koşulu."""
    _migrasyon(olaylar_yol, durum_yol)
    return os.path.exists(olaylar_yol) and os.path.getsize(olaylar_yol) > 0


# --- komutlar ----------------------------------------------------------------
def baslat(args):
    olaylar_yol, durum_yol = _yollar(args)
    ust = os.path.dirname(olaylar_yol)
    if ust:
        os.makedirs(ust, exist_ok=True)
    onceki = os.path.exists(olaylar_yol) and os.path.getsize(olaylar_yol) > 0
    olay = {"zaman": simdi(), "tip": "baslat", "dosya": args.baslat, "ceza_dali": args.ceza}
    olay["imza"] = _imza_hesapla(olay)
    # --baslat fan-out ÖNCESİ tek-aktörlü bir komuttur; defteri taze kurar.
    with open(olaylar_yol, "w", encoding="utf-8") as f:
        f.write(json.dumps(olay, ensure_ascii=False) + "\n")
    _durum_yaz(durum_yol, derle(olaylar_yol))
    print(f"Defter açıldı: {olaylar_yol} — dosya: {args.baslat}"
          + (f" (ceza dalı: {args.ceza})" if args.ceza else ""))
    if onceki:
        print("NOT: önceki olay defteri vardı; --baslat taze başlattı (eski kayıtlar sıfırlandı).")
    print("Gerçeğin kaynağı: append-only olay defteri (jsonl); türev görünüm: " + durum_yol)
    print("Hatırlatma: statü ancak KANITLA yazılır; kanıt = fiilî Skill çağrısı / "
          "gerçek script çıktısı / gerçek MCP çağrısı (araç+sorgu+sonuç).")
    _durum_md_yaz(getattr(args, "kok", None))


PAS_AZAMI_BAYT = 256 * 1024  # M1 (Paket D DÜZELTME YENİ-1) — pas gövdesi tavanı


def _dizin_icinde_mi(yol, dizin):
    """`yol` gerçekten `dizin` (veya bir alt dizini) içinde mi? `os.path.realpath`
    ile çözülür (`..`/sembolik bağ kaçışlarına karşı) — `ictihat_muhakeme_denetim.
    _dizin_icinde_mi` ile AYNI kural (Paket D YENİ-1: ailenin zaten sahip olduğu
    kapsama denetimi burada da uygulanır)."""
    try:
        yol_n = os.path.normcase(os.path.realpath(yol))
        dizin_n = os.path.normcase(os.path.realpath(dizin))
    except OSError:
        return False
    return yol_n == dizin_n or yol_n.startswith(dizin_n + os.sep)


def _pas_cikti_dizini(kok):
    return os.path.join(kok or ".", "_oa", "cikti")


def _pas_yolu_tam_coz(kok, pas_yolu):
    return pas_yolu if os.path.isabs(pas_yolu) else os.path.join(kok or ".", pas_yolu)


def _pas_yolu_kapsam_disi_mi(kok, pas_yolu):
    """M1 PAS PROTOKOLÜ'nün kendi hükmü zaten `_oa/cikti/NN-parca-*.md` şart
    koşar; bu fonksiyon o hükmü MEKANİK olarak zorlar. True → pas_yolu
    `_oa/cikti/` dışına çıkıyor (göreli `..`, mutlak yol, sembolik bağ dahil)."""
    if not pas_yolu:
        return False
    tam_yol = _pas_yolu_tam_coz(kok, pas_yolu)
    return not _dizin_icinde_mi(tam_yol, _pas_cikti_dizini(kok))


def _pas_yolu_izin_denetle(kok, pas_yolu):
    """M1 (Paket D DÜZELTME YENİ-1) — `--pas-yolu` deftere YAZILMADAN ÖNCE
    çağrılır: kapsam dışıysa FAIL-CLOSED RET (exit) — kirli/keyfi bir dosya
    yolu deftere hiç girmez, sonraki `ajan-brif` onu asla devralamaz. Bu,
    A-Ş3 sınıfının (dizin dışına YAZMA) okuma yönündeki ikizini kapatır."""
    if not pas_yolu:
        return
    if _pas_yolu_kapsam_disi_mi(kok, pas_yolu):
        tam_yol = _pas_yolu_tam_coz(kok, pas_yolu)
        sys.exit(
            "RET: --pas-yolu yalnız _oa/cikti/ altını işaret edebilir (P1-11 PAS "
            f"PROTOKOLÜ) — verilen: {pas_yolu} (çözülen: {os.path.realpath(tam_yol)}; "
            f"izinli kapsam: {os.path.realpath(_pas_cikti_dizini(kok))})")


def _pas_yolu_uyarilari(kok, pas_yolu):
    """M1 PAS PROTOKOLÜ (Paket D sınav bulgusu) — `--pas-yolu` verildiğinde iki
    UCUZ, BLOKLAMAYAN mekanik kontrol: (1) dosya diskte var mı; (2) ilk
    boş-olmayan satırı `TEZ:` ile başlıyor mu (P1-11 zorunluluğu). İkisi de
    exit koduna dokunmaz — yalnız GÖRÜNÜR uyarı üretir (ailenin ucuz+görünür
    advisory deseni). Kapsam denetimi burada YAPILMAZ — `_pas_yolu_izin_denetle`
    zaten deftere yazılmadan ÖNCE bloklayıcı olarak çalışmıştır (YENİ-1)."""
    if not pas_yolu:
        return []
    uyarilar = []
    tam_yol = _pas_yolu_tam_coz(kok, pas_yolu)
    if not os.path.isfile(tam_yol):
        uyarilar.append(
            f"UYARI: --pas-yolu diskte bulunamadı ({pas_yolu}) — sonraki brif bu pası devralamaz")
        return uyarilar
    try:
        ilk_satir = ""
        with open(tam_yol, encoding="utf-8", errors="replace") as f:
            for satir in f:
                if satir.strip():
                    ilk_satir = satir.strip()
                    break
        if not ilk_satir.startswith("TEZ:"):
            uyarilar.append(
                "UYARI: pas ilk satırında TEZ: taşımıyor (P1-11 PAS PROTOKOLÜ)")
    except OSError:
        pass  # okunamadıysa üstteki dosya-var kontrolü zaten bloklamıyor; sessizce geç
    return uyarilar


def isle(args):
    olaylar_yol, durum_yol = _yollar(args)
    kanit = dogrula_statu(args)
    if args.adim is None:
        sys.exit("HATA: --adim gerekli (0-10).")
    if str(args.adim) not in {str(k) for k in ADIMLAR}:
        sys.exit(f"HATA: adım {args.adim} yok (0-10).")
    if not _defter_var(olaylar_yol, durum_yol):
        sys.exit(f"HATA: defter bulunamadı: {olaylar_yol} — önce --baslat ile aç.")
    _pas_yolu_izin_denetle(getattr(args, "kok", None), getattr(args, "pas_yolu", None))

    # P0-6 — KADEMELİ ÖNKOŞUL-ARTEFAKT KAPISI (yalnız UYGULANDI'da; GEREKSIZ/
    # BILGI-EKSIK/YUKLENEMEDI gerekçeli serbesttir — mevcut davranış).
    serh_bayrak, serh_metni, ek_uyari = False, None, ""
    if args.durum == "UYGULANDI":
        kok = getattr(args, "kok", None)
        onceki_d = derle(olaylar_yol, durum_yol)  # bu olay eklenmeden ÖNCEKİ durum (çapraz-adım için)
        izin, sorun, onkosul_uyari, serh_mesaj = _onkosul_kontrol(
            kok, args.adim, args.parca, getattr(args, "serh", None), mevcut_d=onceki_d,
            kanit=kanit)
        if not izin:
            sys.exit("RET: " + sorun +
                      f' (Bilerek geçmek için: --serh "gerekçe (>={SERH_GEREKCE_MIN} kr)")')
        if serh_mesaj:
            serh_bayrak, serh_metni = True, serh_mesaj
        elif onkosul_uyari:
            ek_uyari = "\nUYARI: " + onkosul_uyari

    # ATOMİK APPEND — eşzamanlı --isle'ler (farklı adım) birbirini silemez.
    olay = {"zaman": simdi(), "tip": "adim", "adim": args.adim,
            "parca": args.parca, "durum": args.durum, "kanit": kanit,
            "surum": OA_SURUM}
    if getattr(args, "pas_yolu", None):
        olay["pas_yolu"] = args.pas_yolu
    if serh_bayrak:
        olay["serh"] = True
        olay["serh_metni"] = serh_metni
    olay["imza"] = _imza_hesapla(olay)
    olay_ekle(olaylar_yol, olay)
    d_sonra = derle(olaylar_yol)
    _durum_yaz(durum_yol, d_sonra)  # türev görünümü tazele
    uyari = ""
    if (args.durum == "UYGULANDI" and args.parca in SCRIPTLI
            and "script" not in kanit.lower() and ".py" not in kanit.lower()):
        uyari = ("\nUYARI: bu parça SCRIPT'lidir; kanıtta script çıktısına iz yok — "
                 "gerçek script koştuysa kanıta yaz, koşmadıysa statü sahte olur.")
    if serh_bayrak:
        uyari += "\n⚠ ŞERHLİ UYGULANDI: " + serh_metni
    for pas_uyari in _pas_yolu_uyarilari(getattr(args, "kok", None), getattr(args, "pas_yolu", None)):
        uyari += "\n" + pas_uyari
    # GÖREV C(1) — DAL UYUŞMAZLIĞI: bu ÇAĞRIDA yazılan parça dosyanın dalına
    # aykırıysa hemen görünür bir UYARI (bloklamaz); kalıcı görünürlük için
    # AYNI kontrol _denetle_hesapla üzerinden --goster/--denetle/DURUM.md'de
    # de tekrar hesaplanır (bkz. _dal_uyusmazlik_uyarilari).
    if d_sonra is not None and args.durum not in _DAL_UYARI_ATLA_DURUMLARI:
        dal_tek = _dosya_dali_tahmin(getattr(args, "kok", None), d_sonra.get("ceza_dali"))
        if dal_tek is not None:
            dal_mesaj = _dal_uyusmazlik_tek(dal_tek, args.parca)
            if dal_mesaj:
                uyari += "\nUYARI: DAL UYUŞMAZLIĞI: " + dal_mesaj
    print(f"İşlendi: adım {args.adim} / {args.parca} → {args.durum}{uyari}{ek_uyari}")
    _durum_md_yaz(getattr(args, "kok", None))


def katman_isle(args):
    olaylar_yol, durum_yol = _yollar(args)
    kanit = dogrula_statu(args)
    if not _defter_var(olaylar_yol, durum_yol):
        sys.exit(f"HATA: defter bulunamadı: {olaylar_yol} — önce --baslat ile aç.")
    olay = {"zaman": simdi(), "tip": "katman", "katman": args.katman,
            "durum": args.durum, "kanit": kanit, "surum": OA_SURUM}
    olay["imza"] = _imza_hesapla(olay)
    olay_ekle(olaylar_yol, olay)
    d_sonra = derle(olaylar_yol)
    _durum_yaz(durum_yol, d_sonra)
    uyari = ""
    # GÖREV C(1) — DAL UYUŞMAZLIĞI (bkz. isle() için AYNI kontrol/yorum).
    if d_sonra is not None and args.durum not in _DAL_UYARI_ATLA_DURUMLARI:
        dal_tek = _dosya_dali_tahmin(getattr(args, "kok", None), d_sonra.get("ceza_dali"))
        if dal_tek is not None:
            dal_mesaj = _dal_uyusmazlik_tek(dal_tek, args.katman)
            if dal_mesaj:
                uyari = "\nUYARI: DAL UYUŞMAZLIĞI: " + dal_mesaj
    print(f"İşlendi: katman {args.katman} → {args.durum}{uyari}")
    _durum_md_yaz(getattr(args, "kok", None))


def _arac_hatalari_yaz(arac_hatalari):
    """D5: kayıtlı 'ARAÇ ÇÖKTÜ' olaylarını GÖRÜNÜR biçimde bas — sessizce atlanamaz."""
    if not arac_hatalari:
        return
    print(f"— ⚠ ARAÇ ÇÖKTÜ — teyitsiz ({len(arac_hatalari)}) —")
    for h in arac_hatalari:
        konum = ""
        if h.get("adim") is not None or h.get("parca"):
            konum = f" [adım {h.get('adim')}/{h.get('parca')}]" if h.get("adim") is not None \
                else f" [{h.get('parca')}]"
        sorgu = f" · sorgu: {h['sorgu']}" if h.get("sorgu") else ""
        print(f"  ⚠ {h.get('arac')}{konum}{sorgu} · hata: {h.get('hata')}")


def arac_hata(args):
    """D5 — SESSİZ-ARAÇ HATASI KAPISI: bir MCP/araç çağrısı çökerse deftere
    'ARAÇ ÇÖKTÜ — teyitsiz' olarak İŞLENİR; sessizce geçilmez (sessiz-atlama
    yasağının MCP tarafı). Defter önceden --baslat ile açılmış olmalı (diğer
    --isle/--katman komutlarıyla aynı ön-koşul)."""
    olaylar_yol, durum_yol = _yollar(args)
    if not _defter_var(olaylar_yol, durum_yol):
        sys.exit(f"HATA: defter bulunamadı: {olaylar_yol} — önce --baslat ile aç.")
    olay = {"zaman": simdi(), "tip": "arac-hatasi", "arac": args.arac,
            "sorgu": args.sorgu, "hata": args.hata, "adim": args.adim, "parca": args.parca}
    olay["imza"] = _imza_hesapla(olay)
    olay_ekle(olaylar_yol, olay)
    _durum_yaz(durum_yol, derle(olaylar_yol))
    konum = f" [adım {args.adim}/{args.parca}]" if args.adim is not None else \
        (f" [{args.parca}]" if args.parca else "")
    sorgu = f" · sorgu: {args.sorgu}" if args.sorgu else ""
    print(f"KAYDEDİLDİ: ⚠ ARAÇ ÇÖKTÜ — teyitsiz · araç: {args.arac}{konum}{sorgu} · hata: {args.hata}")
    print("Bu olay --goster/--denetle çıktısında HER ZAMAN görünür (sessizce geçilmez); "
          "iş alternatif kaynak/yöntemle tamamlandıysa bunu ilgili adımın kanıtına da yaz.")
    _durum_md_yaz(getattr(args, "kok", None))


AVUKAT_KARARI_GEREKCE_MIN = 15  # karakter — çatal çözümü gerekçesiz kaydedilemez


def avukat_karari_kaydet(args):
    """M7 (Paket D, v0.5.5) — AVUKAT KARARI BEKLEYEN listesindeki bir çatalı
    (BİLGİ-EKSİK / ŞERHLİ UYGULANDI kalemi) avukat NİHAİ kararıyla ÇÖZER.
    (--adim + --parca) VEYA --katman ile hedeflenir; --gerekce ZORUNLUDUR
    (≥AVUKAT_KARARI_GEREKCE_MIN karakter) — 'çatallar gerekçeli seçeneklerle
    listelenir' doktrinin karar tarafı: seçilen seçeneğin NEDEN seçildiği
    kalıcı olarak (append-only) DURUM.md'ye ve deftere işlenir; önceki
    BEKLEYEN kaydı SİLİNMEZ (kayıpsızlık), yalnız `_avukat_karari_bekleyen`
    listesinden ÇIKARILIR (çözülmüş sayılır)."""
    olaylar_yol, durum_yol = _yollar(args)
    if not _defter_var(olaylar_yol, durum_yol):
        sys.exit(f"HATA: defter bulunamadı: {olaylar_yol} — önce --baslat ile aç.")
    if not args.katman and (args.adim is None or not args.parca):
        sys.exit("HATA: --avukat-karari için (--adim + --parca) VEYA --katman gerekli.")
    if not args.gerekce or len(args.gerekce.strip()) < AVUKAT_KARARI_GEREKCE_MIN:
        sys.exit(f"RET: --avukat-karari GEREKÇESİZ kaydedilemez — --gerekce "
                 f"(≥{AVUKAT_KARARI_GEREKCE_MIN} karakter) ZORUNLU.")
    # DÜZELTME (v0.5.5 şerh turu — Ş14 KUCUK): hedefin (adım+parça/katman)
    # defterde GERÇEKTEN AÇIK bir çatal olup olmadığı, olay eklemeden ÖNCE
    # (mevcut durum) denetlenir — yön fail-CLOSED DEĞİL (kayıpsızlık/
    # append-only bozulmasın, meşru 'önden karar' senaryosu kapanmasın),
    # yalnız sonuç mesajı NİTELENDİRİLİR (bkz. aşağıdaki UYARI).
    d_onceki = derle(olaylar_yol)
    hedef_acik = True
    if d_onceki is not None:
        hedef_acik = _avukat_karari_hedefi_acik_mi(
            d_onceki, adim=args.adim, parca=args.parca, katman=args.katman)
    olay = {"zaman": simdi(), "tip": "avukat-karari", "adim": args.adim, "parca": args.parca,
            "katman": args.katman, "karar": args.avukat_karari, "gerekce": args.gerekce.strip()}
    olay["imza"] = _imza_hesapla(olay)
    olay_ekle(olaylar_yol, olay)
    _durum_yaz(durum_yol, derle(olaylar_yol))
    hedef = f"katman {args.katman}" if args.katman else f"adım {args.adim} / {args.parca}"
    mesaj = f"AVUKAT KARARI KAYDEDİLDİ — {hedef}: {args.avukat_karari} (gerekçe: {args.gerekce})"
    if not hedef_acik:
        mesaj += (f"\n⚠ UYARI: bu hedef ({hedef}) defterde AÇIK bir çatal olarak "
                  "bulunamadı — parça adı/adım no yazım hatası olabilir; DURUM.md > "
                  "Avukat Kararı Bekleyen bölümünü teyit et.")
    print(mesaj)
    _durum_md_yaz(getattr(args, "kok", None))


def goster(args):
    olaylar_yol, durum_yol = _yollar(args)
    d = derle(olaylar_yol, durum_yol)
    if d is None:
        sys.exit(f"HATA: defter bulunamadı: {olaylar_yol} — önce --baslat ile aç.")
    _durum_yaz(durum_yol, d)  # türev görünümü tazele
    print(f"# Pipeline Defteri — {d['dosya']}  (açılış: {d['olusturma']})")
    for no in sorted(d["adimlar"], key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
        a = d["adimlar"][no]
        for parca, p in a["parcalar"].items():
            isaret = {"UYGULANDI": "✓", "GEREKSIZ": "−", "BILGI-EKSIK": "?",
                      "YUKLENEMEDI": "!", "BEKLIYOR": "⬜"}.get(p["durum"], "?")
            serh_notu = "  ⚠ ŞERHLİ UYGULANDI" if p.get("serh") else ""
            pas_notu = f"  [PAS: {p.get('pas_yolu')}]" if p.get("pas_yolu") else ""
            print(f"{isaret} {no:>2}. {a['ad']:<11} {parca:<18} {p['durum']}"
                  + (f" — {p['kanit'][:90]}" if p["kanit"] else "") + serh_notu + pas_notu)
    print("— Katmanlar —")
    for k, p in d["katmanlar"].items():
        print(f"  {k:<18} {p['durum']}" + (f" — {p['kanit'][:90]}" if p["kanit"] else ""))
    _arac_hatalari_yaz(d.get("arac_hatalari") or [])
    # P1-9(b) DÜZELTME — gölge-dizin bekçisi --goster'da da GÖRÜNÜR (yalnız
    # --denetle'ye özgü kalmasın; --goster daha sık/ucuz çağrılan bir komut).
    kok_g = getattr(args, "kok", None)
    sozlesme_disi = _sozlesme_disi_dizinler(kok_g or ".")
    if sozlesme_disi:
        print(f"⚠ SÖZLEŞME-DIŞI DİZİN(LER): "
              + ", ".join(f"_oa/{ad}" for ad in sozlesme_disi)
              + " — beklenmeyen konum (gölge hat/dağınık-çıktı adayı olabilir).")
    _durum_md_yaz(getattr(args, "kok", None))
    # YENİ-2 düzeltmesi (turu 2): tam oa_metrik telemetri tablosu ([1]-[7])
    # yalnız AÇIKÇA istenirse (`--telemetri`) basılır — varsayılan `--goster`
    # UCUZ/SIK çağrı olarak kalır (bkz. yukarıdaki P1-9(b) notu), hook yolu
    # da artık bunu otomatik basmaz (bkz. `_hook_govde_calistir`); bu ikisinin
    # TEK ortak çıkış noktası burasıdır.
    if getattr(args, "telemetri", False):
        print(_oa_metrik_ozet_al(kok_g or "."))


# P0-4 (v0.5.5) — Gate G dairesel bağımlılık kırıcı, KÖKTEN çözüm: subprocess
# (nested `sys.executable tam_tur.py --durum`) VE ortam-değişkeni bayrağı
# sınıfı TAMAMEN kalkar. `pipeline_kayit.py` `tam_tur.py`'yi İN-PROCESS import
# eder (aynı dizin, importlib.util — path/env kırılganlığı yok) ve doğrudan
# `_analiz_kaydi_fiziksel_tamam` fonksiyonunu çağırır; ayrı bir Python süreci
# BAŞLAMAZ. Bu, T3'ün reddedilen `--gate-g-haric` CLI bayrağından (--help'te
# görünür, elle verilebilir) FARKLIDIR: `gate_g_atla` yalnız Python fonksiyon
# parametresidir, CLI'den asla ulaşılamaz — TEK meşru çağıran `tam_tur.py`'nin
# KENDİ `_defter_denetle`'idir (bkz. tam_tur.py) ve atlama HER ZAMAN GÖRÜNÜR
# bir uyarı satırı üretir (sessiz atlama yasağı).
_TAM_TUR_MOD = None


def _tam_tur_modulu():
    """tam_tur.py'yi İN-PROCESS import eder (bkz. modül-üstü not). Başarısızsa
    None döner — çağıran taraf bunu GÖRÜNÜR bir uyarıya çevirir (fail-open,
    sessiz değil)."""
    global _TAM_TUR_MOD
    if _TAM_TUR_MOD is not None:
        return _TAM_TUR_MOD
    betik = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tam_tur.py")
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_oa_pipeline_tam_tur_inproc", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        # P0-4 DÜZELTME: istisna metni ÇAĞIRANA (aşağıdaki `tam_tur is None`
        # dalı) taşınır — eski subprocess yolu istisnayı `({e})` ile
        # raporluyordu, in-process sarmalayıcı bunu SESSİZCE yutmasın.
        print(f"UYARI: tam_tur.py import edilemedi ({e}) — tam yol: {betik}")
        return None
    _TAM_TUR_MOD = mod
    return _TAM_TUR_MOD


def _gate_g_kalicilik_denetle(kok, atla=False):
    """Gate G — KALICILIK KAPISI (§ pipeline KAPANIŞ mekanik kapısı): tam_tur.py bu
    kökte KULLANILMIŞSA (`_oa/analiz/dosya-analiz.json` var), pipeline "analiz
    tamamlandi" damgasını tam_tur'un KENDİ mekanik fiziksel-tamam sinyali olmadan
    VURAMAZ — dosya-analiz.md + _oa/cikti özetleri ATOMİK yazılmış ve GÜNCEL
    olmalı. 'tamamlandi' = tam_tur.py'nin KENDİ `_analiz_kaydi_fiziksel_tamam`
    fonksiyonunun SONUCU (İN-PROCESS çağrılır), MODEL BEYANI DEĞİL.

    `atla=True` — DAİRESEL BAĞIMLILIK KIRICI (P0-4): bu denetim `tam_tur.cmd_kaydet`
    TARAFINDAN (o TAMAM işaretini YAZACAK OLAN operasyonun KENDİSİ) çağrıldığında,
    işaretin YAZILMADAN ÖNCE kendine karşı sınanması FİZİKSEL OLARAK İMKÂNSIZDIR
    (döngü tam burada kurulur: yaz→denetle→yaz gerektirir). `atla=True` yalnız bu
    tek meşru durumda, tam_tur.py'nin kendi in-process çağrısıyla geçirilir; CLI'de
    hiçbir bayrak YOKTUR, dışarıdan elle verilemez. Atlama HER ZAMAN GÖRÜNÜR bir
    uyarı olarak döner (sessiz atlama yasağı) — bloklamaz, gizlemez.

    tam_tur.py bu kökte HİÇ kullanılmamışsa (dosya-analiz.json yok — tam_tur
    kullanmayan akış) kapı SESSİZCE atlanır (defter kapısıyla simetrik davranış;
    mevcut/tam_tur'suz akışlar bloklanmaz). Döner: (sorun:str|None, uyari:str|None)."""
    analiz_json = os.path.join(kok or ".", "_oa", "analiz", "dosya-analiz.json")
    if not os.path.exists(analiz_json):
        # P0-4 DÜZELTME: `atla` kontrolü BU satırın ARDINA alındı — tam_tur.py
        # hiç kullanılmamış bir kökte (dosya-analiz.json yok) her `--kaydet`
        # çağrısında gereksiz "ATLANDI" gürültüsü basılmasın (gerçek atlama
        # tam_tur KULLANAN bir kökte anlamlıdır; kullanılmayan kökte zaten
        # SESSİZCE atlanıyordu — bu satır sırası o sessizliği korur).
        return None, None
    if atla:
        return None, ("Gate G (kalıcılık): ATLANDI — bu denetim tam_tur.cmd_kaydet'in "
                       "KENDİSİNDEN çağrıldı (TAMAM işaretini YAZACAK operasyon kendine "
                       "karşı önceden sınanamaz — P0-4 dairesel bağımlılık kırıcı).")
    # P1-12 DÜZELTME (BLOKER, sinav bulgusu) — 'çöken kapı = atlanan kapı'
    # sınıfı burada FAIL-CLOSED'a çevrilir: dosya-analiz.json bu kökte VARKEN
    # (tam_tur FİİLEN kullanılmışken) tam_tur.py import edilemiyor/çöküyorsa,
    # kalıcılık GERÇEKTEN sınanamamış demektir — bu bir 'atlama' değil, bir
    # SORUNDUR (TESLİM ENGELİ). Eski davranış (None, uyarı) bu en kritik yolu
    # sessizce fail-open bırakıyordu; şimdi sorun döner (sorunlar listesine
    # girer), --zorla/--serh mekanizmaları GEREKÇELİ geçişi zaten sağlar.
    tam_tur = _tam_tur_modulu()
    if tam_tur is None:
        return ("Gate G (kalıcılık): tam_tur.py import edilemedi — kapı KAPALI "
                "(FAIL-CLOSED, P1-12); tam yolu için yukarıdaki UYARI satırına bkz."), None
    try:
        durum = tam_tur._durum_oku(kok or ".") or {}
        tamam, sebep = tam_tur._analiz_kaydi_fiziksel_tamam(kok or ".", durum)
    except Exception as e:
        return (f"Gate G (kalıcılık) denetlenemedi: tam_tur.py çağrılamadı ({e}) — "
                "kapı KAPALI (FAIL-CLOSED, P1-12)."), None
    if tamam:
        return None, None
    return (f"Gate G (kalıcılık): dosya-analiz.md fiziksel TAMAM değil — {sebep} "
            "(tam_tur._analiz_kaydi_fiziksel_tamam, İN-PROCESS)."), None


def _makbuz_denetim_hesapla(kok, d):
    """P0-5(d) — adım-9 (oa-kontrol) UYGULANDI ise TESLİM MAKBUZU (_oa/defter/
    teslim-makbuz.json) GEÇERLİ olmalı: var + exit_kodu==0 + kayıtlı taslak
    hâlâ diskte + GÜNCEL sha kayıtlı sha256 ile eşleşiyor (sonradan elle
    değiştirilmemiş) VE — DÜZELTME (Paket-B sinav-turu BLOKER giderimi,
    'doğal sıra' atlatması) — makbuzun taslağı HÂLÂ `_oa/cikti`'daki EN YENİ
    dilekçe-şekilli dosyayla eşleşiyor. Eski sürüm yalnız makbuzun KENDİ İÇ
    tutarlılığına (exit_kodu+sha) bakıyordu; 'teslim et → adım-9 işaretle →
    SONRA revize/yeni sürüm yaz' (en sık gerçek akış) doğal sırasında makbuz
    kendi içinde tutarlı kalırken (A hâlâ diskte, sha hâlâ eşleşiyor) B artık
    en yeni dosya olur — bu durumda yazım-anı kapısı
    (`_makbuz_onkosul_saglam_mi`) ile AYNI `_dilekce_sekilli_makbuzsuz_uyarisi`
    kontrolü burada da (denetim-anı) çalıştırılır: SİMETRİK kapı. Geçiş
    supabı (T1): bu defterde HİÇ v0.5.5+ olay yoksa (eski/az önce yükseltilmiş
    kök) sorun BLOKLEYICI değil, yalnız UYARIdır — ilk v0.5.5 yazımından
    SONRA (bu defter artık 'migrate' olmuş sayılır) blokleyicidir. adım-9
    UYGULANDI olayının kendisi ŞERHLİ yazılmışsa (yazım anındaki gerekçe
    BAŞKA bir uyumsuzluğa aitti) o gerekçe metni GÖRÜNÜR kalsın diye mesaja
    eklenir — ama bu, SONRADAN oluşan yeni bir uyumsuzluğu (ör. B dosyası)
    sessizce affetmez, yalnız bağlam sağlar. Döner: (sorun:str|None,
    uyari:str|None)."""
    adim9 = (d.get("adimlar", {}).get("9", {}).get("parcalar", {}) or {}).get("oa-kontrol")
    if not adim9 or adim9.get("durum") != "UYGULANDI":
        return None, None
    mesaj = None
    m, hata = _makbuz_oku(kok)
    if m is None:
        mesaj = ("TESLİM MAKBUZU yok — adım-9 UYGULANDI ama teslim_paketi.py hiç "
                 f"TESLİME HAZIR olmamış ({hata}).")
    elif m.get("exit_kodu") != 0:
        mesaj = "teslim-makbuz.json exit_kodu != 0 (son teslim RED/başarısız)."
    else:
        taslak = m.get("taslak_yol")
        sha_kayitli = m.get("taslak_sha256")
        if taslak and sha_kayitli:
            if not os.path.isfile(taslak):
                mesaj = f"teslim-makbuz.json'daki taslak artık diskte yok: {taslak}"
            else:
                guncel = _sha256_dosya(taslak)
                if guncel != sha_kayitli:
                    mesaj = ("teslim-makbuz.json'daki taslak SONRADAN DEĞİŞTİRİLMİŞ "
                             f"(sha uyumsuz) — {taslak} (teslim_paketi.py'yi yeniden koş).")
    if mesaj is None:
        # Makbuz kendi içinde tutarlı — ŞİMDİ de hâlâ `_oa/cikti`'daki EN YENİ
        # dilekçe-şekilli dosyaya karşılık geliyor mu? (doğal-sıra kontrolü)
        mesaj = _dilekce_sekilli_makbuzsuz_uyarisi(kok)
        if mesaj and adim9.get("serh"):
            mesaj += (" [NOT: adım-9 UYGULANDI ŞERHLİ yazılmıştı — o gerekçe: "
                      f"{adim9.get('serh_metni') or '?'} — bu, o yazımdan SONRAKİ "
                      "bir değişikliği (yeni/revize dosya) kapsamaz, yeni bir "
                      "teslim_paketi.py koşusu veya yeni bir şerh gerektirir.]")
    if mesaj is None:
        return None, None
    if not _surum_v055_var_mi(d, kok):
        # DÜZELTME (turu 2, YENİ-1): "eski/önceki-sürüm defter" ifadesi
        # `surum_gorulen` TAMAMEN boş olan (ör. elle yazılmış) defterler
        # için yanıltıcıydı — dosya eski DEĞİL, defter yalnız damgasız.
        # Sebep artık ayırt edilerek söylenir (mevcut "eski/önceki-sürüm"
        # alt dizesi geriye dönük uyumluluk için korunur).
        if (d or {}).get("surum_gorulen"):
            sebep = "eski/önceki-sürüm defter"
        else:
            sebep = ("eski/önceki-sürüm defter — YA DA defterde hiç sürüm damgası "
                     "yok (elle yazılmış/pipeline_kayit.py CLI'sinden geçmemiş olabilir; "
                     "bkz. Defter Bütünlüğü: N model-beyanlı)")
        return None, f"TESLİM MAKBUZU ({sebep} — yalnız uyarı): " + mesaj
    return "TESLİM MAKBUZU: " + mesaj, None


def _dilekce_sekilli_makbuzsuz_uyarisi(kok):
    """P0-5 DÜZELTME(a) (sinav-turu ile SIKILAŞTIRILDI) — ad-deseni
    ('*TESLIM*/*FINAL*') TEK tetikleyici DEĞİLDİR. İki ayrı kaçağı kapatır:
    (1) 'en yeni dosya' TÜM _oa/cikti dosyaları arasından değil, yalnız
    dilekçe-şekilli (mahkeme/taraf/netice başlıklı) OLANLAR arasından seçilir
    — dilekçeden SONRA yazılmış dilekçe-şekilli-OLMAYAN bir not/log dosyası
    artık uyarıyı SUSTURAMAZ. (2) geçerli (exit_kodu==0) bir TESLİM MAKBUZU
    VARSA dahi, o makbuzun `taslak_yol`u bu en-yeni dilekçe-şekilli dosyanın
    MUTLAK YOLUYLA eşleşmiyorsa (ad ne olursa olsun) yine uyarı basılır —
    başka bir taslak için üretilmiş BAYAT/YANLIŞ-DOSYA makbuzu bu dosyayı
    artık teslime yetkilendiremez. Her zaman aktif (ucuz disk okuması; sürüm
    supabı taşımaz).

    DÜZELTME (v0.5.5 şerh turu — Ş9 ÖNEMLİ, ALT KLASÖR körlüğü): eskiden
    `os.listdir` ile ÖZYİNELEMESİZDİ — `_oa/cikti/dilekce/...` gibi bir alt
    klasördeki dilekçe SESSİZCE görünmez kalıyor, bu da TÜM makbuz zincirinin
    (P0-5) bir alt klasöre dosya koymakla atlanabilmesi demekti. Artık
    `os.walk` ile ÖZYİNELEMELİ taranır (`tam_tur._cikti_topla` ile SİMETRİK)."""
    cdiz = os.path.join(kok or ".", "_oa", "cikti")
    if not os.path.isdir(cdiz):
        return None
    dilekce_dosyalari = []
    for kok_dizin, alt_dizinler, dosyalar in os.walk(cdiz):
        alt_dizinler.sort()
        for ad in sorted(dosyalar):
            yol = os.path.join(kok_dizin, ad)
            if not os.path.isfile(yol):
                continue
            try:
                with open(yol, encoding="utf-8", errors="replace") as f:
                    icerik = f.read()
            except OSError:
                continue
            if _DILEKCE_DESEN.search(icerik):
                dilekce_dosyalari.append(yol)
    if not dilekce_dosyalari:
        return None
    en_yeni = max(dilekce_dosyalari, key=lambda y: os.path.getmtime(y))
    en_yeni_abs = os.path.abspath(en_yeni)
    m, _hata = _makbuz_oku(kok)
    if m is not None and m.get("exit_kodu") == 0:
        taslak_kayitli = m.get("taslak_yol")
        if taslak_kayitli and os.path.abspath(taslak_kayitli) == en_yeni_abs:
            return None
        return (f"makbuzsuz dilekçe adayı: {en_yeni} (dilekçe-şekilli en yeni çalışma "
                "evrakı — geçerli TESLİM MAKBUZU BAŞKA bir dosya için üretilmiş: "
                f"{taslak_kayitli or '?'}; ad ne olursa olsun teslim_paketi.py'yi BU "
                "dosya için koş)")
    return (f"makbuzsuz dilekçe adayı: {en_yeni} (dilekçe-şekilli en yeni çalışma "
            "evrakı — geçerli TESLİM MAKBUZU bulunamadı; ad ne olursa olsun "
            "teslim_paketi.py koş)")


def _udf_makbuzsuz_uyarisi(kok):
    """P0-5 DÜZELTME(a) sinav-turu — plan metninin 'udf_yaz üretimi = TESLİM
    olayı' cümlesinin somutlanması: çalışma kökünde VEYA `_oa/cikti`'da,
    geçerli (exit_kodu==0) TESLİM MAKBUZU'nun KENDİ ürettiği `.udf` dosyası
    DIŞINDA, o makbuzun `zaman`ından SONRA üretilmiş/değiştirilmiş bir `.udf`
    dosyası varsa GÖRÜNÜR bir uyarı basılır — udf_yaz.py teslim_paketi.py
    ZİNCİRİ ATLANARAK doğrudan çağrılıp müvekkile/mahkemeye giden bir UDF
    üretmiş olabilir. Advisory (asla blokleyici değil); P2-14'ün tam
    sayaç/telemetri entegrasyonu Paket C kapsamındadır."""
    m, _hata = _makbuz_oku(kok)
    makbuz_zaman = None
    makbuz_udf_abs = None
    if m is not None and m.get("exit_kodu") == 0:
        try:
            makbuz_zaman = datetime.datetime.fromisoformat(m.get("zaman"))
        except (TypeError, ValueError):
            makbuz_zaman = None
        if m.get("udf_yolu"):
            makbuz_udf_abs = os.path.abspath(m["udf_yolu"])
    aday_dizinler = [kok or ".", os.path.join(kok or ".", "_oa", "cikti")]
    bulunan = []
    for dizin in aday_dizinler:
        if not os.path.isdir(dizin):
            continue
        try:
            girdiler = os.listdir(dizin)
        except OSError:
            continue
        for ad in girdiler:
            if not ad.lower().endswith(".udf"):
                continue
            yol = os.path.join(dizin, ad)
            if not os.path.isfile(yol):
                continue
            yol_abs = os.path.abspath(yol)
            if makbuz_udf_abs and yol_abs == makbuz_udf_abs:
                continue
            try:
                mt = os.path.getmtime(yol)
            except OSError:
                continue
            if makbuz_zaman is not None and datetime.datetime.fromtimestamp(mt) <= makbuz_zaman:
                continue
            bulunan.append(yol)
    if not bulunan:
        return None
    en_yeni = max(bulunan, key=lambda y: os.path.getmtime(y))
    return (f"makbuzsuz UDF üretimi: {en_yeni} (geçerli TESLİM MAKBUZU'ndan BAĞIMSIZ "
            "bir .udf — teslim_paketi.py zinciri atlanmış olabilir; bu dosya için "
            "teslim_paketi.py'yi koş)")


def _denetle_hesapla(kok, olaylar_yol, durum_yol, gate_g_atla=False, makbuz_kontrolu=True,
                      teslim_oncesi=False):
    """--denetle'nin ÇEKİRDEK mantığı — CLI'den (`denetle`) VE İN-PROCESS
    çağıranlardan (`denetle_calistir`, bkz. tam_tur.py `_defter_denetle`, P0-4)
    ORTAK kullanılır. Döner: (d:dict|None, sorunlar:list[str], uyarilar:list[str]).
    `d` None ise defter bulunamadı demektir (çağıran HATA ile çıkmalı).
    `makbuz_kontrolu=False` — YALNIZ `teslim_paketi.py`'nin (d) adımının
    İN-PROCESS çağrısında kullanılır (dairesel bağımlılık kırıcı, P0-5): o
    kapının amacı defter BOŞLUĞUdur, makbuz BÜTÜNLÜĞÜ değil — makbuz zaten
    teslim_paketi'nin KENDİSİ tarafından zincirin SONUNDA üretilir; kendi
    üreteceği makbuzun YOKLUĞU yüzünden kendine engel koyması (yaz→denetle→
    yaz döngüsü) fiziksel olarak imkânsız bir önkoşuldur.

    `teslim_oncesi=True` — sinav-turu BLOKER düzeltmesi (P0-5×P0-6 dairesel
    KİLİT): YALNIZ `teslim_paketi.py`'nin (d) İN-PROCESS çağrısında,
    `makbuz_kontrolu=False` İLE BİRLİKTE kullanılır. adım-9 (KONTROL) ve
    adım-10 (KAPANIŞ) BEKLIYOR durumları bu modda sorun SAYILMAZ — bu ikisi
    TANIM GEREĞİ teslimden SONRA kapanır (adım-9 kapanmak için TAM DA (d)
    kapısının ürettiği makbuza muhtaçtır); aksi hâlde (d) kapısı hiçbir
    zaman UYGULANDI adım-9'dan önce açılamaz, adım-9 de makbuzsuz UYGULANDI
    yazılamayacağından döngü kapanmaz (--serh tek çıkış olur — sinav'ın
    uyardığı ucuzlama). Bu istisna YALNIZ (d) kapısında geçerlidir; bağımsız
    `--denetle` (CLI) ve `--hook-denetle` HER ZAMAN `teslim_oncesi=False` ile
    çağrılır — nihai/teslim-sonrası denetimde adım-9/10 boşluğu YİNE tam
    güçte sorun sayılır."""
    d = derle(olaylar_yol, durum_yol)
    if d is None:
        return None, [], []
    _durum_yaz(durum_yol, d)
    sorunlar, uyarilar = [], []
    if teslim_oncesi:
        uyarilar.append("teslim-öncesi kip: adım 9 (KONTROL) / adım 10 (KAPANIŞ) BEKLIYOR "
                         "durumu bu denetimde sorun SAYILMADI (bunlar tanım gereği teslimden "
                         "SONRA kapanır — dairesel bağımlılık kırıcı, bkz. P0-5×P0-6).")
    for no in sorted(d["adimlar"], key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
        a = d["adimlar"][no]
        no_i = int(no) if str(no).lstrip("-").isdigit() else None
        for parca, p in a["parcalar"].items():
            if p["durum"] == "BEKLIYOR":
                if teslim_oncesi and no_i in (9, 10):
                    continue
                sorunlar.append(f"adım {no} ({a['ad']}) / {parca}: statü YOK (sessiz atlama?)")
            elif p["durum"] == "UYGULANDI":
                if not p["kanit"] or len(p["kanit"]) < MIN_KANIT:
                    sorunlar.append(f"adım {no} / {parca}: UYGULANDI ama kanıt yetersiz")
                elif (parca in SCRIPTLI and "script" not in p["kanit"].lower()
                      and ".py" not in p["kanit"].lower()):
                    uyarilar.append(f"adım {no} / {parca}: script'li parça, kanıtta script izi yok")
                if p.get("serh"):
                    uyarilar.append(f"adım {no} / {parca}: ⚠ ŞERHLİ UYGULANDI — "
                                     f"{p.get('serh_metni') or ''}")
            elif p["durum"] == "YUKLENEMEDI":
                uyarilar.append(f"adım {no} / {parca}: fiziken yüklenemedi — çıktıda açıkça belirtilmeli")
    for k, p in d["katmanlar"].items():
        if p["durum"] == "BEKLIYOR":
            sorunlar.append(f"katman {k}: statü YOK (kalıcı katman 'gereksiz' olamaz; somut çıktısı kaydedilmeli)")
    # D5: araç hataları --denetle'yi TEK BAŞINA bloklamaz (alternatif kaynakla iş fiilen
    # tamamlanmış olabilir) ama GÖRÜNÜR uyarı olarak HER ZAMAN basılır — sessiz-atlama YOK.
    arac_hatalari = d.get("arac_hatalari") or []
    for h in arac_hatalari:
        konum = f" (adım {h.get('adim')}/{h.get('parca')})" if h.get("adim") is not None else ""
        uyarilar.append(f"ARAÇ ÇÖKTÜ — teyitsiz: {h.get('arac')}{konum} · hata: {h.get('hata')}")
    # P0-5(d) — TESLİM MAKBUZU bütünlüğü (bkz. _makbuz_denetim_hesapla).
    makbuz_sorun = makbuz_uyari = None
    if makbuz_kontrolu:
        makbuz_sorun, makbuz_uyari = _makbuz_denetim_hesapla(kok, d)
        if makbuz_sorun:
            sorunlar.append(makbuz_sorun)
        if makbuz_uyari:
            uyarilar.append(makbuz_uyari)
    # P0-5 DÜZELTME(a) — ad-bağımsız "makbuzsuz dilekçe adayı" uyarısı.
    # DÜZELTME (v0.5.5 şerh turu — Ş10 KÜÇÜK, çift-basım): `_makbuz_denetim_
    # hesapla` (adım-9 uyum kolu) BU AYNI mesajı (bkz. `_adim9_teslim_
    # makbuzu_uyumu` içindeki `mesaj = _dilekce_sekilli_makbuzsuz_uyarisi`)
    # zaten `makbuz_sorun`/`makbuz_uyari` içine gömmüş olabilir — o zaman
    # burada BAĞIMSIZ bir uyarı olarak İKİNCİ KEZ eklemek yalnız gürültü
    # DEĞİL, hook parmak izine (`_hook_cikti_degisti_mi`) aynı bilginin iki
    # kez girmesi demektir. Zaten (sorun VEYA uyarı olarak) mevcutsa bastırılır.
    dilekce_uyari = _dilekce_sekilli_makbuzsuz_uyarisi(kok)
    if dilekce_uyari and dilekce_uyari not in (makbuz_sorun or "") and dilekce_uyari not in (makbuz_uyari or ""):
        uyarilar.append(dilekce_uyari)
    # P0-5 DÜZELTME(a) sinav-turu — "udf_yaz üretimi = TESLİM olayı" (advisory).
    udf_uyari = _udf_makbuzsuz_uyarisi(kok)
    if udf_uyari:
        uyarilar.append(udf_uyari)
    # Gate G — KALICILIK KAPISI: tam_tur.py bu kökte kullanılmışsa, pipeline
    # "analiz tamamlandi" damgasını tam_tur'un KENDİ mekanik sinyali olmadan
    # vuramaz (bkz. _gate_g_kalicilik_denetle). tam_tur hiç kullanılmamışsa
    # sessizce atlanır (defter kapısıyla simetrik).
    gate_g_sorun, gate_g_uyari = _gate_g_kalicilik_denetle(kok, atla=gate_g_atla)
    if gate_g_sorun:
        sorunlar.append(gate_g_sorun)
    if gate_g_uyari:
        uyarilar.append(gate_g_uyari)
    # P1-9(b) DÜZELTME — sözleşme-dışı dizin (gölge hat) bekçisi artık yalnız
    # DURUM.md'de değil, --denetle/--goster STDOUT'unda da GÖRÜNÜR (ve
    # dolayısıyla P1-8 KAPANIŞ Gate'in devir notunda da) — "gölge hat bir daha
    # SESSİZ olamaz". Advisory: sorunlar'a DEĞİL, uyarilar'a eklenir.
    sozlesme_disi = _sozlesme_disi_dizinler(kok)
    if sozlesme_disi:
        uyarilar.append(
            "SÖZLEŞME-DIŞI DİZİN(LER): " + ", ".join(f"_oa/{ad}" for ad in sozlesme_disi)
            + " — beklenmeyen konum (gölge hat/dağınık-çıktı adayı olabilir).")
    # E4 (v0.5.5.1) — bekçinin kör noktası: _oa/ KÖKÜNDEKİ serbest DOSYALAR.
    kok_dosya = _sozlesme_disi_kok_dosyalari(kok)
    if kok_dosya:
        uyarilar.append(
            "SÖZLEŞME-DIŞI KÖK DOSYA(LAR): " + ", ".join(f"_oa/{ad}" for ad in kok_dosya)
            + " — _oa/ kökü defter/analiz/cikti/metin/teyit dizinlerine aittir; "
              "bu dosyalar ya ilgili dizine taşınmalı ya da beyaz listeye alınmalıdır.")
    # E2 (v0.5.5.1) — elle yazılmış kütük satırının erken görünürlüğü.
    denge_uyari = _defter_muhakeme_dengesi_uyarisi(kok)
    if denge_uyari:
        uyarilar.append(denge_uyari)
    # P1-10 — bayat working-memory de aynı görünürlük genişlemesini alır
    # (isle()'daki blokleyici kapı ile AYNI kaynak fonksiyon, burada advisory).
    bayat = _bayat_md_uyarisi(kok)
    if bayat:
        uyarilar.append(bayat)
    # P2-13 — post-hoc kayıt dedektörü (advisory, exit kodunu ASLA değiştirmez).
    uyarilar.extend(_posthoc_kayit_uyarilari(kok, d))
    # GÖREV C(1) — DAL UYUŞMAZLIĞI: --isle/--katman anındaki tekil uyarıyla
    # AYNI kaynak fonksiyon üzerinden kalıcı görünürlük (--denetle/--goster/
    # DURUM.md hepsi buradan geçer) — advisory, sorunlar'a DEĞİL uyarilar'a.
    uyarilar.extend(_dal_uyusmazlik_uyarilari(kok, d))
    return d, sorunlar, uyarilar


def denetle_calistir(kok, gate_g_atla=False, makbuz_kontrolu=True, teslim_oncesi=False):
    """İN-PROCESS denetim arayüzü — CLI'siz, subprocess'siz (P0-4). tam_tur.py'nin
    `_defter_denetle`'i VE `teslim_paketi.py`'nin (d) adımı `sys.executable
    pipeline_kayit.py --denetle` subprocess'i KOŞTURMAK YERİNE bu fonksiyonu
    doğrudan çağırır. Döner: (temiz:bool, cikti:str) — eski subprocess+stdout
    sözleşmesiyle UYUMLU (çağıran tarafın ayrıştırma mantığı değişmez).
    `makbuz_kontrolu=False` / `teslim_oncesi=True` — YALNIZ `teslim_paketi.py`'nin
    (d) çağrısında BİRLİKTE kullanılır (bkz. `_denetle_hesapla` docstring —
    dairesel bağımlılık kırıcı)."""
    olaylar_yol, durum_yol = _yollar(argparse.Namespace(kok=kok, yol=None))
    d, sorunlar, uyarilar = _denetle_hesapla(kok, olaylar_yol, durum_yol,
                                              gate_g_atla=gate_g_atla,
                                              makbuz_kontrolu=makbuz_kontrolu,
                                              teslim_oncesi=teslim_oncesi)
    if d is None:
        return False, f"HATA: defter bulunamadı: {olaylar_yol} — önce --baslat ile aç."
    try:
        # P0-7 KUCUK-düzeltme (sinav-turu): DURUM.md HER ZAMAN kanonik (tam
        # güçte, varsayılan parametreli) bir denetimden türetilir — teslim_paketi/
        # tam_tur'un ÖZEL-amaçlı (gate_g_atla/makbuz_kontrolu/teslim_oncesi
        # değiştirilmiş) çağrılarında bu üçlü YENİDEN KULLANILAMAZ (DURUM.md'nin
        # gördüğü tablo hafifletilmiş olurdu). YALNIZ tam varsayılan parametrelerle
        # (ör. --hook-denetle'nin `denetle_calistir(kok)` çağrısı) yukarıda zaten
        # hesaplanmış üçlü DURUM.md'ye de aktarılır — aynı hesaplama tur başına
        # İKİ KEZ (bir kez burada, bir kez _durum_md_yaz içinde) koşmaz.
        kanonik = not gate_g_atla and makbuz_kontrolu and not teslim_oncesi
        _durum_md_yaz(kok, onceden_hesaplanan=(d, sorunlar, uyarilar) if kanonik else None)
    except Exception:
        pass
    satirlar = []
    if uyarilar:
        satirlar.append("UYARILAR:")
        satirlar += [f"  ⚠ {u}" for u in uyarilar]
    if sorunlar:
        satirlar.append("TESLİM ENGELİ — boşluklu tur teslim edilemez:")
        satirlar += [f"  ✗ {s}" for s in sorunlar]
    else:
        satirlar.append("DENETİM TEMİZ: tüm adımlar ve katmanlar kanıtlı statüde.")
    return (not sorunlar), "\n".join(satirlar)


def denetle(args):
    olaylar_yol, durum_yol = _yollar(args)
    d, sorunlar, uyarilar = _denetle_hesapla(getattr(args, "kok", None), olaylar_yol, durum_yol)
    if d is None:
        sys.exit(f"HATA: defter bulunamadı: {olaylar_yol} — önce --baslat ile aç.")
    _durum_md_yaz(getattr(args, "kok", None))
    if uyarilar:
        print("UYARILAR:")
        for u in uyarilar:
            print("  ⚠ " + u)
    if sorunlar:
        print("TESLİM ENGELİ — boşluklu tur teslim edilemez:")
        for s in sorunlar:
            print("  ✗ " + s)
        sys.exit(1)
    print("DENETİM TEMİZ: tüm adımlar ve katmanlar kanıtlı statüde. "
          "(Bu, içeriğin doğruluğunu değil, işletimin eksiksizliğini garanti eder — "
          "içerik denetimi oa-kontrol'ündür.)")


# ═════════════════════════════════════════════════════════════════════════
# P0-8 (v0.5.5) — DURUM.md TÜRETİMİ: pipeline_kayit.py HER olayda _oa/DURUM.md'yi
# fiziksel kanıttan ATOMİK üretir. "Elle düzenlenmez" — bu bloğun DIŞINDA
# hiçbir yazar yoktur (tek-yazar kuralı). Defter yoksa sessizce çıkar (mevcut
# 'defter kullanmayan akış bloklanmaz' simetrisi). Her çağrı noktası bu
# fonksiyonu try/except ile sarar — DURUM.md üretimi ASLA ana operasyonu
# (isle/katman/denetle/...) bloklamaz/başarısız kılmaz.
# ═════════════════════════════════════════════════════════════════════════

def _kutuk_dilekce_sayaci(kok):
    """(kutuk_n, dilekce_n) — künye teyit kütüğü satır sayısı VS en yeni
    dilekçe-şekilli _oa/cikti dosyasındaki (yaklaşık) tekil esas/karar atfı
    sayısı. Dilekçedeki atıf kütükten FAZLAYSA teyitsiz atıf sızmış olabilir
    (advisory sayaç — hukuki karar değil, mekanik gözlem)."""
    kutuk = os.path.join(kok, "_oa", "teyit", "kunye-teyit.md")
    kutuk_n = 0
    if os.path.isfile(kutuk):
        try:
            with open(kutuk, encoding="utf-8", errors="replace") as f:
                for satir in f:
                    s = satir.strip()
                    if s.startswith("|") and not s.lower().lstrip("|").strip().startswith("zaman"):
                        kutuk_n += 1
        except OSError:
            pass
    cdiz = os.path.join(kok, "_oa", "cikti")
    dilekce_n = 0
    if os.path.isdir(cdiz):
        atif_re = re.compile(r"\bE\.?\s*\d{4}\s*/\s*\d+")
        for ad in os.listdir(cdiz):
            yol = os.path.join(cdiz, ad)
            if not os.path.isfile(yol):
                continue
            try:
                with open(yol, encoding="utf-8", errors="replace") as f:
                    icerik = f.read()
            except OSError:
                continue
            if _DILEKCE_DESEN.search(icerik):
                dilekce_n += len(set(atif_re.findall(icerik)))
    return kutuk_n, dilekce_n


def _vakia_delilsiz_unsur_uyarisi(kok):
    """M4 (Paket D, v0.5.5) — UNSUR ŞABLONLARI: `oa-vakia/scripts/vakia_matris.py
    --dogrula ... --json <yol>` çıktısındaki `ispat_bosluklari` (delilsiz
    iddia/unsur id'leri) `_oa/cikti/*vakia*.json` dosyalarından toplanır.
    Bu bir hukuki değerlendirme DEĞİLDİR — yalnız oa-vakia'nın KENDİ ürettiği
    JSON'u okur (DURUM.md salt-okur; ikinci bir denetim mantığı İCAT ETMEZ).
    Dosya yok/okunamaz/beklenmedik şemalıysa SESSİZCE boş liste döner (bu
    advisory bir renderer alanıdır, asla çökmez)."""
    cdiz = os.path.join(kok, "_oa", "cikti")
    if not os.path.isdir(cdiz):
        return []
    uyarilar = []
    for yol in sorted(glob.glob(os.path.join(cdiz, "*vakia*.json"))):
        try:
            with open(yol, encoding="utf-8", errors="replace") as f:
                m = json.load(f)
        except Exception:
            continue
        if not isinstance(m, dict):
            continue
        bosluklar = m.get("ispat_bosluklari") or []
        if not bosluklar:
            continue
        ad = os.path.relpath(yol, kok)
        for iid in bosluklar:
            uyarilar.append(f"{ad}: unsur/iddia '{iid}' — DESTEKLEYİCİ DELİL YOK")
    return uyarilar


def _sozlesme_disi_dizinler(kok):
    """_oa/ altında DIZIN_BEYAZ_LISTE dışı klasörler — gölge-hat/dağınık-
    çıktı adayı (advisory; asla blokleyici değil)."""
    oa = os.path.join(kok, "_oa")
    if not os.path.isdir(oa):
        return []
    try:
        return sorted(ad for ad in os.listdir(oa)
                      if os.path.isdir(os.path.join(oa, ad)) and ad not in DIZIN_BEYAZ_LISTE)
    except OSError:
        return []


# ── E4 (v0.5.5.1) — KÖK DOSYA BEKÇİSİ ───────────────────────────────────────
# P1-9(b) bekçisi yalnız _oa/ altındaki DİZİNlere bakıyordu; kökteki serbest
# DOSYALAR onun kör noktasıydı (İsmail Gümüş saha koşusunda `sureler.json`,
# `dosya.md`, `README.md` orada duruyordu ve hiçbir sinyal üretmiyordu).
# Advisory — bloklamaz: amaç çizgisi gereği görünürlük yeter, muhakemeyi
# durduran bir kapı EKLENMEZ.
KOK_DOSYA_BEYAZ_LISTE = {
    "dosya.md", "README.md", "DURUM.md", "sureler.json",
    ".oturum-kilidi", ".gitignore",
}


def _sozlesme_disi_kok_dosyalari(kok):
    """_oa/ KÖKÜNDEKİ (dizin DEĞİL) beyaz-liste dışı dosyalar — dağınık-çıktı
    adayı (advisory)."""
    oa = os.path.join(kok or ".", "_oa")
    if not os.path.isdir(oa):
        return []
    try:
        return sorted(ad for ad in os.listdir(oa)
                      if os.path.isfile(os.path.join(oa, ad))
                      and ad not in KOK_DOSYA_BEYAZ_LISTE)
    except OSError:
        return []


# ── E2 (v0.5.5.1) — DEFTER-MUHAKEME SAYIM DENGESİ ───────────────────────────
# `oa_hafiza.py teyit --damga` kütük satırını (DAMGA=<sınıf>) ve muhakeme
# bölümünü (**DAMGA:**) TEK komutta, birlikte yazar — ikisi zorunlu olarak eşit
# sayıda olur. Saha koşusunda kütükte DAMGA'lı satırlar vardı ama HİÇBİR
# muhakeme bölümü yoktu: satırlar script DIŞINDA (elle) eklenmişti, yani o
# künyelerin İLGİLİ-KISIM/DAVAYA-BAĞ muhakemesi hiç yapılmamıştı. Bu, teslim
# kapısının (ictihat_muhakeme_denetim.py) çok geç fark ettiği bir kopukluktur;
# burası ERKEN ve GÖRÜNÜR uyarıdır — advisory, exit kodunu değiştirmez.
_KUTUK_DAMGA_DESEN = re.compile(r"DAMGA\s*=\s*[A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜ\-]*")
_MUHAKEME_DAMGA_DESEN = re.compile(r"^\*\*DAMGA:\*\*", re.M)


def _defter_muhakeme_dengesi_uyarisi(kok):
    """Kütükteki DAMGA'lı satır sayısı > muhakeme bölümü sayısı ise uyarı
    metni, değilse None. ASLA istisna fırlatmaz."""
    try:
        kutuk = os.path.join(kok or ".", "_oa", "teyit", "kunye-teyit.md")
        if not os.path.isfile(kutuk):
            return None
        with open(kutuk, encoding="utf-8", errors="replace") as f:
            kutuk_metin = f.read()
        # Yalnız veri satırları (tablo gövdesi) — başlık/kural metni sayılmaz.
        kutuk_n = sum(1 for satir in kutuk_metin.split("\n")
                      if satir.lstrip().startswith("|") and _KUTUK_DAMGA_DESEN.search(satir))
        if kutuk_n == 0:
            return None
        muhakeme_n = 0
        desen = os.path.join(kok or ".", "_oa", "cikti", "*ictihat-muhakeme*.md")
        for yol in sorted(glob.glob(desen)):
            try:
                with open(yol, encoding="utf-8", errors="replace") as f:
                    muhakeme_n += len(_MUHAKEME_DAMGA_DESEN.findall(f.read()))
            except OSError:
                continue
        if muhakeme_n >= kutuk_n:
            return None
        return (f"DEFTER-MUHAKEME DENGESİZLİĞİ: kütükte DAMGA'lı {kutuk_n} satır var, "
                f"muhakeme kaydında yalnız {muhakeme_n} bölüm — {kutuk_n - muhakeme_n} künyenin "
                f"İLGİLİ-KISIM/DAVAYA-BAĞ muhakemesi YOK. `teyit --damga` ikisini birlikte "
                f"yazar; fark, satırın script DIŞINDA (elle) eklendiğini gösterir. Eksik "
                f"künyeler için `oa_hafiza.py teyit --damga ... --ilgili-kisim ... --bag ...` "
                f"koşulmadan bu atıflar dilekçeye teyitli olarak giremez.")
    except Exception:
        return None


# ── E5 (v0.5.5.1) — WORKING MEMORY TETİĞİ ───────────────────────────────────
# Saha koşusunda `dosya-analiz.md` 1.247 bayt ve 2 başlıktı; render motoru
# (tam_tur `_md_render`) 40 KB'lık çıktıyı kayıpsız gömüyor — yani motor
# sağlamdı, ÇAĞRILMAMIŞTI: modelin elle yazdığı dosya `--senkron`'un yerine
# geçmişti ve devirde working memory boş kalıyordu. Ders: kapının gücü
# kodunda değil TETİĞİNDE. Bu yüzden onarım artık ritüel beklemez — hook
# gövdesinden İN-PROCESS koşar. TAMAM ÜRETMEZ (Gate G+ fail-closed kalır);
# yalnız kaybolan working memory'yi birincil kaynaklardan geri getirir.
def _analiz_md_kendini_onar(kok):
    """tam_tur bu kökte kullanılmışsa (`dosya-analiz.json` var) ve md
    yok/biçimi bozuksa `cmd_senkron`'u koşturur. Döner: uyarı metni | None.
    ASLA istisna fırlatmaz."""
    try:
        analiz_dizin = os.path.join(kok or ".", "_oa", "analiz")
        if not os.path.exists(os.path.join(analiz_dizin, "dosya-analiz.json")):
            return None          # tam_tur hiç kullanılmamış — sessizce atla (defter kapısıyla simetrik)
        tam_tur = _tam_tur_modulu()
        if tam_tur is None:
            return None
        md_yol = tam_tur._analiz_md(kok)
        try:
            with open(md_yol, encoding="utf-8", errors="replace") as f:
                icerik = f.read()
        except OSError:
            icerik = ""
        if tam_tur._iskelet_saglam_mi(icerik):
            return None          # biçim sağlam — dokunma
        onceki = len(icerik.encode("utf-8"))
        tam_tur.cmd_senkron(kok)
        try:
            yeni = os.path.getsize(md_yol)
        except OSError:
            yeni = 0
        return (f"WORKING MEMORY ONARILDI (otomatik --senkron): dosya-analiz.md bizim "
                f"biçimimizde DEĞİLDİ ({onceki:,} B — elle yazılmış/bozulmuş olabilir), "
                f"birincil kaynaklardan yeniden türetildi ({yeni:,} B). TAMAM işaretçisi "
                f"YAZILMADI — turu `tam_tur.py --kaydet` kapatır.")
    except Exception:
        return None


# P1-10 (v0.5.5) — CANLI-SENKRON KAPISI. Bayatlık HESABINDAN *ictihat-muhakeme*
# ve teyit-kaynaklı dosyalar HARİÇ tutulur (DÜZELTME — sinav 'senkron
# değirmeni' bulgusu): bu dosyalar zaten deterministik script çıktısıdır
# (P0-2 tek-komutu), model muhakemesi DEĞİLDİR; her `teyit --damga` sonrası
# zorunlu bir `--senkron` dayatmak working-memory'yi TEKDÜZE ŞİŞİRİR
# (kullanıcının analiz-token-verimliliği hedefiyle çatışır) ve tam_tur akışını
# gereksiz sıklıkta tetikler. 2sn TOLERANS — aynı-saniye NTFS mtime çözünürlüğü
# yanlış-pozitif üretmesin.
_BAYATLIK_HARIC_DESEN = re.compile(r"ictihat-muhakeme|teyit", re.I)
_BAYATLIK_TOLERANS_SN = 2


def _en_yeni_cikti_mtime(kok, haric_desen=_BAYATLIK_HARIC_DESEN):
    """_oa/cikti'daki (haric_desen'e uyan dosyalar HARİÇ) en yeni dosyanın
    mtime'ı; dizin yoksa/dosya yoksa None."""
    cdiz = os.path.join(kok or ".", "_oa", "cikti")
    if not os.path.isdir(cdiz):
        return None
    en_yeni = None
    try:
        for ad in os.listdir(cdiz):
            if haric_desen is not None and haric_desen.search(ad):
                continue
            yol = os.path.join(cdiz, ad)
            if os.path.isfile(yol):
                mt = os.path.getmtime(yol)
                if en_yeni is None or mt > en_yeni:
                    en_yeni = mt
    except OSError:
        return None
    return en_yeni


def _canli_senkron_bayat_mi(kok):
    """P1-10 — dosya-analiz.md (working memory), _oa/cikti'daki en yeni ÇALIŞMA
    EVRAKINDAN (*ictihat-muhakeme*/teyit dosyaları HARİÇ) mtime bazında
    ESKİYSE (2sn toleransla) sorun metnini döndürür. Kontrol YALNIZ diskten
    okur (subprocess/tam_tur çağrısı YOK — P0-5 tasarım kuralı). Tetik şartı:
    `_oa/analiz/dosya-analiz.json` VAR (tam_tur akışı fiilen kullanılmış) —
    yoksa (tam_tur'suz akışlar) kontrol TAMAMEN atlanır (None)."""
    kok_ = kok or "."
    analiz_md = os.path.join(kok_, "_oa", "analiz", "dosya-analiz.md")
    analiz_json = os.path.join(kok_, "_oa", "analiz", "dosya-analiz.json")
    if not (os.path.isfile(analiz_md) and os.path.isfile(analiz_json)):
        return None
    en_yeni = _en_yeni_cikti_mtime(kok_)
    if en_yeni is None:
        return None
    try:
        md_mt = os.path.getmtime(analiz_md)
    except OSError:
        return None
    if md_mt < en_yeni - _BAYATLIK_TOLERANS_SN:
        return ("CANLI-SENKRON: working memory (dosya-analiz.md) _oa/cikti'daki en yeni "
                "çalışma evrakından BAYAT — `python tam_tur.py --senkron --kok .` koş "
                "(deterministik render, 0 model-token), sonra kaydet. UYARI: --senkron "
                "md'yi BİRİNCİL KAYNAKLARDAN YENİDEN TÜRETİR — md'ye elle yazdıysan "
                "içeriği ÖNCE _oa/cikti'ya taşı (eski md otomatik _oa/arsiv-yerel'e "
                "nüshalanır, kayıpsızlık korunur).")
    return None


# P2-13 (v0.5.5) — POST-HOC KAYIT DEDEKTÖRÜ (advisory — ASLA blokleyiciye
# yükselmez; üç tasarımın ortak yargısı). *TESLIM*/*FINAL* desenli dosya adı
# BASİT bir zaman-çapasıdır — P0-5'in İÇERİK-bazlı 'dilekçe-şekilli en yeni
# dosya' denetiminden AYRIDIR ve onun yerini TUTMAZ (P0-6 artefaktsız-
# UYGULANDI'yı görür, bu dedektör artefaktı-SONRADAN-yazılmış-UYGULANDI'yı).
def _teslim_dosya_mtime_en_yeni(kok):
    """_oa/cikti altında adında (case-insensitive) 'teslim' veya 'final' geçen
    en yeni dosyanın mtime'ı; hiç yoksa None."""
    cdiz = os.path.join(kok or ".", "_oa", "cikti")
    if not os.path.isdir(cdiz):
        return None
    en_yeni = None
    try:
        for ad in os.listdir(cdiz):
            if not re.search(r"teslim|final", ad, re.I):
                continue
            yol = os.path.join(cdiz, ad)
            if os.path.isfile(yol):
                mt = os.path.getmtime(yol)
                if en_yeni is None or mt > en_yeni:
                    en_yeni = mt
    except OSError:
        return None
    return en_yeni


def _posthoc_kayit_uyarilari(kok, d):
    """P2-13 — bir adımın UYGULANDI zaman damgası *TESLIM*/*FINAL* desenli
    dosyanın mtime'ından SONRAYSA GÖRÜNÜR (advisory) uyarı üretir. mtime
    git-checkout/kopyalama/OneDrive ile oynayabildiğinden bu ASLA exit kodunu
    değiştirmez — yalnız 'üretimin kaydı mı, kaydın üretimi mi' sorusunu
    görünür kılar."""
    if not d:
        return []
    teslim_mt = _teslim_dosya_mtime_en_yeni(kok)
    if teslim_mt is None:
        return []
    uyarilar = []
    for no in sorted(d.get("adimlar", {}),
                      key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
        a = d["adimlar"][no]
        for parca, p in a.get("parcalar", {}).items():
            if p.get("durum") != "UYGULANDI" or not p.get("zaman"):
                continue
            try:
                kayit_epoch = datetime.datetime.fromisoformat(p["zaman"]).timestamp()
            except Exception:
                continue
            fark = kayit_epoch - teslim_mt
            if fark > 1:   # 1sn tolerans (mtime/olay çözünürlüğü)
                uyarilar.append(
                    f"POST-HOC KAYIT: adım {no} ({a['ad']}) / {parca} kaydı TESLİM "
                    f"dosyasından {fark:.0f} sn SONRA düşülmüş — üretimin kaydı mı, "
                    "kaydın üretimi mi?")
    return uyarilar


def _bayat_md_uyarisi(kok):
    """DURUM.md advisory satırı — `_canli_senkron_bayat_mi` ile AYNI (tek
    kaynak) bayatlık hesabını kullanır; burada yalnız GÖRÜNÜRLÜK sağlar,
    `isle()`'daki blokleyici kapı AYRI bir çağrı ile kendi kararını verir."""
    return _canli_senkron_bayat_mi(kok)


def _ocr_bos_uyarisi(kok):
    """P0-9 (v0.5.5) OCR-NÖBETÇİSİ — `_oa/metin/00-kunye.json`'daki 'ocr_durum'
    damgalı ('OCR-BOŞ → GÖRSEL İNCELEME GEREK') kayıtları DURUM.md'ye görünür
    kılar. Bu bir hukuki değerlendirme DEĞİLDİR — yalnız oa_ingest'in KENDİ
    ürettiği künyeyi okur (DURUM.md salt-okur, ikinci bir denetim mantığı İCAT
    ETMEZ). Dosya yok/okunamaz/beklenmedik şemalıysa SESSİZCE boş liste döner
    (advisory bir renderer alanıdır, asla çökmez)."""
    yol = os.path.join(kok, "_oa", "metin", "00-kunye.json")
    if not os.path.isfile(yol):
        return []
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            kunye = json.load(f)
    except Exception:
        return []
    if not isinstance(kunye, dict):
        return []
    uyarilar = []
    for k in kunye.get("kayitlar", []) or []:
        if not isinstance(k, dict) or not k.get("ocr_durum"):
            continue
        sayfalar = k.get("ocr_bos_sayfalar") or []
        sayfa_s = ", ".join(str(s) for s in sayfalar) if sayfalar else "?"
        uyarilar.append(f"{k.get('kaynak') or k.get('md') or '(adsız)'}: {k.get('ocr_durum')} "
                         f"(sayfa {sayfa_s}) — görsel: `_oa/metin/{k.get('gorsel_klasor') or '?'}`")
    return uyarilar


def _avukat_karari_bekleyen(d):
    """BILGI-EKSIK ve ŞERHLİ UYGULANDI kalemleri — model KARAR VEREMEZ,
    avukatın gözden geçirmesi gerekenler listesi (mekanik derleme). M7
    (Paket D, v0.5.5): bir çatal `--avukat-karari` ile ÇÖZÜLMÜŞSE (aynı
    adım+parça/katman için kayıtlı bir karar varsa) burada ARTIK GÖRÜNMEZ —
    çözüm `d['avukat_kararlari']`de KALICI kalır (DURUM.md'nin ayrı bölümü),
    bekleyen liste yalnız GERÇEKTEN AÇIK çatalları gösterir."""
    kararlar = d.get("avukat_kararlari") or []
    kalemler = []
    for no in sorted(d["adimlar"], key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
        a = d["adimlar"][no]
        for parca, p in a["parcalar"].items():
            if _avukat_karari_cozulmus_mu(kararlar, adim=no, parca=parca,
                                          zaman=p.get("zaman"), sira=p.get("_sira")):
                continue
            if p["durum"] == "BILGI-EKSIK":
                kalemler.append(f"adım {no} ({a['ad']}) / {parca}: BİLGİ EKSİK — {p.get('kanit') or ''}")
            elif p.get("serh"):
                kalemler.append(f"adım {no} ({a['ad']}) / {parca}: ŞERHLİ UYGULANDI — "
                                 f"{p.get('serh_metni') or ''}")
    for k, p in d["katmanlar"].items():
        if _avukat_karari_cozulmus_mu(kararlar, katman=k, zaman=p.get("zaman"), sira=p.get("_sira")):
            continue
        if p["durum"] == "BILGI-EKSIK":
            kalemler.append(f"katman {k}: BİLGİ EKSİK — {p.get('kanit') or ''}")
    return kalemler


def _avukat_karari_hedefi_acik_mi(d, adim=None, parca=None, katman=None):
    """DÜZELTME (v0.5.5 şerh turu — Ş14 KUCUK): `--avukat-karari` hedefinin
    (adım+parça VEYA katman) `_avukat_karari_bekleyen` listesinde GERÇEKTEN
    AÇIK bir çatal olarak bulunup bulunmadığını söyler — `_avukat_karari_
    kaydet` olay yazmadan ÖNCE bunu çağırıp sonucu bir UYARIYA çevirir
    (BLOKLAMAZ — kayıpsızlık/append-only bozulmasın, meşru 'önden karar'
    senaryosu da kapanmasın; yalnız yanıltıcı 'kaydedildi' başarısı
    nitelendirilir). `_avukat_karari_bekleyen` ile AYNI 'açık mı' mantığını
    (BILGI-EKSIK veya çözülmemiş ŞERHLİ UYGULANDI) TEK bir hedef için koşar
    (tek-yazar kuralı — ikinci bir kural kümesi İCAT EDİLMEZ)."""
    kararlar = d.get("avukat_kararlari") or []
    if katman is not None:
        p = d.get("katmanlar", {}).get(katman)
        if p is None:
            return False
        if _avukat_karari_cozulmus_mu(kararlar, katman=katman, zaman=p.get("zaman"),
                                       sira=p.get("_sira")):
            return False
        return p.get("durum") == "BILGI-EKSIK"
    no = str(adim)
    a = d.get("adimlar", {}).get(no)
    if a is None:
        return False
    p = a.get("parcalar", {}).get(parca)
    if p is None:
        return False
    if _avukat_karari_cozulmus_mu(kararlar, adim=no, parca=parca, zaman=p.get("zaman"),
                                   sira=p.get("_sira")):
        return False
    return p.get("durum") == "BILGI-EKSIK" or bool(p.get("serh"))


def _siradaki(d):
    """Sıradaki ilk BEKLIYOR adım/parça (yoksa katman) — MEKANİK gözlem,
    hukuki karar DEĞİL."""
    for no in sorted(d["adimlar"], key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
        a = d["adimlar"][no]
        for parca, p in a["parcalar"].items():
            if p["durum"] == "BEKLIYOR":
                return f"adım {no} ({a['ad']}) / {parca}"
    for k, p in d["katmanlar"].items():
        if p["durum"] == "BEKLIYOR":
            return f"katman {k}"
    return "tüm adım/katmanlar işlenmiş — teslim_paketi.py ile teslim denetimini koş."


def _durum_md_yaz(kok, onceden_hesaplanan=None):
    """P0-8 — _oa/DURUM.md'yi fiziksel kanıttan ATOMİK türetir. Defter yoksa
    sessizce çıkar; herhangi bir hata bu fonksiyonun İÇİNDE yutulur (çağıran
    hiçbir zaman bu yüzden çökmez — bkz. blok-üstü not).

    `onceden_hesaplanan` — sinav-turu KUCUK-düzeltme (P0-7 performans notu):
    `(d, sorunlar, uyarilar)` üçlüsü ÖNCEDEN (varsayılan/kanonik parametrelerle)
    hesaplanmışsa `denetle_calistir` bunu doğrudan geçirir — aynı hesaplama
    (disk taraması + kapı denetimleri) tur başına İKİ KEZ koşmaz. Verilmezse
    (çoğu çağıran yol: isle/katman/goster/baslat/arac_hata) burada YENİDEN
    (kanonik/varsayılan parametrelerle) hesaplanır — mevcut davranış değişmez."""
    try:
        kok = os.path.abspath(kok or ".")
        olaylar_yol, durum_yol_hesap = _yollar(argparse.Namespace(kok=kok, yol=None))
        if onceden_hesaplanan is not None:
            d, sorunlar, uyarilar = onceden_hesaplanan
        else:
            d, sorunlar, uyarilar = _denetle_hesapla(kok, olaylar_yol, durum_yol_hesap)
        if d is None:
            return
        satirlar = []
        satirlar.append("<!-- BU DOSYA pipeline_kayit.py TARAFINDAN TÜRETİLİR — ELLE DÜZENLENMEZ. -->")
        satirlar.append(f"# DURUM — {d.get('dosya') or '(adsız)'}")
        satirlar.append(f"_Türetim zamanı: {simdi()}_  ·  _oluşturma: {d.get('olusturma') or '—'}_")
        satirlar.append("")
        # Görev A — DEFTER BÜTÜNLÜĞÜ: her olayın araç-imzalı/model-beyanlı
        # dağılımı GÖRÜNÜR sayılır. BLOKLAMAZ — yalnız ayırt eder (bkz. AMAÇ
        # ÇİZGİSİ kabul kuralı, 2026-07-29).
        arac_n, model_n = _defter_imza_sayaci(olaylar_yol)
        satirlar.append("## Defter Bütünlüğü")
        satirlar.append(f"- defter: {arac_n} araç-imzalı, {model_n} model-beyanlı"
                         + ("  (imzasız/elle düşürülmüş satır var — bloklanmadı, yalnız işaretlendi)"
                            if model_n else ""))
        # DÜZELTME (hakem düzeltme turu 1, madde 1) — imza algoritması
        # anahtarsızdır/kaynak kodda açıktır; bu SINIR daha önce yalnız kod
        # yorumunda yazılıyordu, avukata görünür değildi. Koşulsuz (her
        # zaman) basılır — bu bir UYARI değil, kalıcı tek satırlık
        # dokümantasyondur (gürültü sayılmaz).
        satirlar.append("- _araç-imzalı, aracın (pipeline_kayit.py CLI'sinin) "
                         "çağrıldığına dair ZAYIF (anahtarsız) bir işarettir; "
                         "kasıtlı taklidi engellemez — amaç ayırt etmek, "
                         "delil üretmek değildir._")
        satirlar.append("")
        satirlar.append("## Adım Tablosu")
        for no in sorted(d["adimlar"], key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
            a = d["adimlar"][no]
            try:
                adim_i = int(no)
            except (TypeError, ValueError):
                adim_i = None
            for parca, p in a["parcalar"].items():
                isaret = {"UYGULANDI": "✓", "GEREKSIZ": "−", "BILGI-EKSIK": "?",
                          "YUKLENEMEDI": "!", "BEKLIYOR": "⬜"}.get(p["durum"], "?")
                serh_bayrak = " ⚠ŞERHLİ" if p.get("serh") else ""
                beyan_var = p["durum"] != "BEKLIYOR"
                imza_etiket = ""
                if beyan_var:
                    imza_etiket = "  [araç-imzalı]" if p.get("arac_imzali") else "  [model-beyanlı]"
                fiziksel_etiket = ""
                if adim_i is not None:
                    artefakt_var = _adim_artefakt_var_mi(kok, adim_i, parca)
                    hal = _fiziksel_hal(beyan_var, artefakt_var)
                    if hal is not None:
                        # KUCUK-DÜZELTME (hakem düzeltme turu 1, madde 2/
                        # bulgu 3) — 'artefakt YOK' durumunda HANGİ ayağın
                        # eksik olduğu etikete eklenir (avukat mevcut başka
                        # dosyaları görüp etiketi 'yanlış' sanmasın diye).
                        ek = ""
                        if beyan_var and artefakt_var is False:
                            eksik_metni = _adim_artefakt_eksik_metni(kok, adim_i, parca)
                            if eksik_metni:
                                ek = f" — eksik: {eksik_metni}"
                        fiziksel_etiket = f"  [FİZİKSEL: {hal}{ek}]"
                satirlar.append(f"- {isaret} adım {no} ({a['ad']}) / {parca}: {p['durum']}"
                                 f"{serh_bayrak}{imza_etiket}{fiziksel_etiket}")
        satirlar.append("")
        satirlar.append("## Katmanlar")
        for k, p in d["katmanlar"].items():
            beyan_var = p["durum"] != "BEKLIYOR"
            imza_etiket = ""
            if beyan_var:
                imza_etiket = "  [araç-imzalı]" if p.get("arac_imzali") else "  [model-beyanlı]"
            satirlar.append(f"- {k}: {p['durum']}{imza_etiket}")
        satirlar.append("")
        satirlar.append("## Kapı Durumu")
        if not sorunlar and not uyarilar:
            satirlar.append("- Tüm kapılar temiz (sorun/uyarı yok).")
        for s in sorunlar:
            satirlar.append(f"- ✗ {s}")
        for u in uyarilar:
            satirlar.append(f"- ⚠ {u}")
        satirlar.append("")
        kutuk_n, dilekce_n = _kutuk_dilekce_sayaci(kok)
        satirlar.append("## Kütük-vs-Dilekçe Künye Sayacı")
        satirlar.append(f"- Kütük satırı (teyitli): {kutuk_n}")
        satirlar.append(f"- Dilekçedeki tekil atıf (yaklaşık): {dilekce_n}")
        if dilekce_n > kutuk_n:
            satirlar.append("- ⚠ dilekçedeki atıf sayısı kütük satırından FAZLA — "
                             "teyitsiz atıf sızmış olabilir.")
        satirlar.append("")
        dokum_n, muhakeme_n, makbuz_durum = _dokum_muhakeme_makbuz_sayaclari(kok)
        satirlar.append("## Döküm / Muhakeme / Makbuz Sayaçları")
        satirlar.append(f"- Döküm (_oa/teyit/dokum/): {dokum_n} dosya")
        satirlar.append(f"- İçtihat muhakeme kaydı (_oa/cikti/*ictihat-muhakeme*): {muhakeme_n} dosya")
        satirlar.append(f"- Teslim makbuzu: {makbuz_durum}")
        satirlar.append("")
        sozlesme_disi = _sozlesme_disi_dizinler(kok)
        if sozlesme_disi:
            satirlar.append("## Sözleşme-Dışı Dizin Uyarısı")
            for ad in sozlesme_disi:
                satirlar.append(f"- ⚠ _oa/{ad} sözleşme dışı bir dizin (beklenmeyen konum — gölge hat olabilir).")
            satirlar.append("")
        bayat = _bayat_md_uyarisi(kok)
        if bayat:
            satirlar.append("## Bayat Working-Memory Uyarısı")
            satirlar.append(f"- ⚠ {bayat}")
            satirlar.append("")
        ocr_bos = _ocr_bos_uyarisi(kok)
        if ocr_bos:
            satirlar.append("## 🔴 OCR-BOŞ Uyarısı (P0-9 OCR-NÖBETÇİSİ)")
            for u in ocr_bos:
                satirlar.append(f"- 🔴 {u}")
            satirlar.append("")
        delilsiz_unsur = _vakia_delilsiz_unsur_uyarisi(kok)
        if delilsiz_unsur:
            satirlar.append("## 🔴 Delilsiz Unsur Uyarısı (Vakıa — M4, Paket D)")
            for u in delilsiz_unsur:
                satirlar.append(f"- 🔴 {u}")
            satirlar.append("")
        akb = _avukat_karari_bekleyen(d)
        satirlar.append("## Avukat Kararı Bekleyen")
        if akb:
            for k in akb:
                satirlar.append(f"- {k}")
        else:
            satirlar.append("- (yok)")
        satirlar.append("")
        avukat_kararlari = d.get("avukat_kararlari") or []
        if avukat_kararlari:
            satirlar.append("## Avukat Kararları (Kayıtlı — M7, Paket D)")
            for k in avukat_kararlari:
                hedef_str = (f"katman {k.get('katman')}" if k.get("katman")
                             else f"adım {k.get('adim')} / {k.get('parca')}")
                satirlar.append(f"- {hedef_str}: **{k.get('karar')}**"
                                 + (f" — gerekçe: {k.get('gerekce')}" if k.get("gerekce") else "")
                                 + f"  _({k.get('zaman')})_")
            satirlar.append("")
        satirlar.append("## Sıradaki")
        satirlar.append(f"- {_siradaki(d)}")
        satirlar.append("")
        satirlar.append("<!-- elle düzenlenmez — pipeline_kayit.py türetir -->")
        icerik = "\n".join(satirlar) + "\n"
        hedef = os.path.join(kok, "_oa", "DURUM.md")
        ust = os.path.dirname(hedef)
        if ust:
            os.makedirs(ust, exist_ok=True)
        tmp = f"{hedef}.tmp.{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(icerik)
        os.replace(tmp, hedef)
    except Exception as e:
        try:
            print(f"UYARI: _oa/DURUM.md türetilemedi ({e}) — ana işlem etkilenmedi.",
                  file=sys.stderr)
        except Exception:
            pass


# ═════════════════════════════════════════════════════════════════════════
# P0-7 (v0.5.5) — MODEL-BAĞIMSIZ TETİK: `--hook-denetle`, plugin Stop/
# SessionEnd hook'unun çağırdığı komuttur (bkz. hooks/hooks.json). Zincirin
# ucu artık modelin GÖNÜLLÜ çağrısına bağlı değildir — oturum kapanınca
# harness bunu KENDİSİ çalıştırır. `_oa/defter` bu kökte YOKSA SESSİZCE
# `exit 0` (bu dosya pipeline defteri kullanmıyor); VARSA `denetle_calistir`
# (in-process, Gate-G+makbuz dahil) VE `oa_metrik.hesapla` (in-process,
# subprocess YOK — P0-4/P0-5'teki 'kapı başka kapıyı subprocess ile çağırmaz'
# ilkesiyle simetrik) çağrılır; özet stdout'a VE (bu çağrının kendisi zaten
# tetiklediği) `_oa/DURUM.md`'ye yazılır. TÜM gövde try/except ile sarılıdır:
# ASLA bloklamaz, ASLA exit≠0 dönmez (hook sözleşmesi) — hızlı ve hataya
# dayanıklıdır (yalnız disk okuma + JSON ayrıştırma, ağır iş yok).
# ═════════════════════════════════════════════════════════════════════════

def _oa_metrik_modulu():
    betik = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oa_metrik.py")
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_oa_pipeline_metrik_inproc", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _oa_metrik_ozet_al(kok):
    """oa_metrik.py'yi İN-PROCESS çağırıp özet metnini döndürür (subprocess
    YOK). Herhangi bir hata KISA bir uyarı stringine çevrilir — hook'u
    ASLA çökertmez."""
    try:
        om = _oa_metrik_modulu()
        if om is None:
            return "(oa_metrik.py bulunamadı/import edilemedi — özet atlandı)"
        metrik = om.hesapla(kok)
        metrik["cikti"] = os.path.abspath(om._metrik_yolu(kok))
        try:
            ust = os.path.dirname(metrik["cikti"])
            if ust:
                os.makedirs(ust, exist_ok=True)
            with open(metrik["cikti"], "w", encoding="utf-8") as f:
                json.dump(metrik, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # metrik.json yazılamasa da özet basılabilir
        return om.ozet_yaz(metrik)
    except Exception as e:
        return f"(oa_metrik özeti alınamadı: {e})"


def _hook_son_iz_yolu(defter):
    return os.path.join(defter, ".hook-son-iz.json")


def _hook_cikti_degisti_mi(defter, cikti):
    """P0-7 DÜZELTME (Paket-B, sinav-turu BLOKER giderimi) — eski kısa devre
    yalnız `pipeline-olaylar.jsonl`'in boyut/mtime'ına bakıyordu; oysa
    `--hook-denetle`'nin ürettiği bulguların ÇOĞU (`_dilekce_sekilli_
    makbuzsuz_uyarisi`, `_udf_makbuzsuz_uyarisi`, `_makbuz_denetim_hesapla`,
    Gate G) DEFTERDEN TÜRETİLMEZ — model deftere HİÇ DOKUNMADAN (--isle
    çağırmadan) _oa/cikti'ya bir dilekçe veya kökte elden bir .udf yazarsa
    defter değişmez ve eski kısa devre kördü (saha kanıtlı bulgu).

    KÖKTEN çözüm: `denetle_calistir` (dolayısıyla `_durum_md_yaz`) HER
    ÇAĞRIDA KOŞULUR — DURUM.md hiçbir hook koşusunda bayat kalmaz. Kısa
    devre YALNIZ STDOUT BASIMINA uygulanır: önceki koşunun `--denetle`
    ÇIKTI METNİ (sorunlar+uyarılar; deterministik, zaman damgası TAŞIMAZ)
    ile bu koşununki bit-bit AYNIYSA basım bastırılır (gürültü azaltma,
    görünürlük kaybı YOK — herhangi bir yeni uyarı/sorun metni farkı hemen
    yeniden basılmasını tetikler). oa_metrik özeti (zaman damgalı olduğu
    için fingerprint'e KATILMAZ) her koşuda ayrıca hesaplanıp metrik.json'a
    yazılır; yalnız STDOUT'a basılıp basılmayacağı bu kısa devreye bağlıdır."""
    import hashlib
    iz_yolu = _hook_son_iz_yolu(defter)
    onceki_hash = None
    if os.path.isfile(iz_yolu):
        try:
            with open(iz_yolu, encoding="utf-8") as f:
                onceki_hash = (json.load(f) or {}).get("hash")
        except Exception:
            onceki_hash = None
    guncel_hash = hashlib.sha256(cikti.encode("utf-8", errors="replace")).hexdigest()
    degisti = (onceki_hash != guncel_hash)
    try:
        os.makedirs(defter, exist_ok=True)
        tmp = f"{iz_yolu}.tmp.{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"hash": guncel_hash}, f)
        os.replace(tmp, iz_yolu)
    except Exception:
        pass  # iz yazılamasa da hook ana işlevini sürdürür (fail-open, bloklamaz)
    return degisti


def _defter_koku_yukari_ara(baslangic_yol, maks_derinlik=30):
    """DÜZELTME (hakem düzeltme turu 1, madde 3) — `baslangic_yol` (dosya ya
    da dizin olabilir, VAR OLMAK ZORUNDA DEĞİL) konumundan üst dizinlere
    doğru yürüyerek içinde `_oa/defter` bulunan İLK ata dizini döndürür;
    bulunamazsa None. PostToolUse payload'ındaki `tool_input.file_path`
    (YENİ YAZILAN dosyanın kendi yolu), hook'un CWD/stdin-cwd/
    CLAUDE_PROJECT_DIR adaylarının HİÇBİRİYLE örtüşmediği gerçek dağıtım
    senaryosunu (oturum CWD'si dava klasörünün DIŞINDA — saha bulgusu)
    kapatır. ASLA istisna fırlatmaz; dosya sistemi köküne ulaşınca veya
    `maks_derinlik` aşılınca durur (sonsuz döngü yok)."""
    try:
        yol = os.path.abspath(str(baslangic_yol))
    except Exception:
        return None
    if not os.path.isdir(yol):
        yol = os.path.dirname(yol)
    onceki = None
    derinlik = 0
    while yol and yol != onceki and derinlik < maks_derinlik:
        try:
            if os.path.isdir(os.path.join(yol, "_oa", "defter")):
                return yol
        except Exception:
            pass
        onceki = yol
        yol = os.path.dirname(yol)
        derinlik += 1
    return None


def _hook_kok_adaylarini_bul(kok_arg):
    """DÜZELTME (v0.5.5 şerh turu — Ş7/B1 BLOKER): hook'un GERÇEK çağrı
    biçiminde (`hooks/hooks.json` --kok VERMEZ) `kok_arg` her zaman argparse
    varsayılanı '.' olur — bu, hook'u yalnız harness'ın SÜRECİN CWD'sine
    bakan bir no-op'a indirger; oysa Claude Code hook'ları çalışma kökünü
    genelde `CLAUDE_PROJECT_DIR` ortam değişkeni ve/veya stdin'den verilen
    bir JSON payload'ın (`cwd` alanı) İÇİNDE taşır — süreç CWD'si bunlarla
    AYNI olmayabilir (`tests/test_hook_denetle.py` gibi --kok'u AÇIKÇA veren
    çağrılar zaten bu keşfi atlar).

    Aday kökler ÖNCELİK SIRASIYLA toplanır ve TÜMÜ denetlenir (yalnız İLKİ
    değil — çok-köklü/çok-dava kurulumlar için):
    (1) `kok_arg` AÇIKÇA verilmişse (argparse varsayılanı '.' DEĞİLSE) YALNIZ
        o (mevcut testlerin/çağıranların davranışı BİT DÜZEYİNDE korunur);
    (2) stdin JSON payload'ındaki `cwd` (yalnız stdin bir TTY DEĞİLSE okunur
        — interaktif elle çağrıda ASLA blokla-BEKLEME; okunamazsa/boşsa
        sessizce atlanır);
    (3) DÜZELTME (madde 3) — stdin JSON payload'ındaki `tool_input.file_path`
        (yoksa `tool_response.filePath`): PostToolUse'un YENİ YAZDIĞI
        dosyanın kendi yolundan `_defter_koku_yukari_ara` ile yukarı
        yürünerek `_oa/defter` içeren ilk ata dizin bulunursa aday listesine
        eklenir — (1)/(2)/(4) hiçbiri dava köküne değmediğinde (gerçek saha
        dağıtımı: oturum CWD'si dava klasörünün DIŞINDA) hook'u artık KÖR
        bırakmaz;
    (4) `CLAUDE_PROJECT_DIR` ortam değişkeni;
    (5) mevcut CWD ('.') — eski davranış, HER ZAMAN aday listesine dahildir
        (geriye uyum — hiçbir eski senaryo bu keşifle kaybolmaz)."""
    adaylar = []
    if kok_arg and kok_arg != ".":
        adaylar.append(kok_arg)
    else:
        try:
            if not sys.stdin.isatty():
                ham = sys.stdin.read()
                if ham:
                    veri = json.loads(ham)
                    stdin_cwd = (veri or {}).get("cwd")
                    if stdin_cwd:
                        adaylar.append(stdin_cwd)
                    # DÜZELTME (madde 3) — bkz. docstring (3).
                    dosya_yolu = None
                    ti = (veri or {}).get("tool_input")
                    if isinstance(ti, dict):
                        dosya_yolu = ti.get("file_path")
                    if not dosya_yolu:
                        tr = (veri or {}).get("tool_response")
                        if isinstance(tr, dict):
                            dosya_yolu = tr.get("filePath")
                    if dosya_yolu:
                        bulunan = _defter_koku_yukari_ara(dosya_yolu)
                        if bulunan:
                            adaylar.append(bulunan)
        except Exception:
            pass
        proje_dizini = os.environ.get("CLAUDE_PROJECT_DIR")
        if proje_dizini:
            adaylar.append(proje_dizini)
        adaylar.append(".")
    # tekilleştir (sıra korunarak) — aynı köke iki kez denetim koşmasın.
    gorulen, tekil = set(), []
    for a in adaylar:
        ap_ = os.path.abspath(a)
        if ap_ not in gorulen:
            gorulen.add(ap_)
            tekil.append(ap_)
    return tekil


def _hook_basarisizlik_isaretle(kok_aday, hata):
    """B1 DÜZELTME (v0.5.5 şerh turu) — hook denetimi bir kök için FİİLEN
    ÇÖKTÜĞÜNDE artık tamamen sessiz DEĞİLDİR: stderr uyarısına EK olarak
    (o eskiden de vardı ama hook stderr'i genelde kullanıcıya hiç görünmez),
    mümkünse o kökün `_oa/DURUM.md` dosyasına görünür bir uyarı satırı
    eklenir — best-effort, kendi try/except'i içinde (DURUM.md yazımı da
    başarısız olursa hook YİNE DE bloklamaz/çökmez)."""
    try:
        durum_yolu = os.path.join(kok_aday, "_oa", "DURUM.md")
        if os.path.isfile(durum_yolu):
            with open(durum_yolu, "a", encoding="utf-8") as f:
                f.write(f"\n⚠ [{simdi()}] Stop/SessionEnd hook koşamadı: {hata}\n")
    except Exception:
        pass


def _hook_govde_calistir(kok_aday, hook_adi):
    """Stop/SessionEnd (`hook_denetle`) VE PostToolUse (`hook_postwrite`)
    ORTAK gövdesi — bir kök için `denetle_calistir` + oa_metrik özetini
    koşturur, DURUM.md/metrik.json'ı HER ZAMAN tazeler (bu yüzden hiçbir
    koşuda bayat kalmaz); yalnız STDOUT basımı, önceki koşudan bu yana çıktı
    DEĞİŞMEDİYSE sessiz kısa devre olur (bkz. `_hook_cikti_degisti_mi`). Bu
    kökte `_oa/defter` YOKSA sessizce hiçbir şey yapmaz. ASLA istisna
    fırlatmaz dışarı — hata `_hook_basarisizlik_isaretle` ile İŞARETLENİR
    (DURUM.md varsa) + stderr'e basılır.

    DÜZELTME (turu 2, YENİ-2 — saha ölçümü): PostToolUse stdout'u modele
    DOĞRUDAN geri beslenir (bağlam maliyeti) — throttle (`_hook_cikti_degisti_mi`)
    2.-N. tetikte bunu 0 bayta indiriyor ama İLK tetikte tam `oa_metrik`
    telemetri tablosu ([1]-[7], ölçülen sahada tek kök için ~5,2 KB, çok
    köklü kurulumda daha fazla) hook yoluyla basılıyordu. Telemetri BLOKAJ
    DEĞİLDİR ve avukat onu talep etmediyse otomatik tetikte gerekmez — bu
    yüzden metrik.json YİNE HER KOŞUDA yazılır (yan etki KORUNUR, `_oa_metrik_
    ozet_al` çağrısı aynen kalır) ama tam tablo hook STDOUT'una BASILMAZ;
    yalnız `--goster` (avukatın kendi isteğiyle çağırdığı, ucuz/sık komut)
    tam tabloyu gösterir (bkz. `goster()`). Denetim/uyarı satırları (`cikti`)
    HİÇ KISALMADAN aynen basılmaya devam eder — kısılan yalnız telemetridir."""
    try:
        defter = os.path.join(kok_aday, "_oa", "defter")
        if not os.path.isdir(defter):
            return  # bu aday kökte pipeline defteri yok — sessizce atla
        # E5 (v0.5.5.1) — WORKING MEMORY TETİĞİ: denetimden ÖNCE koşar, çünkü
        # onarım sonrası tablo (Gate G / bayatlık) TAZE hâli görmelidir. Elle
        # yazılmış/bozuk dosya-analiz.md burada birincil kaynaklardan yeniden
        # türetilir — ritüelin koşulmasını BEKLEMEZ.
        onarim_uyarisi = _analiz_md_kendini_onar(kok_aday)
        # HER ZAMAN koşar (DURUM.md + metrik.json bu yüzden hiçbir koşuda
        # bayat kalmaz) — yalnız aşağıdaki STDOUT basımı kısa devre olabilir.
        temiz, cikti = denetle_calistir(kok_aday)
        if onarim_uyarisi:
            # Onarım GÖRÜNÜR olmalı (sessiz atlama yasağının simetriği: sessiz
            # ONARIM da yasak) ve parmak izine girmeli ki kısa devre yutmasın.
            cikti = f"{cikti}\n{onarim_uyarisi}"
        # YENİ-2 düzeltmesi: yan etki (metrik.json yazımı) korunur, dönen tam
        # metin hook STDOUT'una BASILMAZ (bkz. docstring) — yalnız varlığına
        # işaret eden tek satır basılır.
        _oa_metrik_ozet_al(kok_aday)
        if not _hook_cikti_degisti_mi(defter, cikti):
            return  # denetim ÇIKTISI son koşudan bu yana değişmedi — sessiz kısa devre
        print("═" * 66)
        print(f"OTOMATİK DENETİM ({hook_adi} hook — kök: {kok_aday})")
        print("═" * 66)
        print(cikti)
        print(f"(oa_metrik telemetrisi _oa/defter/metrik.json'a yazıldı — tam tablo: "
              f"`pipeline_kayit.py --goster --telemetri --kok {kok_aday}`)")
    except Exception as e:
        try:
            print(f"UYARI: {hook_adi} hook ({kok_aday}) başarısız oldu ({e}) — "
                  "işlem ENGELLENMEDİ.", file=sys.stderr)
        except Exception:
            pass
        _hook_basarisizlik_isaretle(kok_aday, str(e))


# ── ATLANMIŞ HAT NÖBETÇİSİ (v0.5.6.1 — P0, saha kanıtlı) ───────────────────
# SAHA VAKASI: model çekirdek skill'i çağırdı, iki dilekçe + UDF + PDF üretti,
# ama `oa-pipeline`'a HİÇ devretmedi — parçaların yalnız description'larını
# okuyup disiplini kendi muhakemesiyle yürüttü. Çıktı iyiydi; ama süre hesabı,
# antitez matrisi ve teslim kapıları HİÇ koşmadı. Avukat "plugin'i kullandın
# mı?" diye sormasa fark edilmeyecekti.
#
# NEDEN HİÇBİR HOOK KONUŞMADI: hem `_hook_postwrite_tetikle_mi` hem
# `_hook_govde_calistir` işe `_oa/defter` VAR MI diye başlıyordu; hat hiç
# açılmadıysa defter de yoktur, dolayısıyla tetik SESSİZCE geri dönüyordu.
# Yani nöbetçi, tam da nöbet tutması gereken vakada uyuyordu.
#
# DÜZELTME: "çıktı var + defter yok" ayrı ve ÖNCELİKLİ bir sinyaldir. Bu,
# ZORLAMA değil GÖRÜNÜRLÜK'tür (amaç çizgisi): iş engellenmez, avukat
# hangi kapıların hiç koşmadığını ÖĞRENİR. Modelin kestirmesi meşru olabilir
# — ama sessiz kalması olamaz.
_HAT_ATLANDI_BASLIK = "⚠ HAT ATLANDI — pipeline defteri YOK ama çalışma ürünü VAR"


def _calisma_urunu_var_mi(kok, azami_tarama=400):
    """Kökte dilekçe-şekilli bir çalışma ürünü var mı? `_oa/cikti` ZORUNLU
    DEĞİL — saha vakasında model çıktıyı kök altındaki `cikti/`ye yazmıştı,
    yani nöbetçi sözleşmeli dizine bakarak arasa yine kör kalırdı. Bu yüzden
    kökün ilk iki katmanı taranır. Döner: bulunan dosya adları (en çok 5).
    ASLA istisna fırlatmaz."""
    bulunan = []
    try:
        sayac = 0
        for dizin, altlar, adlar in os.walk(kok):
            # `.git`, `evraklar` gibi ağır/ilgisiz ağaçlara girme; derinlik 2.
            altlar[:] = [a for a in altlar
                         if not a.startswith(".") and a not in ("__pycache__", "node_modules")]
            if dizin.count(os.sep) - kok.count(os.sep) >= 2:
                altlar[:] = []
            for ad in adlar:
                if sayac >= azami_tarama:
                    return bulunan
                if not ad.lower().endswith((".md", ".txt", ".html", ".udf")):
                    continue
                sayac += 1
                yol = os.path.join(dizin, ad)
                try:
                    with open(yol, encoding="utf-8", errors="replace") as f:
                        if _DILEKCE_DESEN.search(f.read(20000)):
                            bulunan.append(os.path.relpath(yol, kok))
                            if len(bulunan) >= 5:
                                return bulunan
                except OSError:
                    continue
    except Exception:
        return bulunan
    return bulunan


def _hat_atlandi_uyarisi(kok):
    """`_oa/defter` YOK ama çalışma ürünü VAR ise görünür uyarı metni, aksi
    hâlde None. ASLA istisna fırlatmaz, ASLA bloklamaz."""
    try:
        if os.path.isdir(os.path.join(kok, "_oa", "defter")):
            return None                      # hat açılmış — bu nöbetçinin işi değil
        urunler = _calisma_urunu_var_mi(kok)
        if not urunler:
            return None                      # ürün de yok — söylenecek bir şey yok
        return (
            f"{_HAT_ATLANDI_BASLIK}\n"
            f"  Bulunan çalışma ürünü: {', '.join(urunler)}\n"
            "  Bu klasörde `_oa/defter` yok; yani `oa-pipeline` hattı HİÇ açılmadı.\n"
            "  Aşağıdakilerin hiçbiri koşmamış olabilir — çıktı doğru olsa BİLE\n"
            "  denetlenmemiştir:\n"
            "    · oa-sure      — süre/zamanaşımı deterministik hesabı\n"
            "    · oa-vakia     — iddia↔delil matrisi, ispat boşluğu\n"
            "    · oa-antitez   — sekiz cephe, çürütülmemiş antitez\n"
            "    · oa-kontrol   — teslim öncesi künye/atıf denetimi + makbuz\n"
            "    · oa-gizlilik  — Layer 0 dış çıktı süzgeci\n"
            "  Hattı açmak için: `python pipeline_kayit.py --baslat \"<dosya adı>\"`\n"
            "  (Bu bir ENGEL DEĞİLDİR — yalnız görünürlüktür. Kestirme meşru\n"
            "   olabilir; sessiz kalması olamaz.)")
    except Exception:
        return None


# ── DEVİR HATIRLATICISI (v0.5.6.1 — UserPromptSubmit) ──────────────────────
# DÜRÜST SINIR, ÖNCE BU: hiçbir hook modeli bir skill'i çağırmaya ZORLAYAMAZ.
# `PreToolUse` yalnız model ZATEN bir araç çağırdığında ateşler — atlama
# vakasında hiç çağırmadığı için ateşlemez. Elimizdeki en güçlü mekanizma
# `UserPromptSubmit`tir: çıktısı modelin BAĞLAMINA, üstelik model prompt'u
# işlemeden ÖNCE girer.
#
# NEDEN SKILL.md'DEN GÜÇLÜ: SKILL.md ancak model o skill'i ÇAĞIRIRSA yüklenir
# — yani atlama vakasında hiç okunmaz. Bu hook ise çağrıdan bağımsız, HER
# turda koşar. §0.5 "atlanamaz" talimatı böylece metinden bağlama taşınır.
#
# NEDEN YİNE DE GARANTİ DEĞİL: bağlama giren bir cümle bir TALİMATTIR, kapı
# değil. Model yine atlayabilir. Bu yüzden ikinci ayak `_hat_atlandi_uyarisi`
# (Stop hook) TESPİT eder. Zorlama+tespit birlikte çalışır; tek başına ikisi
# de yetmez.
#
# GÜRÜLTÜ DİSİPLİNİ: hat açıksa (defter var) ÇIKTI YOKTUR. Her turda tekrar
# eden bir uyarı, okunmayan bir uyarıya dönüşür (uyum maliyeti = uyum).
def _dosya_klasoru_mu(kok):
    """Bu klasör bir DAVA DOSYASI klasörü mü? Ucuz sezgi: UYAP evrak deseni
    (`NNN_...` adlandırması) ya da `_oa` kökü var mı. ASLA istisna fırlatmaz."""
    try:
        if os.path.isdir(os.path.join(kok, "_oa")):
            return True
        sayac = 0
        for girdi in os.scandir(kok):
            if girdi.is_file() and re.match(r"^\d{3}[_-]", girdi.name):
                sayac += 1
                if sayac >= 3:      # üç numaralı evrak = UYAP indirmesi
                    return True
        return False
    except Exception:
        return False


def hook_prompt(kok=None):
    """UserPromptSubmit — devir yükümlülüğünü modelin bağlamına enjekte eder.
    Döner: her zaman 0 (ASLA bloklamaz). Hat açıksa hiçbir şey basmaz."""
    try:
        k = os.path.abspath(kok or ".")
        if not _dosya_klasoru_mu(k):
            return 0                                     # dava klasörü değil — sessiz
        if os.path.isdir(os.path.join(k, "_oa", "defter")):
            return 0                                     # hat zaten açık — sessiz
        metin = (
            "ORTAK AVUKAT — DEVİR YÜKÜMLÜLÜĞÜ (mekanik hatırlatma, bu turda geçerli):\n"
            "Bu klasör bir dava dosyası klasörü ve `_oa/defter` YOK — yani pipeline "
            "hattı henüz açılmamış. Hukuki bir iş (analiz, dilekçe, mütalaa, araştırma) "
            "yapılacaksa çekirdek `ortak-avukat` §0.5 uyarınca ilk hamle `oa-pipeline`'a "
            "DEVİRDİR ve devir SÖZLE değil ÇAĞRIYLA olur — parçaların description'larını "
            "okuyup disiplini taklit etmek o parçayı çalıştırmak DEĞİLDİR.\n"
            "Atlanırsa şunlar hiç koşmaz: oa-sure (süre/zamanaşımı aritmetiği) · "
            "oa-vakia (iddia↔delil matrisi) · oa-antitez (sekiz cephe) · "
            "oa-kontrol (teslim öncesi künye/atıf denetimi + makbuz) · "
            "oa-gizlilik (Layer 0). Çıktı doğru görünse bile DENETLENMEMİŞ olur.\n"
            "Bu bir ENGEL DEĞİLDİR: tek ve izole bir soru soruluyorsa tam hattı açma; "
            "tereddütte aç."
        )
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": metin,
        }}, ensure_ascii=False))
        return 0
    except Exception:
        return 0                                          # sessiz başarısızlık — asla bloklamaz


def hook_denetle(kok=None):
    """P0-7 — Stop/SessionEnd hook komutu. Döner: her zaman 0 (ASLA
    bloklamaz)."""
    try:
        kokler = _hook_kok_adaylarini_bul(kok)
    except Exception:
        kokler = [os.path.abspath(kok or ".")]
    for kok_aday in kokler:
        # ATLANMIŞ HAT NÖBETÇİSİ — defter denetiminden ÖNCE. `_hook_govde_calistir`
        # defter yoksa sessizce döner; oysa "defter YOK + ürün VAR" hâli tam da
        # görünmesi gereken hâldir (bkz. `_hat_atlandi_uyarisi` notu).
        atlandi = _hat_atlandi_uyarisi(kok_aday)
        if atlandi:
            print("═" * 66)
            print(atlandi)
            print("═" * 66)
        _hook_govde_calistir(kok_aday, "Stop/SessionEnd")
    return 0


# ═════════════════════════════════════════════════════════════════════════
# GÖREV B / P0-B (v0.5.5) — ÜRETİM-ANI TETİK'in İKİNCİ AYAĞI: Stop/SessionEnd
# yalnız OTURUM KAPANIRKEN koşar; bir taslak/UDF üretimi ile oturum kapanışı
# arasında model hiçbir şey çağırmadan uzun süre çalışabilir (saha bulgusu:
# TASLAK.udf basıldı ama dökum=0/muhakeme kaydı=0/makbuz=YOK hâli oturum
# kapanana kadar GÖRÜNMEDİ). PostToolUse(Write|Edit) bu boşluğu kapatır —
# HER Write/Edit çağrısından SONRA tetiklenir. Tam `denetle_calistir` +
# oa_metrik HER ZAMAN koşturmak (Gate-G/makbuz/OCR taraması dahil) PAHALI
# olurdu (amaç-çizgisi: "ateşlemeyen kapıyı sil" / "araç yolunu ucuzlat");
# bu yüzden `_hook_postwrite_tetikle_mi` UCUZ bir ön-denetimle (mtime +
# desen taraması, disk-ağır iş YOK) yalnız "bu kökte gerçekten YENİ bir
# dilekçe-şekilli dosya düştü mü" sorusuna bakar — HAYIR ise tam gövde hiç
# çağrılmaz.
# ═════════════════════════════════════════════════════════════════════════

HOOK_POSTWRITE_PENCERE_SN = 60  # PostToolUse'un "yeni sayılır" mtime penceresi


def _hook_postwrite_tetikle_mi(kok_aday, pencere_sn=HOOK_POSTWRITE_PENCERE_SN):
    """UCUZ ön-denetim: bu kökte (a) `_oa/defter` VAR mı VE (b) `_oa/cikti`
    altında SON `pencere_sn` saniye içinde değiştirilmiş, dilekçe-şekilli
    görünen (`_DILEKCE_DESEN` — `_dilekce_sekilli_makbuzsuz_uyarisi` ile AYNI
    desen, TEK KAYNAK) bir dosya VAR mı. İkisi de doğruysa True — yalnız o
    zaman tam `_hook_govde_calistir` (Gate-G + makbuz + oa_metrik dahil AĞIR
    iş) koşturulur. Yalnız `os.scandir` + `mtime` + kısa bir ön-okuma (ilk
    ~20KB) yapar; ASLA istisna fırlatmaz (hata → False, tetiklemez — bu bir
    görünürlük KAYBI yaratmaz, çünkü Stop/SessionEnd hook'u zaten AYRICA
    (defter değişmese bile) aynı bulguyu yakalar — bkz. `_hook_cikti_degisti_mi`
    testleri)."""
    try:
        defter = os.path.join(kok_aday, "_oa", "defter")
        if not os.path.isdir(defter):
            return False
        cikti_dizin = os.path.join(kok_aday, "_oa", "cikti")
        if not os.path.isdir(cikti_dizin):
            return False
        simdi_ts = time.time()
        for girdi in os.scandir(cikti_dizin):
            if not girdi.is_file():
                continue
            try:
                if (simdi_ts - girdi.stat().st_mtime) > pencere_sn:
                    continue
            except OSError:
                continue
            try:
                with open(girdi.path, encoding="utf-8", errors="replace") as f:
                    icerik = f.read(20000)  # ilk ~20KB yeter — desen genelde künye/başlıkta
            except OSError:
                continue
            if _DILEKCE_DESEN.search(icerik):
                return True
        return False
    except Exception:
        return False


def hook_postwrite(kok=None):
    """GÖREV B / P0-B (v0.5.5) — PostToolUse(Write|Edit) hook komutu. Bu
    kökte (veya keşfedilen aday köklerden herhangi birinde)
    `_hook_postwrite_tetikle_mi` True DÖNMEDİKÇE hiçbir ağır iş yapmaz
    (hızlı erken çıkış). Döner: her zaman 0 (ASLA bloklamaz)."""
    try:
        kokler = _hook_kok_adaylarini_bul(kok)
    except Exception:
        kokler = [os.path.abspath(kok or ".")]
    for kok_aday in kokler:
        try:
            tetik = _hook_postwrite_tetikle_mi(kok_aday)
        except Exception as e:
            _hook_basarisizlik_isaretle(kok_aday, f"--hook-postwrite ön-denetimi çöktü: {e}")
            continue
        if not tetik:
            continue
        _hook_govde_calistir(kok_aday, "PostToolUse")
    return 0


def main():
    ap = argparse.ArgumentParser(description="oa-pipeline defteri — statü ancak kanıtla yazılır (append-only jsonl)")
    ap.add_argument("--kok", default=".",
                    help="çalışma kökü (tam_tur.py/oa_metrik.py simetrisi; varsayılan CWD → CWD/_oa)")
    ap.add_argument("--yol", help="(geriye uyum) doğrudan pipeline-durum.json yolu; jsonl aynı klasörde")
    ap.add_argument("--baslat", metavar="DOSYA_ADI")
    ap.add_argument("--ceza", choices=["mudafii", "musteki"])
    ap.add_argument("--isle", action="store_true")
    ap.add_argument("--adim", type=int)
    ap.add_argument("--parca")
    ap.add_argument("--katman")
    ap.add_argument("--durum")
    ap.add_argument("--kanit")
    ap.add_argument("--gerekce")
    ap.add_argument("--eksik")
    ap.add_argument("--pas-yolu", dest="pas_yolu", default=None,
                    help="M1 PAS PROTOKOLÜ (Paket D) — bu adımın ürettiği `_oa/cikti/"
                         "NN-*.md` PASının yolu (göreli veya mutlak). Kaydedilir; "
                         "`ajan-brif` bir SONRAKİ parçaya bu pası 1. sıradan enjekte eder.")
    ap.add_argument("--goster", action="store_true")
    ap.add_argument("--telemetri", action="store_true",
                     help="--goster ile birlikte: oa_metrik telemetri tablosunu ([1]-[7]) "
                          "da basar (YENİ-2 düzeltmesi — varsayılan --goster/hook yolu "
                          "artık bunu otomatik basmaz, bkz. değişiklik günlüğü).")
    ap.add_argument("--denetle", action="store_true")
    ap.add_argument("--serh",
                     help="P0-6: önkoşul-artefakt kapısı (adım-5/9) VEYA İNGEST-ÖNCE "
                          f"BLOKLU'yken GEREKÇELİ geçiş (>={SERH_GEREKCE_MIN} karakter) — "
                          "olay 'serh:true' ile İŞLENİR, sessiz geçilmez.")
    ap.add_argument("--arac-hata", action="store_true", dest="arac_hata",
                    help="D5: bir MCP/araç çağrısı çöktüğünde deftere 'ARAÇ ÇÖKTÜ' işler")
    ap.add_argument("--arac", help="--arac-hata: çöken aracın adı (ör. ictihat_getir)")
    ap.add_argument("--sorgu", help="--arac-hata: (opsiyonel) yapılan sorgu")
    ap.add_argument("--hata", help="--arac-hata: hata açıklaması (zorunlu)")
    ap.add_argument("--hook-denetle", action="store_true", dest="hook_denetle",
                     help="P0-7: model-bağımsız Stop/SessionEnd hook komutu — defter "
                          "yoksa sessiz exit 0, varsa denetimi basar (oa_metrik metrik.json'a "
                          "yazılır ama STDOUT'a basılmaz — bkz. --telemetri, YENİ-2); "
                          "ASLA bloklamaz (her zaman exit 0).")
    ap.add_argument("--hook-postwrite", action="store_true", dest="hook_postwrite",
                     help="GÖREV B/P0-B (v0.5.5): model-bağımsız PostToolUse(Write|Edit) "
                          "hook komutu — yalnız _oa/cikti altında SON 60sn içinde "
                          "dilekçe-şekilli yeni bir dosya varsa tam denetim koşar "
                          "(hızlı erken çıkış); ASLA bloklamaz (her zaman exit 0).")
    ap.add_argument("--hook-prompt", action="store_true", dest="hook_prompt",
                     help="P0 (v0.5.6.1): model-bağımsız UserPromptSubmit hook komutu — "
                          "dosya klasöründe hat AÇILMAMIŞSA devir yükümlülüğünü modelin "
                          "BAĞLAMINA enjekte eder (SKILL.md'den yapısal olarak güçlüdür: "
                          "SKILL.md ancak çağrılırsa yüklenir, bu HER turda koşar). "
                          "Hat açıksa SESSİZDİR; ASLA bloklamaz (her zaman exit 0).")
    ap.add_argument("--avukat-karari", dest="avukat_karari", default=None,
                     help="M7 (Paket D): AVUKAT KARARI BEKLEYEN'deki bir çatalı "
                          "((--adim+--parca) VEYA --katman ile hedeflenir) NİHAİ "
                          "karar metniyle kaydeder — --gerekce ZORUNLU.")
    args = ap.parse_args()

    if args.hook_prompt:
        sys.exit(hook_prompt(args.kok))

    if args.hook_denetle:
        sys.exit(hook_denetle(args.kok))
    elif args.hook_postwrite:
        sys.exit(hook_postwrite(args.kok))
    elif args.avukat_karari is not None:
        avukat_karari_kaydet(args)
    elif args.baslat:
        baslat(args)
    elif args.isle:
        if not (args.parca and args.durum):
            sys.exit("HATA: --isle için --adim, --parca ve --durum gerekli.")
        isle(args)
    elif args.katman and args.durum:
        katman_isle(args)
    elif args.arac_hata:
        if not args.arac:
            sys.exit("HATA: --arac-hata için --arac (araç adı) gerekli.")
        if not args.hata:
            sys.exit("HATA: --arac-hata için --hata (hata açıklaması) gerekli.")
        arac_hata(args)
    elif args.goster:
        goster(args)
    elif args.denetle:
        denetle(args)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
