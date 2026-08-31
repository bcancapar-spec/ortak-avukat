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

import argparse, json, os, sys, datetime, importlib.util, re, glob, time, hashlib, stat

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
# C5 (v0.5.8.5) — ELDEN: yeni resmî statü. SCRIPT'li bir parça UYGULANDI
# yazılırken kanıt metninde `_oa/` altı bir artefakt yolu YOKSA (veya yol
# diskte yoksa) statü otomatik ELDEN'e düşer: iş yapılmış olabilir ama script
# artefaktı diskte KANITLANMAMIŞTIR — UYGULANDI ile aynı kefeye konmaz,
# BLOKLANMAZ da (görünürlük, engel değil). derle/DURUM.md ELDEN'i ayrı sayar;
# --denetle "script izi yok" çoklu uyarısını ELDEN kalemleri için TEK özet
# satıra indirir.
STATULER = {"UYGULANDI", "GEREKSIZ", "BILGI-EKSIK", "YUKLENEMEDI", "ELDEN"}
# C5 — ELDEN KAPSAMI: görev sayımındaki parçalar (illiyet, sure, vakia, kiyas,
# antitez, usul, gizlilik, ingest) koddaki mevcut SCRIPTLI listesinden
# TÜRETİLİR (ikiz-liste yasağı): 'manifest' (adım-0) ve 'oa-sozlesme' sayımda
# YOKTUR — kapsam dışı kalır (mevcut UYGULANDI sözleşmeleri korunur).
# 'ingest'in defterde ayrı parçası yoktur; fiziksel izi zaten İNGEST-ÖNCE
# kapısının (_oa/metin/00-kunye.json) konusudur.
ELDEN_KAPSAM = frozenset(SCRIPTLI) - {"manifest", "oa-sozlesme"}
MIN_KANIT = 20  # karakter — "yaptım" tek kelimesi kanıt değildir

# C5 — kanıt metnindeki `_oa/...` artefakt yolu deseni (hem / hem \ ayırıcı).
_OA_ARTEFAKT_YOL_RE = re.compile(r"_oa[/\\][\w.\-/\\]+")


def _kanit_artefakt_yolu_var_mi(kok, kanit):
    """C5 — kanıt metnindeki `_oa/...` yollarını arar. Döner:
    (yol_bulundu: bool, diskte_var: bool) — diskte_var, bulunan yollardan EN
    AZ BİRİ `kok` altında fiilen varsa True. ASLA istisna fırlatmaz."""
    try:
        if not kanit:
            return False, False
        eslesmeler = _OA_ARTEFAKT_YOL_RE.findall(kanit)
        if not eslesmeler:
            return False, False
        for e in eslesmeler:
            parcalar = [p for p in re.split(r"[/\\]+", e.rstrip(".,;:!?)»'\"")) if p]
            yol = os.path.join(kok or ".", *parcalar)
            if os.path.exists(yol):
                return True, True
        return True, False
    except Exception:
        return False, False

# ── P0-5 (v0.5.5) — olay-bazlı sürüm damgası (geçiş supabı) ─────────────────
# Her --isle/--katman olayına 'surum' alanı eklenir. Bir defterde HİÇ v0.5.5+
# olay yoksa (eski/az önce yükseltilmiş kök) MAKBUZ denetimleri (yalnız
# P0-5(d)/(e)) yalnız UYARI basar; ilk v0.5.5 yazımından SONRA blokleyicidir
# ("açık defterler yükseltmeden sonraki ilk kayıtta otomatik migrate olur").
# P0-6'nın önkoşul-artefakt kapıları bu supabı TAŞIMAZ — v0.5.5'te baştan
# itibaren aktiftir (eski jsonl'lerde de aynı fiziksel eksiklik varsa aynı
# şekilde uygulanır; bu davranış farkı bilinçlidir, bkz. SKILL.md).
OA_SURUM = "0.5.15"


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


def _kiyas_artefakti_mi(yol):
    """B-28 (v0.5.14) — TEK SÖZLEŞME + İÇERİK DENETİMİ.

    Onarım öncesi iki ayrı ad sözleşmesi vardı: önkoşul `05-kiyas*` arıyor,
    tüketici (`_kiyas_bosluk_uyarisi`) `*kiyas*.json` okuyordu — `01-kiyas.json`
    üreten model haksız yere bloklanıyor, ters yönde ise `05-kiyas.json` içine
    yazılmış 400 harflik 'A' dolgusu boyut kapısını (`_govde_saglam_mi`) geçip
    önkoşulu YEŞİL yapıyordu. Artık tek sözleşme `*kiyas*` desenidir ve `.json`
    uzantılı aday, tüketicinin okuduğu şeyin ta kendisi olmak zorundadır
    (`arac == "kiyas_denetim"`). `.md`/`.txt` çalışma evrakı AYNEN gövde
    boyutuyla değerlendirilir (geriye uyum — saha deseni). ASLA fırlatmaz."""
    if not _govde_saglam_mi(yol):
        return False
    if not str(yol).lower().endswith(".json"):
        return True
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            m = json.load(f)
    except Exception:
        return False
    return isinstance(m, dict) and m.get("arac") == "kiyas_denetim"


def _kiyas_onkosul_saglam_mi(kok):
    cikti = os.path.join(kok or ".", "_oa", "cikti")
    kiyas = next((y for y in sorted(glob.glob(os.path.join(cikti, "*kiyas*")))
                  if _kiyas_artefakti_mi(y)), None)
    muhakeme = _glob_saglam(os.path.join(cikti, "*ictihat-muhakeme*"))
    if kiyas and muhakeme:
        return True, None
    eksik = []
    if not kiyas:
        eksik.append("_oa/cikti/05-kiyas* (tek sözleşme: *kiyas*; .json ise "
                     "arac=kiyas_denetim olmalı) yok/boş/geçersiz")
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
    if args.durum == "ELDEN":
        # C5 — ELDEN doğrudan da yazılabilir (dürüst beyan: script artefaktı
        # yok, iş elden yürütüldü); kanıt yine zorunludur.
        if not args.kanit or len(args.kanit.strip()) < MIN_KANIT:
            sys.exit("RET: ELDEN kanıtsız yazılamaz. --kanit ile elden yürütülen işi "
                     f"en az {MIN_KANIT} karakterle belgele.")
        return args.kanit.strip()


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

    # C5 (v0.5.8.5) — ELDEN DÜŞÜRME: SCRIPT'li parça UYGULANDI yazılırken
    # kanıtta `_oa/` altı artefakt yolu YOKSA veya yol diskte yoksa statü
    # UYGULANDI yerine ELDEN yazılır (yeni resmî durum — bloklamaz, ayırt
    # eder: iş yapılmış olabilir ama script artefaktı diskte KANITSIZDIR).
    durum = args.durum
    elden_notu = ""
    # ŞERHLİ geçişte düşürme YOK: şerh, gerekçeli/AVUKATA görünür bir istisna
    # olarak zaten işaretlidir (Avukat Kararı Bekleyen hattı ŞERHLİ UYGULANDI
    # semantiğine bağlıdır) — ikinci bir yeniden-etiketleme onu gölgelerdi.
    if durum == "UYGULANDI" and args.parca in ELDEN_KAPSAM and not serh_bayrak:
        yol_var, disk_var = _kanit_artefakt_yolu_var_mi(getattr(args, "kok", None), kanit)
        if not (yol_var and disk_var):
            durum = "ELDEN"
            sebep = ("kanıtta _oa/ altı artefakt yolu YOK" if not yol_var
                     else "kanıttaki _oa/ yolu diskte YOK")
            elden_notu = ("\nELDEN DÜŞÜRME (C5): " + sebep + " — statü UYGULANDI "
                          "yerine ELDEN yazıldı. Script fiilen koştuysa çıktısını "
                          "_oa/ altına yaz ve yolunu kanıta ekleyip yeniden işle; "
                          "iş bilinçli elden yürütüldüyse bu statü DÜRÜST kayıttır.")

    # ATOMİK APPEND — eşzamanlı --isle'ler (farklı adım) birbirini silemez.
    olay = {"zaman": simdi(), "tip": "adim", "adim": args.adim,
            "parca": args.parca, "durum": durum, "kanit": kanit,
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
    uyari = elden_notu
    if (durum == "UYGULANDI" and args.parca in SCRIPTLI
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
    if d_sonra is not None and durum not in _DAL_UYARI_ATLA_DURUMLARI:
        dal_tek = _dosya_dali_tahmin(getattr(args, "kok", None), d_sonra.get("ceza_dali"))
        if dal_tek is not None:
            dal_mesaj = _dal_uyusmazlik_tek(dal_tek, args.parca)
            if dal_mesaj:
                uyari += "\nUYARI: DAL UYUŞMAZLIĞI: " + dal_mesaj
    print(f"İşlendi: adım {args.adim} / {args.parca} → {durum}{uyari}{ek_uyari}")
    _durum_md_yaz(getattr(args, "kok", None))


def adim_batch(args):
    """G3a (v0.5.8.6 — 777 dersi: 33/42 adım kaydı deftere elle/imzasız
    düştü çünkü tek tek CLI çağrısı 'pahalı' görüldü) — TEK çağrıda çok adım
    kaydı. Ucuzlatma SADECE çağrı sayısındadır: her kayıt `isle()` ile AYNI
    koddan geçer — kanıt disiplini (kanıtsız UYGULANDI = RET), önkoşul
    kapıları (İNGEST-ÖNCE, P0-6), C5 ELDEN düşürme ve araç imzası AYNEN
    uygulanır. Kayıtlar SIRAYLA işlenir; i. kayıt RET olursa öncekiler
    defterde KALIR (append-only — geri alma yoktur) ve komut o noktada hata
    koduyla durur (hangi kaydın düştüğü görünür).

    JSON biçimi: `[{"adim": 1, "parca": "oa-interview", "durum": "UYGULANDI",
    "kanit": "..."}, ...]` — alanlar --isle bayraklarıyla birebir
    (gerekce/eksik/serh/pas_yolu opsiyonel)."""
    try:
        with open(args.adim_batch, encoding="utf-8") as f:
            kayitlar = json.load(f)
    except Exception as e:
        sys.exit(f"HATA: --adim-batch dosyası okunamadı/bozuk: {e}")
    if not isinstance(kayitlar, list) or not kayitlar:
        sys.exit("HATA: --adim-batch JSON'u boş olmayan bir LİSTE olmalı — "
                 '[{"adim": 1, "parca": "oa-interview", "durum": "UYGULANDI", '
                 '"kanit": "..."}].')
    for i, k in enumerate(kayitlar, 1):
        if not isinstance(k, dict):
            sys.exit(f"HATA: --adim-batch kayıt #{i} bir sözlük değil.")
        if not (k.get("parca") and k.get("durum")):
            sys.exit(f"HATA: --adim-batch kayıt #{i}: 'parca' ve 'durum' zorunlu.")
        alt = argparse.Namespace(
            kok=getattr(args, "kok", None), yol=getattr(args, "yol", None),
            adim=k.get("adim"), parca=k.get("parca"), durum=k.get("durum"),
            kanit=k.get("kanit"), gerekce=k.get("gerekce"), eksik=k.get("eksik"),
            serh=k.get("serh"), pas_yolu=k.get("pas_yolu"))
        isle(alt)   # RET/HATA hâlinde sys.exit — sonraki kayıtlar işlenmez
    print(f"BATCH: {len(kayitlar)} kayıt işlendi — tümü araç-imzalı "
          "(kanıt/önkoşul kuralları tek-kayıt --isle ile AYNEN uygulandı).")


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
                      "YUKLENEMEDI": "!", "BEKLIYOR": "⬜",
                      "ELDEN": "✋"}.get(p["durum"], "?")
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
    elden_kalemler = []  # C5 — ELDEN kalemleri TEK özet satıra iner (gürültü disiplini)
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
            elif p["durum"] == "ELDEN":
                # C5 — çoklu "script izi yok" uyarısı ELDEN kalemleri için
                # üretilmez; hepsi aşağıda TEK özet satırda toplanır.
                elden_kalemler.append(f"{no}/{parca}")
                if p.get("serh"):
                    uyarilar.append(f"adım {no} / {parca}: ⚠ ŞERHLİ — "
                                     f"{p.get('serh_metni') or ''}")
            elif p["durum"] == "YUKLENEMEDI":
                uyarilar.append(f"adım {no} / {parca}: fiziken yüklenemedi — çıktıda açıkça belirtilmeli")
    if elden_kalemler:
        uyarilar.append(
            f"ELDEN (tek özet): {len(elden_kalemler)} parça script artefaktı diskte "
            "kanıtlanmadan elden işlendi — " + ", ".join(elden_kalemler)
            + " (script fiilen koştuysa çıktısını _oa/ altına yaz ve statüyü yeniden işle).")
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


# ═════════════════════════════════════════════════════════════════════════
# GÖRÜŞ 2026-08 (semantica uyarlama analizi, antitez turu sonucu — bkz.
# _gorus/semantica-uyarlama.md §4): üç deterministik motorun --json çıktısı
# ilk kez GERÇEK bir tüketiciye bağlanır. Desen _vakia_delilsiz_unsur_uyarisi
# ile BİREBİR aynıdır: DURUM.md salt-okur, aracın KENDİ ürettiği JSON'u okur,
# ikinci bir denetim mantığı İCAT ETMEZ; dosya yok/okunamaz/yabancı şemalıysa
# SESSİZCE boş döner (advisory renderer alanı — asla çökmez, asla bloklamaz).
# ═════════════════════════════════════════════════════════════════════════

_ADVISORY_TAVAN = 20  # 3-4k evraklık dosyada DURUM.md şişmesin (ölçek sertleştirmesi)


def _advisory_tavanla(uyarilar):
    """GÖRÜŞ 2026-08 ölçek sertleştirmesi — advisory liste tavanı. Kırpma
    SESSİZ DEĞİLDİR: düşen kayıt sayısı ve tam listenin adresi yazılır
    ("no silent caps"). Tavan yalnız DURUM.md görünümünü korur; tam veri
    daima _oa/cikti/*.json kaynağında durur."""
    if len(uyarilar) <= _ADVISORY_TAVAN:
        return uyarilar
    fazla = len(uyarilar) - _ADVISORY_TAVAN
    return uyarilar[:_ADVISORY_TAVAN] + [
        f"… +{fazla} uyarı daha (tam liste ilgili _oa/cikti/*.json dosyasında)"]


def _graf_yapisal_bosluk_uyarisi(kok):
    """oa-illiyet/scripts/grafik_denetim.py `--json <yol>` çıktısındaki yapısal
    boşluklar (`sema_hatalari`, `desteksiz_kenarlar`, `cevrimler`)
    `_oa/cikti/*graf*.json` dosyalarından toplanır. Hukuki değerlendirme
    DEĞİLDİR — köprü düğüm/kesme adayı gibi STRATEJİ sinyalleri bilerek
    alınmaz (onlar uyarı değil karar-malzemesidir, oa-strateji/oa-antitez okur)."""
    cdiz = os.path.join(kok, "_oa", "cikti")
    if not os.path.isdir(cdiz):
        return []
    uyarilar = []
    for yol in sorted(glob.glob(os.path.join(cdiz, "*graf*.json"))):
        try:
            with open(yol, encoding="utf-8", errors="replace") as f:
                m = json.load(f)
        except Exception:
            continue
        if not isinstance(m, dict) or m.get("arac") != "grafik_denetim":
            continue
        ad = os.path.relpath(yol, kok)
        for h in (m.get("sema_hatalari") or []):
            uyarilar.append(f"{ad}: şema hatası — {h}")
        for k in (m.get("desteksiz_kenarlar") or []):
            if isinstance(k, dict):
                uyarilar.append(f"{ad}: desteksiz kenar {k.get('kaynak')}→"
                                f"{k.get('hedef')} ({k.get('tur')}) — iddia delilsiz")
        for c in (m.get("cevrimler") or []):
            if isinstance(c, list) and c:
                uyarilar.append(f"{ad}: dairesel illiyet — "
                                + " → ".join(str(x) for x in c))
    return _advisory_tavanla(uyarilar)


def _kiyas_bosluk_uyarisi(kok):
    """oa-kiyas/scripts/kiyas_denetim.py `--json <yol>` çıktısındaki subsumtion
    boşlukları `_oa/cikti/*kiyas*.json` dosyalarından toplanır: karşılanmamış
    unsur, teyitsiz içtihat, kritik_bosluk bayrağı. kiyas_denetim bilinçli
    olarak exit 0 döner ("kapı değil karar-malzemesi") — bu bekçi o tasarımı
    DEĞİŞTİRMEZ, yalnız DURUM.md'de görünür kılar."""
    cdiz = os.path.join(kok, "_oa", "cikti")
    if not os.path.isdir(cdiz):
        return []
    uyarilar = []
    for yol in sorted(glob.glob(os.path.join(cdiz, "*kiyas*.json"))):
        try:
            with open(yol, encoding="utf-8", errors="replace") as f:
                m = json.load(f)
        except Exception:
            continue
        if not isinstance(m, dict) or m.get("arac") != "kiyas_denetim":
            continue
        ad = os.path.relpath(yol, kok)
        bulundu = False
        for u in (m.get("unsur_vakia_eslesme") or []):
            if isinstance(u, dict) and u.get("durum") == "karsilanmamis":
                uyarilar.append(f"{ad}: unsur '{u.get('unsur_ad') or u.get('unsur_id')}' "
                                f"KARŞILANMAMIŞ (subsumtion boşluğu)")
                bulundu = True
        for kunye in (m.get("teyitsiz_ictihat") or []):
            uyarilar.append(f"{ad}: teyitsiz içtihat — {kunye}")
            bulundu = True
        if m.get("kritik_bosluk") and not bulundu:
            uyarilar.append(f"{ad}: kritik boşluk işaretli (eksik bileşen — norm/vakıa)")
    return _advisory_tavanla(uyarilar)


def _usul_bosluk_uyarisi(kok):
    """oa-usul/scripts/usul_matris.py `--json <yol>` çıktısındaki G1-G8
    boşlukları `_oa/cikti/*usul*.json` dosyalarından toplanır (usul_matris
    boşlukta zaten exit 1 döner; burası yalnız DURUM.md kalıcı görünürlüğü)."""
    cdiz = os.path.join(kok, "_oa", "cikti")
    if not os.path.isdir(cdiz):
        return []
    uyarilar = []
    for yol in sorted(glob.glob(os.path.join(cdiz, "*usul*.json"))):
        try:
            with open(yol, encoding="utf-8", errors="replace") as f:
                m = json.load(f)
        except Exception:
            continue
        if not isinstance(m, dict) or m.get("arac") != "usul_matris":
            continue
        ad = os.path.relpath(yol, kok)
        for b in (m.get("bosluklar") or []):
            uyarilar.append(f"{ad}: {b}")
    return _advisory_tavanla(uyarilar)


def _defter_nobetci_uyarisi(kok, olaylar_yol):
    """GÖRÜŞ 2026-08 — DEFTER KÜÇÜLME NÖBETÇİSİ: append-only defterin satır
    sayısı bir önceki türetime göre AZALMIŞSA görünür uyarı (bütün-dosya
    kaybı / kırpılma tespiti). Satır-bazlı hash-ZİNCİRİ BİLEREK kurulmadı:
    paralel fan-out append'i zinciri çatallar ve sahte alarm üretir (antitez
    turu bulgusu — bkz. _gorus/semantica-uyarlama.md §2-K5). Durum dosyası:
    _oa/defter/defter-nobetci.json {satir, sha, zaman}. Advisory — asla
    çökmez; eşzamanlı iki türetimde son-yazan-kazanır (atomik os.replace)."""
    try:
        if not olaylar_yol or not os.path.isfile(olaylar_yol):
            return []
        with open(olaylar_yol, "rb") as f:
            veri = f.read()
        satir = veri.count(b"\n") + (1 if veri and not veri.endswith(b"\n") else 0)
        sha = hashlib.sha256(veri).hexdigest()[:16]
        durum_yol = os.path.join(os.path.dirname(olaylar_yol), "defter-nobetci.json")
        onceki = None
        if os.path.isfile(durum_yol):
            try:
                with open(durum_yol, encoding="utf-8") as f:
                    onceki = json.load(f)
            except Exception:
                onceki = None
        uyarilar = []
        if (isinstance(onceki, dict) and isinstance(onceki.get("satir"), int)
                and satir < onceki["satir"]):
            uyarilar.append(
                f"DEFTER KÜÇÜLDÜ: {onceki['satir']} → {satir} satır — append-only "
                f"defterde satır kaybı (kırpılma/üzerine yazma incelenmeli; "
                f"önceki sha {onceki.get('sha')}, şimdiki {sha}).")
        tmp = f"{durum_yol}.tmp.{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"satir": satir, "sha": sha, "zaman": simdi()}, f,
                      ensure_ascii=False)
        os.replace(tmp, durum_yol)
        return uyarilar
    except Exception:
        return []


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
            # C5 — ELDEN de bir 'işlendi' beyanıdır: teslimden SONRA düşülen
            # ELDEN kaydı da post-hoc şüphesi taşır (UYGULANDI ile eşit muamele).
            if p.get("durum") not in ("UYGULANDI", "ELDEN") or not p.get("zaman"):
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


def _elden_turetilmis_mi(kok, parca, p):
    """G3b (v0.5.8.6 — 777 dersi: 6 parçanın kanıtı 'ELDEN:' ile başladığı
    hâlde statü UYGULANDI kaldı; 33/42 satır elle/imzasız düştü) — bir
    UYGULANDI kaydının TÜRETİLMİŞ görünümde 'UYGULANDI (ELDEN-türetilmiş)'
    gösterilip gösterilmeyeceği: (a) kanıt metni 'ELDEN' ile başlıyorsa VEYA
    (b) kayıt imzasız (model-beyanlı) + SCRIPT'li parça + kanıtta diskte var
    olan `_oa/` artefakt yolu YOKSA. Kayıt DEĞİŞTİRİLMEZ (append-only) —
    yalnız görünüm türetilir. ASLA fırlatmaz."""
    try:
        if (p or {}).get("durum") != "UYGULANDI":
            return False
        kanit = str(p.get("kanit") or "").strip()
        if kanit.upper().startswith("ELDEN"):
            return True
        if p.get("arac_imzali"):
            return False
        if parca not in ELDEN_KAPSAM:
            return False
        yol_var, disk_var = _kanit_artefakt_yolu_var_mi(kok, kanit)
        return not (yol_var and disk_var)
    except Exception:
        return False


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
        elden_turetilmis_n = 0   # G3b — ayrı sayaç (kayıt değişmez, görünüm türetilir)
        for no in sorted(d["adimlar"], key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
            a = d["adimlar"][no]
            try:
                adim_i = int(no)
            except (TypeError, ValueError):
                adim_i = None
            for parca, p in a["parcalar"].items():
                isaret = {"UYGULANDI": "✓", "GEREKSIZ": "−", "BILGI-EKSIK": "?",
                          "YUKLENEMEDI": "!", "BEKLIYOR": "⬜",
                          "ELDEN": "✋"}.get(p["durum"], "?")
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
                # G3b — TÜRETİLMİŞ görünüm: kanıtı 'ELDEN' ile başlayan VEYA
                # imzasız+script-artefaktsız UYGULANDI, durum sütununda
                # "UYGULANDI (ELDEN-türetilmiş)" gösterilir (kayıt değişmez).
                durum_goster = p["durum"]
                if _elden_turetilmis_mi(kok, parca, p):
                    durum_goster = "UYGULANDI (ELDEN-türetilmiş)"
                    elden_turetilmis_n += 1
                satirlar.append(f"- {isaret} adım {no} ({a['ad']}) / {parca}: {durum_goster}"
                                 f"{serh_bayrak}{imza_etiket}{fiziksel_etiket}")
        # C5 (v0.5.8.5) — ELDEN ayrı sayılır: UYGULANDI ile aynı kefede değil.
        elden_n = sum(1 for a in d["adimlar"].values()
                      for p in (a.get("parcalar") or {}).values()
                      if p.get("durum") == "ELDEN")
        if elden_n:
            satirlar.append(f"- ✋ ELDEN sayacı: {elden_n} parça — script artefaktı "
                             "diskte kanıtlanmadan elden işlendi (UYGULANDI değildir; "
                             "ayrı sayılır).")
        # G3b — ELDEN-TÜRETİLMİŞ sayacı (777: elle satır + 'ELDEN:' kanıtlı
        # UYGULANDI'lar görünmez kalmıştı). Kayıt defterde AYNEN durur
        # (append-only); yalnız bu türetilmiş görünüm ayrı sayar.
        if elden_turetilmis_n:
            satirlar.append(f"- ✋ ELDEN-türetilmiş sayacı: {elden_turetilmis_n} parça — "
                             "kanıtı 'ELDEN' ile başlayan VEYA imzasız+script-artefaktsız "
                             "UYGULANDI kayıtları (kayıt DEĞİŞTİRİLMEDİ; yalnız türetilmiş "
                             "görünümde ayrı sayılır — UYGULANDI ile aynı kefede değildir).")
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
        # GÖRÜŞ 2026-08 — üç motorun --json çıktısı + defter nöbetçisi
        # (advisory; _vakia_delilsiz_unsur_uyarisi ile aynı desen ve statü).
        graf_bosluk = _graf_yapisal_bosluk_uyarisi(kok)
        if graf_bosluk:
            satirlar.append("## 🔴 Graf Yapısal Boşluk Uyarısı (İlliyet — GÖRÜŞ 2026-08)")
            for u in graf_bosluk:
                satirlar.append(f"- 🔴 {u}")
            satirlar.append("")
        kiyas_bosluk = _kiyas_bosluk_uyarisi(kok)
        if kiyas_bosluk:
            satirlar.append("## 🔴 Kıyas Boşluk Uyarısı (Silojizm — GÖRÜŞ 2026-08)")
            for u in kiyas_bosluk:
                satirlar.append(f"- 🔴 {u}")
            satirlar.append("")
        usul_bosluk = _usul_bosluk_uyarisi(kok)
        if usul_bosluk:
            satirlar.append("## 🔴 Usul Boşluk Uyarısı (G1-G8 — GÖRÜŞ 2026-08)")
            for u in usul_bosluk:
                satirlar.append(f"- 🔴 {u}")
            satirlar.append("")
        nobetci = _defter_nobetci_uyarisi(kok, olaylar_yol)
        if nobetci:
            satirlar.append("## 🔴 Defter Nöbetçisi Uyarısı (GÖRÜŞ 2026-08)")
            for u in nobetci:
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


# ── C3 (v0.5.8.5) — HOOK NABZI ─────────────────────────────────────────────
# Üç sahada üç farklı hook ölümünün ortak dersi: kanca öldüğünde bunu KİMSE
# görmüyordu — sessizlik "temiz" ile "ölü"yü ayırt ettirmiyordu. Nabız,
# `.hook-son-iz.json`ı olay-başına ISO damgayla genişletir ({prompt: ISO,
# pretool: ISO, postwrite: ISO, denetle: ISO, acilis: ISO}); kapanış-sınıfı
# koşu (hook_denetle) prompt damgası YOK/ESKİ ise bunu GÖRÜNÜR söyler.
# Defter yoksa damga atılamaz (dosya defterde yaşar) — sessiz atlanır.
NABIZ_PROMPT_ESIK_SN = 24 * 3600  # 'eski' eşiği — bir çalışma dönemi (24 saat)


def _hook_nabiz_damgala(kok, olay_adi, oturum=None):
    """Nabız damgası: `.hook-son-iz.json`a `{olay_adi: şimdi}` MERGE eder
    (hash + diğer olay damgaları korunur). v0.5.11 (1865-T4a): payload
    session_id verilirse `son_oturum` alanı da güncellenir — Bash'le koşan
    scriptler (teslim_paketi, --isle) oturum izini bu köprüden okur.
    ASLA fırlatmaz, ASLA bloklamaz."""
    try:
        defter = os.path.join(kok, "_oa", "defter")
        if not os.path.isdir(defter):
            return
        iz_yolu = _hook_son_iz_yolu(defter)
        veri = {}
        if os.path.isfile(iz_yolu):
            try:
                with open(iz_yolu, encoding="utf-8") as f:
                    veri = json.load(f) or {}
            except Exception:
                veri = {}
        if not isinstance(veri, dict):
            veri = {}
        veri[olay_adi] = simdi()
        if oturum:
            veri["son_oturum"] = str(oturum)[:64]
        tmp = f"{iz_yolu}.tmp.{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False)
        os.replace(tmp, iz_yolu)
    except Exception:
        pass


# ── T12 (v0.5.9) — ÇİFT-KANAL DEDUP ────────────────────────────────────────
# Saha deseni: plugin `hooks/hooks.json` VE kullanıcı `settings.json` AYNI
# olayı İKİ KEZ kaydettirmiş olabilir — aynı hook gövdesi aynı turda iki kez
# koşar: çift enjeksiyon, çift defter olayı, çift otomatik mühür. Çözüm:
# gövde başında olay-başına son-çalışma damgası (`.hook-son-iz.json` içinde
# `"_dedup": {olay: epoch_ms}` EK alanı — nabız şeması AYNEN korunur, MERGE
# yazılır). AYNI olay AYNI SANİYE içinde ikinci kez çağrıldıysa YAN-ETKİSİZ
# kısa devre: çıktı basılmaz, defter olayı yazılmaz, mühür basılmaz — exit 0
# sessiz. Farklı olaylar birbirini ETKİLEMEZ; aynı olayın meşru ardışık
# turları (saniye farklı) ETKİLENMEZ.
#
# GÜVENLİK İSTİSNASI (ayirt): PreToolUse/PostToolUse aynı saniyede FARKLI
# payload'larla meşru olarak art arda ateşleyebilir (paralel araç çağrıları)
# — elle-UDF/sunum-kilidi kapısının ikinci çağrıda susması kapı kaybıdır.
# Bu gövdeler payload parmak izini `ayirt` olarak geçirir: anahtar
# "olay:ayirt" olur — yalnız BİT-BİT AYNI payload (çift kanal kopyası) kısa
# devre yapar. `_dedup` sözlüğü en yeni kayıtlarla sınırlı tutulur (şişme
# yok). Damga kısa devrede GÜNCELLENMEZ — üçüncü/dördüncü kopya da aynı
# ilk damgaya karşı ölçülür.
_DEDUP_EN_COK_KAYIT = 16


def _hook_dedup_kisa_devre(kok, olay_adi, ayirt=None):
    """Çift-kanal dedup: True → çağıran gövde YAN-ETKİSİZ sessiz çıkmalı.
    Defter yoksa damga yazılamaz → her zaman False (dedup devre dışı —
    nabız sözleşmesiyle simetrik). Oku-güncelle-yaz atomik-yakın
    (tmp + os.replace); HER hata yutulur → False. ASLA fırlatmaz."""
    try:
        defter = os.path.join(kok, "_oa", "defter")
        if not os.path.isdir(defter):
            return False
        anahtar = f"{olay_adi}:{ayirt}" if ayirt else str(olay_adi)
        simdi_ms = int(time.time() * 1000)
        iz_yolu = _hook_son_iz_yolu(defter)
        veri = {}
        if os.path.isfile(iz_yolu):
            try:
                with open(iz_yolu, encoding="utf-8") as f:
                    veri = json.load(f) or {}
            except Exception:
                veri = {}
        if not isinstance(veri, dict):
            veri = {}
        dedup = veri.get("_dedup")
        if not isinstance(dedup, dict):
            dedup = {}
        onceki = dedup.get(anahtar)
        try:
            if onceki is not None and int(onceki) // 1000 == simdi_ms // 1000:
                return True          # aynı olay + aynı saniye → kısa devre
        except Exception:
            pass                     # bozuk damga — güncellenip geçilir
        dedup[anahtar] = simdi_ms
        if len(dedup) > _DEDUP_EN_COK_KAYIT:
            # En eski damgalar atılır (yalnız sayısal olanlar sıralanabilir).
            def _ms(c):
                try:
                    return int(c[1])
                except Exception:
                    return 0
            dedup = dict(sorted(dedup.items(), key=_ms)[-_DEDUP_EN_COK_KAYIT:])
        veri["_dedup"] = dedup
        tmp = f"{iz_yolu}.tmp.{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False)
        os.replace(tmp, iz_yolu)
        return False
    except Exception:
        return False


def _hook_payload_ayirt(veri):
    """Payload parmak izi (pretool/postwrite dedup ayırt edicisi): stdin
    payload'ının deterministik sha256 kısa özeti. None/bozukta '-' (payload'sız
    çağrılar kendi aralarında dedup'lanır). ASLA fırlatmaz."""
    try:
        if not isinstance(veri, dict):
            return "-"
        ham = json.dumps(veri, ensure_ascii=False, sort_keys=True, default=str)
        return hashlib.sha256(ham.encode("utf-8", "replace")).hexdigest()[:12]
    except Exception:
        return "-"


def _hook_denetle_ayirt(kok):
    """`denetle` dedup ayırt edicisi: dava kökünün UCUZ durum parmak izi.
    İki katman: (a) `_oa/defter` dosyalarının İÇERİK hash'i — denetim
    çıktısı defterden türediği için defterdeki her gerçek değişiklik
    (--isle olayı, makbuz, RED) izi değiştirir; denetle'nin KENDİ yazdığı
    `.hook-son-iz.json` (+ .tmp artıkları) HARİÇTİR ki ilk koşunun damgası
    izi bozup dedup'u ölü koda çevirmesin; kendi yeniden-türetimleri
    (pipeline-durum.json/DURUM.md) İÇERİK-AYNI yazdığı için içerik hash'i
    onlardan etkilenmez (mtime'a bakılmaz). (b) `_oa/{cikti,teslim}` +
    kök dizin dosya listesi (ad+boyut+mtime) — model arada dilekçe/UDF
    yazdıysa iz DEĞİŞİR → denetim AYNEN koşar (Paket-B BLOKER senaryosu —
    durum-körü dedup o kapıyı öldürürdü). ASLA fırlatmaz."""
    try:
        parcalar = []
        kok = os.path.abspath(kok)
        defter = os.path.join(kok, "_oa", "defter")
        if os.path.isdir(defter):
            for taban, _dizinler, dosyalar in os.walk(defter):
                for ad in dosyalar:
                    if ad == ".hook-son-iz.json" or ".tmp." in ad:
                        continue          # denetle'nin kendi yazımı — bağışık
                    yol = os.path.join(taban, ad)
                    try:
                        with open(yol, "rb") as f:
                            icerik = hashlib.sha256(f.read()).hexdigest()[:16]
                        parcalar.append(f"{os.path.relpath(yol, kok)}|{icerik}")
                    except Exception:
                        pass
        for d in (os.path.join(kok, "_oa", "cikti"),
                  os.path.join(kok, "_oa", "teslim")):
            if not os.path.isdir(d):
                continue
            for taban, _dizinler, dosyalar in os.walk(d):
                for ad in dosyalar:
                    yol = os.path.join(taban, ad)
                    try:
                        st = os.stat(yol)
                        parcalar.append(f"{os.path.relpath(yol, kok)}|"
                                        f"{st.st_size}|{st.st_mtime_ns}")
                    except Exception:
                        pass
        try:
            for girdi in os.scandir(kok):
                if girdi.is_file():
                    st = girdi.stat()
                    parcalar.append(f"{girdi.name}|{st.st_size}|{st.st_mtime_ns}")
        except Exception:
            pass
        ham = "\n".join(sorted(parcalar))
        return hashlib.sha256(ham.encode("utf-8", "replace")).hexdigest()[:12]
    except Exception:
        return "-"


def _hook_nabiz_prompt_uyarisi(kok, esik_sn=NABIZ_PROMPT_ESIK_SN):
    """Kapanış-sınıfı koşuda ÖLÜ-PROMPT dedektörü: nabız dosyasında `prompt`
    damgası YOKSA ya da `esik_sn`den ESKİYSE görünür uyarı metni döndürür;
    aksi hâlde None. Yalnız defterli köklerde konuşur. ASLA fırlatmaz."""
    try:
        defter = os.path.join(kok, "_oa", "defter")
        if not os.path.isdir(defter):
            return None
        damga = None
        iz_yolu = _hook_son_iz_yolu(defter)
        if os.path.isfile(iz_yolu):
            try:
                with open(iz_yolu, encoding="utf-8") as f:
                    damga = (json.load(f) or {}).get("prompt")
            except Exception:
                damga = None
        if damga:
            try:
                yas = (datetime.datetime.now()
                       - datetime.datetime.fromisoformat(str(damga))).total_seconds()
                if yas <= esik_sn:
                    return None
                durum = f"son damga ESKİ ({damga})"
            except Exception:
                durum = f"damga çözümlenemedi ({damga!r})"
        else:
            durum = "damga HİÇ YOK"
        return ("⚠ HOOK NABZI: UserPromptSubmit (prompt) kancası bu oturumda/"
                f"dönemde hiç ateşlememiş görünüyor — {durum}. Üç saha ölümünün "
                "deseni budur: kanca sessizce ölür, kimse görmez. Masaüstü "
                "uygulamasını TAM kapatıp açın ve dava klasöründe ilk mesajda "
                "enjeksiyonu doğrulayın (hooks.json → UserPromptSubmit; "
                "tools/hook_doktor.py tarifi basar).")
    except Exception:
        return None


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
    # C3 (v0.5.8.5) — dosya artık yalnız 'hash' değil olay-başına NABIZ
    # damgaları da taşır ({prompt|pretool|postwrite|denetle|acilis: ISO});
    # bu yüzden yazım MERGE'dir — diğer anahtarlar asla silinmez.
    veri = {}
    if os.path.isfile(iz_yolu):
        try:
            with open(iz_yolu, encoding="utf-8") as f:
                veri = json.load(f) or {}
        except Exception:
            veri = {}
    if not isinstance(veri, dict):
        veri = {}
    onceki_hash = veri.get("hash")
    guncel_hash = hashlib.sha256(cikti.encode("utf-8", errors="replace")).hexdigest()
    degisti = (onceki_hash != guncel_hash)
    try:
        os.makedirs(defter, exist_ok=True)
        veri["hash"] = guncel_hash
        tmp = f"{iz_yolu}.tmp.{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False)
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


def _payload_dosya_yollari(veri):
    """B-4 (v0.5.14) — payload'ın taşıdığı TÜM dosya yollarını sırayla döndürür.

    İki sözleşme birden desteklenir (kök keşfi yalnız birincisini okuduğu için
    SUNUM KİLİDİ saha kurulumunda ölüydü):
      · `tool_input.file_path`  — Write/Edit (PostToolUse) sözleşmesi
      · `tool_input.files`      — SendUserFile sözleşmesi (str VEYA liste)
      · `tool_response.filePath`— araç yanıtı
    Sıra deterministiktir; tekrar eden yol bir kez döner. ASLA fırlatmaz."""
    yollar, gorulen = [], set()

    def _ekle(deger):
        if isinstance(deger, (list, tuple)):
            for d in deger:
                _ekle(d)
            return
        if not isinstance(deger, str) or not deger.strip():
            return
        if deger not in gorulen:
            gorulen.add(deger)
            yollar.append(deger)

    try:
        if not isinstance(veri, dict):
            return []
        ti = veri.get("tool_input")
        if isinstance(ti, dict):
            _ekle(ti.get("file_path"))
            _ekle(ti.get("files"))
        tr = veri.get("tool_response")
        if isinstance(tr, dict):
            _ekle(tr.get("filePath"))
    except Exception:
        return yollar
    return yollar


def _dava_koku_yukari_ara(baslangic_yol, maks_derinlik=30):
    """B-4 (v0.5.14) — `_defter_koku_yukari_ara`nın GEVŞEK kardeşi: ölçüt
    `_oa/defter` değil `_dosya_klasoru_mu` (defteri henüz doğmamış dava
    klasörü de bulunur). Yalnız katı arama boş döndüğünde çağrılır — aday
    listesinin sırası (dolayısıyla mevcut davranış) korunur.
    ASLA fırlatmaz."""
    try:
        yol = os.path.abspath(str(baslangic_yol))
    except Exception:
        return None
    if not os.path.isdir(yol):
        yol = os.path.dirname(yol)
    onceki, derinlik = None, 0
    while yol and yol != onceki and derinlik < maks_derinlik:
        try:
            if _dosya_klasoru_mu(yol):
                return yol
        except Exception:
            pass
        onceki = yol
        yol = os.path.dirname(yol)
        derinlik += 1
    return None


def _hook_stdin_payload_oku():
    """C2 (v0.5.8.5) — hook stdin payload'ını BİR KEZ okur: stdin bir TTY ise
    (elle interaktif çağrı) ASLA okuma-bekleme yapılmaz; okunamaz/boş/bozuk/
    dict-olmayan payload'da None döner. stdin tek kullanımlıktır — aynı süreçte
    ikinci okuma boş döner; bu yüzden payload'a hem kök keşfi hem içerik
    taraması gereken gövdeler (hook_pretool) bunu KENDİLERİ çağırıp sonucu
    `_hook_kok_adaylarini_bul`a parametreyle geçirir (payload bir kez okunur
    ilkesi). v0.5.11 (T4a): ilk başarılı okuma MODÜL ÖNBELLEĞİNE alınır —
    stdin İKİNCİ KEZ OKUNMAZ (sözleşme aynen), ama aynı süreçte sonraki
    çağrılar (ör. `_payload_oturum`) önbellekten aynı dict'i alır.
    ASLA istisna fırlatmaz."""
    global _PAYLOAD_ONBELLEK
    if _PAYLOAD_ONBELLEK is not None:
        return _PAYLOAD_ONBELLEK
    try:
        if sys.stdin.isatty():
            return None
        ham = sys.stdin.read()
        if not ham:
            return None
        veri = json.loads(ham)
        if isinstance(veri, dict):
            _PAYLOAD_ONBELLEK = veri
            return veri
        return None
    except Exception:
        return None


_PAYLOAD_ONBELLEK = None


def _payload_oturum():
    """T4a — bu hook sürecinin payload'ındaki session_id (önbellekten;
    stdin yeniden OKUNMAZ). Payload yoksa None. ASLA fırlatmaz."""
    try:
        return (_PAYLOAD_ONBELLEK or {}).get("session_id") or None
    except Exception:
        return None


def _hook_kok_adaylarini_bul(kok_arg, payload=None):
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
        VE `tool_input.files` (B-4/v0.5.14: SendUserFile sözleşmesi; yoksa
        `tool_response.filePath`): PostToolUse'un YENİ YAZDIĞI
        dosyanın kendi yolundan `_defter_koku_yukari_ara` ile yukarı
        yürünerek `_oa/defter` içeren ilk ata dizin bulunursa aday listesine
        eklenir — (1)/(2)/(4) hiçbiri dava köküne değmediğinde (gerçek saha
        dağıtımı: oturum CWD'si dava klasörünün DIŞINDA) hook'u artık KÖR
        bırakmaz;
    (4) `CLAUDE_PROJECT_DIR` ortam değişkeni;
    (5) mevcut CWD ('.') — eski davranış, HER ZAMAN aday listesine dahildir
        (geriye uyum — hiçbir eski senaryo bu keşifle kaybolmaz).

    `payload` (C2, v0.5.8.5 — KÖK SİMETRİSİ): çağıran gövde stdin payload'ını
    ZATEN okuduysa (hook_pretool — payload'ı içerik taraması için de kullanır)
    buraya geçirir; stdin İKİNCİ KEZ okunMAZ ('payload bir kez okunur').
    Verilmezse stdin buradan (bir kez) okunur — hook_denetle/hook_postwrite/
    hook_prompt'un mevcut davranışı."""
    adaylar = []
    if kok_arg and kok_arg != ".":
        adaylar.append(kok_arg)
    else:
        try:
            veri = payload if payload is not None else _hook_stdin_payload_oku()
            if veri:
                stdin_cwd = veri.get("cwd")
                if stdin_cwd:
                    adaylar.append(stdin_cwd)
                # DÜZELTME (madde 3) — bkz. docstring (3).
                # B-4 (v0.5.14): `file_path` TEK SÖZLEŞME DEĞİLDİR. SendUserFile
                # payload'ı yolu `tool_input.files` (str veya liste) alanında
                # taşır; kök keşfi onu okumadığı için oturum dava klasörünün
                # DIŞINDAYKEN SUNUM KİLİDİ sessizce ölüydü (EXIT=0, çıktı yok).
                for dosya_yolu in _payload_dosya_yollari(veri):
                    bulunan = (_defter_koku_yukari_ara(dosya_yolu)
                               or _dava_koku_yukari_ara(dosya_yolu))
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
        # C3 (v0.5.8.5) — ÖLÜ-PROMPT UYARISI yalnız kapanış-sınıfı koşuda ve
        # PARMAK İZİNE GİREREK basılır: durum değişmeden tekrar tekrar basmak
        # mevcut gürültü disiplinini (defter değişmeden ikinci koşu SESSİZ)
        # bozardı; durum değiştiğinde (damga doğdu/öldü) yeniden görünür olur.
        if hook_adi == "Stop/SessionEnd":
            nabiz_uyari = _hook_nabiz_prompt_uyarisi(kok_aday)
            if nabiz_uyari:
                cikti = f"{nabiz_uyari}\n{cikti}"
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
        # HOOK OLAY İZİ (v0.5.8.4): gövde fiilen çıktı bastı → deftere iz düş.
        _hook_olay_yaz(kok_aday,
                       "postwrite" if hook_adi == "PostToolUse" else "denetle",
                       "denetim çıktısı basıldı (gövde ateşledi)")
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


# ── BAYAT-TOHUM AŞISI (v0.5.7 — Denizli 754 saha bulgusu) ──────────────────
# Saha gerçeği: model, `_oa/araclar/` kopyalarını yüklü eklentiden değil
# KOMŞU dava klasöründen almıştı — 20/20 script eski nesildi (ingest v1.1
# vs v1.7). Sonuç: Gate A/C, OCR nöbetçisi, makbuz/sha kapıları, DAMGA ve
# KAYNAK-URL disiplini o koşuda FİİLEN yoktu. Eski koşuların doğaçlama
# kopyaları kendi kendini çoğaltıyordu: her yeni dosya, komşusundan
# Temmuz-başı kod miras alıyordu.
#
# AŞI: bu fonksiyon `_oa/araclar/*.py` kopyalarını YÜKLÜ eklentinin kendi
# scriptleriyle BAYT-karşılaştırır. Fark = BAYAT. Uyarı ÜRETİR, BLOKLAMAZ
# (amaç çizgisi) — ama hook katmanı sayesinde her turda görünür ve tek
# kalıcı susturucusu kopyaları tazelemektir. Kendi konumunu `__file__`dan
# çözer: hook, eklenti kökünden koştuğu için karşılaştırma her zaman
# GÜNCEL sürüme karşıdır. ASLA istisna fırlatmaz.

# ── H2a (v0.5.8.6 — 777 saha dersi) — ÖZELLİK PARMAK İZİ ───────────────────
# Bayt-kıyası "eklentideki güncel dosyadan FARKLI mı" sorusuna bakar; ama
# fark her zaman tehlikeyi anlatmaz (yorum satırı da fark üretir) ve indeks
# bulunamadığında kör kalır. 777 filosunda model bayat kiti `_oa/araclar`a
# kopyalayıp koştu: eski udf_yaz AÇILAMAYAN UDF üretti, eski teslim_paketi
# kanonik makbuz (defter/teslim-makbuz.json) hiç yazmadı. Bu tablo, kritik
# kopyaların KENDİ İÇERİĞİNDEN okunan zorunlu özellik dizgeleridir — eksik
# dizge = kopya bu özelliklerin OLMADIĞI bir nesilden geliyor demektir
# ("BAYAT NESİL"), uyarı sınıfı yükselir: üretimde KULLANMA.
_OZELLIK_PARMAK_IZI = {
    "udf_yaz.py": ("_sayfa_kenari_yonetmelik",   # v0.5.8.3 şekil standardı (4×42.52)
                   "hvl-default",                 # v0.5.8.4 stil-tanımı üretimi
                   "udf-uretim-makbuz"),          # v0.5.8.4 üretim makbuzu
    "teslim_paketi.py": ("teslim-makbuz.json",),  # kanonik makbuz (tek ölçüt)
    "oa_hafiza.py": ("--damga",),                 # içtihat muhakeme ritüeli
    # v0.5.11 (1865-T1): rpm anlık-görüntüsünden gelen 20KB'lik erken-nesil
    # pipeline_kayit kopyaları da yakalansın — defter/nabız çekirdeği imzaları.
    "pipeline_kayit.py": ("_hook_nabiz_damgala", "OLAYLAR_ADI"),
}

# ═══════════ v0.5.11 — KİT GÜVENLİK KATMANI (1865 karnesi T1/T3/T4a/T5) ═════
# Saha kanıtı: onarılan kit, masaüstü uygulamasının rpm anlık-görüntü
# yolundan 9 dk sonra eski nesille geri ezildi (777'den beri 3. nüks); onu
# durduran tek şey dosya-düzeyi koruma (salt-okunur) oldu. Doktrin: kit
# güvenilir kaynaktan doğar, kilitli yaşar, yönünü bilir.

# rpm / uygulama anlık-görüntüsü yolu — araç KAYNAĞI olarak YASAK (bayat
# nesil deposu; 777 kök nedeni). Desen hem / hem \ ayırıcıyla eşleşir.
_RPM_YOL_DESENI = re.compile(
    r"local[-_]agent[-_]mode[-_]sessions|AppData[/\\]Roaming[/\\]Claude[/\\]",
    re.I)
_ARACLAR_HEDEF_DESENI = re.compile(r"_oa[/\\]araclar", re.I)

_CEKIRDEK_SCRIPTLER = ("pipeline_kayit.py", "teslim_paketi.py", "udf_yaz.py")


# B-5 (v0.5.14) — POZİTİF SÜRÜM KANITI. Parmak izi tablosu NEGATİF bir
# ölçüttür: "eksik dizge yoksa temiz" der. Denetimde ölçüldü — tablonun en
# yeni imzaları v0.5.11 çekirdeğine aitti ve 0.5.9.1 kitinde ZATEN vardı;
# dolayısıyla ≥0.5.9 her nesil otomatik "taze" ilan ediliyordu ("kanaldan
# YENİ … bayat DEĞİLDİR, tazeleme gerekmez"). Nöbetçi kendi neslini referans
# aldığı için bayat kurulumun bayat olduğunu YAPISAL OLARAK göremiyordu.
# Onarım: hüküm artık dosyanın KENDİ İÇİNDEKİ makine-okur sürüm damgasına
# dayanır. Damga yoksa cevap "taze" değil BİLİNMİYOR'dur.
_ARAC_SURUM_RE = re.compile(
    r"""^\s*OA_SURUM\s*=\s*["']([0-9][0-9A-Za-z.\-]*)["']""", re.M)


def _arac_surum_damgasi(icerik):
    """Script gövdesindeki makine-okur `OA_SURUM = "x.y.z"` damgasını döndürür;
    damga yoksa None ('bilinmiyor'). ASLA fırlatmaz."""
    try:
        m = _ARAC_SURUM_RE.search(str(icerik or ""))
        return m.group(1) if m else None
    except Exception:
        return None


def _arac_dosya_surumu(yol):
    """Diskteki bir araç kopyasının sürüm damgası (yoksa/okunamazsa None)."""
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            return _arac_surum_damgasi(f.read())
    except OSError:
        return None


def _eklenti_script_indeksi():
    """Yüklü eklentinin `skills/*/scripts/*.py` indeksi {ad: yol} (kanal =
    tek meşru kaynak). Deterministik sıralı; ASLA fırlatmaz."""
    indeks = {}
    try:
        skills_kok = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        for parca in sorted(os.listdir(skills_kok)):
            sdir = os.path.join(skills_kok, parca, "scripts")
            if not os.path.isdir(sdir):
                continue
            for ad in sorted(os.listdir(sdir)):
                if ad.endswith(".py") and ad not in indeks:
                    indeks[ad] = os.path.join(sdir, ad)
    except Exception:
        pass
    return indeks


def _kopya_taze_kaniti(ad, yol, icerik=None, indeks=None):
    """B-5 (v0.5.14) — bir `_oa/araclar/` kopyası için POZİTİF tazelik kanıtı.

    Döner: `("taze", kanıt)` | `("bayat", damga)` | `("bilinmiyor", None)`.
    Kabul edilen İKİ pozitif kanıt (ikisi de artefakta bağlıdır, beyana değil):
      (a) kopya kanal kaynağıyla BAYT-ÖZDEŞ (en güçlü kanıt; damgası olmayan
          scriptler bu yoldan doğrulanır),
      (b) kopyanın makine-okur `OA_SURUM` damgası eklentininkinden küçük değil.
    Hiçbiri gösterilemiyorsa cevap "taze" DEĞİL, "bilinmiyor"dur. ASLA
    fırlatmaz."""
    try:
        if icerik is None:
            with open(yol, encoding="utf-8", errors="replace") as f:
                icerik = f.read()
    except OSError:
        return "bilinmiyor", None
    try:
        kaynak = (indeks if indeks is not None else _eklenti_script_indeksi()).get(ad)
        if kaynak and os.path.isfile(kaynak):
            with open(yol, "rb") as f1, open(kaynak, "rb") as f2:
                if f1.read() == f2.read():
                    return "taze", "bayt-özdeş"
    except OSError:
        pass
    damga = _arac_surum_damgasi(icerik)
    if damga is None:
        return "bilinmiyor", None
    if _surum_tuple(damga) < _OA_SURUM_TUPLE:
        return "bayat", damga
    return "taze", "sürüm %s" % damga


def _pretool_rpm_karantina_mi(metin):
    """P0-1 karar çekirdeği: komut metninde rpm-yolu deseni VE `_oa/araclar`
    hedefi BİRLİKTE var mı? Tek başına hiçbiri karantina değildir (rpm
    yolundan OKUMAK serbest; araclar'a meşru kaynaktan kopya serbest).
    ASLA fırlatmaz."""
    try:
        m = str(metin or "")
        return bool(_RPM_YOL_DESENI.search(m)
                    and _ARACLAR_HEDEF_DESENI.search(m))
    except Exception:
        return False


def _pretool_cekirdek_yazimi_mi(veri):
    """P0-2 karar çekirdeği: Write/Edit hedefi `_oa/araclar/` altındaki bir
    ÇEKİRDEK script mi? (Çekirdek elle yazılmaz — kaynaktan kopyalanır;
    1865: üç çekirdek 14-20KB taklitlerle ezilmişti.) ASLA fırlatmaz."""
    try:
        if not isinstance(veri, dict):
            return False
        if veri.get("tool_name") not in ("Write", "Edit"):
            return False
        ti = veri.get("tool_input")
        yol = str((ti or {}).get("file_path") or "")
        if not _ARACLAR_HEDEF_DESENI.search(yol):
            return False
        return os.path.basename(yol) in _CEKIRDEK_SCRIPTLER
    except Exception:
        return False


def _cekirdek_kilitle(kok):
    """P0-2: `_oa/araclar/`daki çekirdek scriptlerden SÜRÜM MUTABAKATI olanları
    salt-okunur yapar (bayat/taklit kit KİLİTLENMEZ — çöp mühürlenmez; onun
    yolu tazeleme + BAYAT NESİL uyarısıdır). İdempotent; kilitlenen dosya
    sayısını döndürür. ASLA fırlatmaz.

    B-5 (v0.5.14): kilit ölçütü artık parmak izi DEĞİL, makine-okur sürüm
    damgasıdır. Denetimde ölçüldü — parmak izi tam ama nesli 0.5.9.1 olan bir
    kit kilitleniyordu; kilit o bayat çekirdeği koruyan bir ÇİVİYE dönüşüyor,
    düz kopyayla tazeleme izin hatasıyla düşüyordu. Sürüm kanıtı yoksa
    (damga okunamıyor ya da eklentininkinden eski) DOSYA KİLİTLENMEZ."""
    kilitlenen = 0
    try:
        araclar = os.path.join(kok, "_oa", "araclar")
        for ad in _CEKIRDEK_SCRIPTLER:
            yol = os.path.join(araclar, ad)
            if not os.path.isfile(yol):
                continue
            try:
                with open(yol, encoding="utf-8", errors="replace") as f:
                    icerik = f.read()
            except OSError:
                continue
            # (a) POZİTİF TAZELİK KANITI — damgasız/eski kopya çivilenmez (B-5).
            durum, _ayrinti = _kopya_taze_kaniti(ad, yol, icerik)
            if durum != "taze":
                continue
            imzalar = _OZELLIK_PARMAK_IZI.get(ad)
            if imzalar:
                if any(dz not in icerik for dz in imzalar):
                    continue          # eksik nesil — kilitleme
            try:
                mod = os.stat(yol).st_mode
                if mod & stat.S_IWRITE:
                    os.chmod(yol, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
                kilitlenen += 1
            except OSError:
                continue
    except Exception:
        pass
    return kilitlenen


def _son_oturum_oku(kok):
    """P1-4a köprüsü: hook'ların `.hook-son-iz.json`a yazdığı `son_oturum`
    değerini okur — Bash'le koşan scriptler (teslim_paketi, --isle) payload
    alamadığından oturum kimliğini buradan alır. Kesin kimlik DEĞİLDİR
    (en-son-aktif-oturum yaklaşımı); alan adları bunu dürüstçe taşır.
    Yoksa/hata → None."""
    try:
        yolu = os.path.join(kok, "_oa", "defter", ".hook-son-iz.json")
        with open(yolu, encoding="utf-8") as f:
            return json.load(f).get("son_oturum") or None
    except Exception:
        return None


def _taze_oturum_uyarisi(transcript_path, esik_sn=1800):
    """P1-4a: bu oturumun transkript dizininde, KENDİSİ dışında son
    `esik_sn` saniyede değişmiş .jsonl varsa tek satır uyarı (çok-oturum
    görünürlüğü — 1865: 5 paralel oturum kit ezme yarışına girdi).
    Tek oturum → None. ASLA fırlatmaz."""
    try:
        if not transcript_path:
            return None
        dizin = os.path.dirname(os.path.abspath(transcript_path))
        kendim = os.path.normcase(os.path.abspath(transcript_path))
        simdi_ts = time.time()
        taze = 0
        for ad in os.listdir(dizin):
            if not ad.endswith(".jsonl"):
                continue
            yol = os.path.join(dizin, ad)
            if os.path.normcase(os.path.abspath(yol)) == kendim:
                continue
            try:
                if (simdi_ts - os.path.getmtime(yol)) <= esik_sn:
                    taze += 1
            except OSError:
                continue
        if not taze:
            return None
        return ("ÇOK-OTURUM: bu klasörde %d taze oturum izi daha var — "
                "aynı _oa üzerinde paralel çalışılıyor. Kit onarımı/kritik "
                "yazımlar TEK oturumda yapılmalı; defter olayları oturum "
                "damgası taşır." % taze)
    except Exception:
        return None


def _sozlesme_disi_uyarisi(kok):
    """P2-5 (1865-T6 'metin-sororn'): sözleşme-dışı `_oa` alt dizinlerini
    prompt kanalına tek satır taşır (bekçi zaten --denetle'de vardı; typo
    dizin oturum İÇİNDE görünür olsun). Bloklamaz. ASLA fırlatmaz."""
    try:
        disi = _sozlesme_disi_dizinler(kok)
        if not disi:
            return None
        return ("SÖZLEŞME-DIŞI DİZİN: _oa altında bilinmeyen dizin(ler): "
                + ", ".join(sorted(disi)[:4])
                + " — yazım hatası olabilir (ör. 'metin-sororn'); içerik "
                  "doğru dizine taşınmalı (bloklamaz).")
    except Exception:
        return None


def _manifest_once_uyarisi(kok):
    """P2-6 (1865-T7): künye (`_oa/metin/00-kunye.json`) HENÜZ YOKKEN künye
    teyit kütüğü satır almaya başladıysa — araştırma sayım kapısından önce
    derinleşiyor demektir — tek satır hatırlatma. Bloklamaz. ASLA fırlatmaz."""
    try:
        kunye = os.path.join(kok, "_oa", "metin", "00-kunye.json")
        if os.path.isfile(kunye):
            return None
        kutuk = os.path.join(kok, "_oa", "teyit", "kunye-teyit.md")
        if not os.path.isfile(kutuk) or os.path.getsize(kutuk) == 0:
            return None
        return ("MANİFEST ÖNCE: evrak sayım kapısı (00-kunye.json) henüz "
                "kurulmadan içtihat araştırması derinleşiyor — oa_ingest "
                "künye+INDEX üretimini tamamla (sayım tutmazsa analiz "
                "başlamaz kuralı).")
    except Exception:
        return None


def _bayat_nesil_listesi(kok):
    """H2a — `_oa/araclar/`daki KRİTİK kopyalarda özellik parmak izi taraması.
    Döner: `["udf_yaz.py (eksik: hvl-default, ...)", ...]` (sıralı; temizse
    boş liste). ASLA istisna fırlatmaz."""
    bulgular = []
    try:
        araclar = os.path.join(kok, "_oa", "araclar")
        if not os.path.isdir(araclar):
            return bulgular
        for ad in sorted(_OZELLIK_PARMAK_IZI):
            yol = os.path.join(araclar, ad)
            if not os.path.isfile(yol):
                continue
            try:
                with open(yol, encoding="utf-8", errors="replace") as f:
                    icerik = f.read()
            except OSError:
                continue
            eksik = [dz for dz in _OZELLIK_PARMAK_IZI[ad] if dz not in icerik]
            if eksik:
                bulgular.append(f"{ad} (eksik: {', '.join(eksik)})")
    except Exception:
        return []
    return bulgular


def _bayat_arac_uyarisi(kok):
    """`_oa/araclar/` kopyaları yüklü eklentiyle bayt-özdeş mi? + H2a: kritik
    kopyalarda özellik parmak izi tam mı? Bayat kopya VEYA bayat-nesil bulgu
    varsa görünür uyarı metni, yoksa None döndürür."""
    try:
        araclar = os.path.join(kok, "_oa", "araclar")
        if not os.path.isdir(araclar):
            return None
        indeks = _eklenti_script_indeksi()
        bayat = []
        for ad in sorted(os.listdir(araclar)):
            if not ad.endswith(".py") or ad not in indeks:
                continue
            kopya = os.path.join(araclar, ad)
            try:
                with open(kopya, "rb") as f1, open(indeks[ad], "rb") as f2:
                    if f1.read() != f2.read():
                        bayat.append(ad)
            except OSError:
                continue
        # H2a — ÖZELLİK PARMAK İZİ: eksik dizge = BAYAT NESİL (sınıf yükselir).
        nesil = _bayat_nesil_listesi(kok)
        # v0.5.11 P1-3 (1865-T5) — YÖN AYRIMI: bayt-farklı bir kopya her zaman
        # "bayat" değildir; kanaldan YENİ nesil de olabilir (depo klonundan
        # tazelenmiş kit + henüz güncellenmemiş kurulum). Yanlış-yön gürültüsü
        # gerçek uyarının itibarını yer.
        # B-5 ONARIMI (v0.5.14): bu ayrım NEGATİF parmak izine dayanıyordu —
        # parmak izi tam olan HER kopya "kanaldan YENİ … tazeleme gerekmez"
        # ilan ediliyordu; ölçüldü: gerçekten bayat bir 0.5.9.1 kiti bu yoldan
        # "taze" damgası aldı. Artık hüküm POZİTİF KANITA bağlıdır ve kanıt
        # gösterilemeyen kopya "taze" değil BİLİNMİYOR sınıfına düşer.
        yeni = []
        if bayat:
            kalan = []
            for ad in bayat:
                yol_ = os.path.join(araclar, ad)
                durum, ayrinti = _kopya_taze_kaniti(ad, yol_, indeks=indeks)
                if durum == "taze":
                    yeni.append("%s (%s)" % (ad, ayrinti))
                elif durum == "bayat":
                    kalan.append("%s (damga %s < %s)" % (ad, ayrinti, OA_SURUM))
                else:
                    # KANIT YOK → "taze" DEĞİL. Fail-closed varsayılan: bu
                    # kopya bayat muamelesi görür ve tazelenmesi istenir
                    # (B-5: "doğrulayamıyorsan 'taze' DEME").
                    kalan.append("%s (nesli doğrulanamadı)" % ad)
            bayat = kalan
        if not bayat and not nesil and not yeni:
            return None
        parcalar = []
        if nesil:
            parcalar.append(
                "⛔ BAYAT NESİL ARAÇ — üretimde KULLANMA; güncel kaynak: YÜKLÜ "
                "eklenti (`skills/*/scripts/`):\n"
                "  " + "; ".join(nesil[:6])
                + (" … (+%d)" % (len(nesil) - 6) if len(nesil) > 6 else "") + "\n"
                "  Bu kopyalar kritik özellik parmak izlerinden YOKSUN — eski nesil\n"
                "  udf_yaz AÇILAMAYAN UDF üretir, eski teslim_paketi kanonik makbuz\n"
                "  (defter/teslim-makbuz.json) yazmaz, eski oa_hafiza --damga\n"
                "  ritüelini bilmez (777 saha bulgusu).")
        if bayat:
            parcalar.append(
                "⚠ BAYAT ARAÇ UYARISI — `_oa/araclar/` kopyaları yüklü eklentiden ESKİ:\n"
                "  " + ", ".join(bayat[:12])
                + (" … (+%d)" % (len(bayat) - 12) if len(bayat) > 12 else "") + "\n"
                "  ('nesli doğrulanamadı' = kopya kanaldan farklı ve tazelik KANITI\n"
                "  yok — ne bayt-özdeşlik ne makine-okur `OA_SURUM` damgası; B-5\n"
                "  gereği bu sınıf 'taze' SAYILMAZ, kurulum güncellemesi istenir.)\n"
                "  Bu kopyalarla koşan adımlar güncel kapılardan (makbuz/sha, OCR\n"
                "  nöbetçisi, DAMGA, KAYNAK-URL) YOKSUN olabilir. Tazele: kopyaları\n"
                "  YÜKLÜ eklentinin `skills/*/scripts/` kökünden YENİDEN al — komşu\n"
                "  dava klasöründen ASLA kopyalama (bayat-tohum bulaşması,\n"
                "  Denizli 754 saha bulgusu). Bu bir ENGEL DEĞİLDİR; görünürlüktür.")
        if yeni:
            parcalar.append(
                "ℹ kit kanaldan FARKLI ama TAZELİK KANITLI (kanaldan YENİ): "
                + ", ".join(yeni[:6])
                + " — kurulumu güncelleyince bu not susar (v0.5.11 yön ayrımı, "
                  "v0.5.14 pozitif kanıt; tazeleme gerekmez).")
        return "\n".join(parcalar)
    except Exception:
        return None


def _arac_version_uyarisi(kok):
    """H2b (v0.5.8.6) — `_oa/araclar/VERSION.json` sürüm damgası denetimi:
    (a) `_oa/araclar` VAR ama VERSION.json YOK → "damgasız araç çantası";
    (b) VERSION.json var ama `surum` alanı `OA_SURUM`dan FARKLI → bayat çanta.
    Uyumluysa/araclar yoksa None. ASLA istisna fırlatmaz, ASLA bloklamaz."""
    try:
        araclar = os.path.join(kok, "_oa", "araclar")
        if not os.path.isdir(araclar):
            return None
        vy = os.path.join(araclar, "VERSION.json")
        if not os.path.isfile(vy):
            return ("⚠ DAMGASIZ ARAÇ ÇANTASI — `_oa/araclar/` var ama "
                    "`_oa/araclar/VERSION.json` YOK: kopyaların hangi sürümden "
                    "alındığı bilinmiyor (777 dersi: bayat kit sessizce koştu). "
                    "Kopyaları YÜKLÜ eklentiden tazele ve damgayı bas: "
                    '`_oa/araclar/VERSION.json` = {"surum": "' + OA_SURUM + '"}. '
                    "Bu bir ENGEL DEĞİLDİR; görünürlüktür.")
        try:
            with open(vy, encoding="utf-8") as f:
                v = json.load(f)
            surum = v.get("surum") if isinstance(v, dict) else None
        except Exception:
            surum = None
        if surum != OA_SURUM:
            return ("⚠ BAYAT ARAÇ ÇANTASI — `_oa/araclar/VERSION.json` sürümü "
                    f"({surum or 'okunamadı'}) yüklü eklentiden ({OA_SURUM}) FARKLI: "
                    "kopyalar eski nesil olabilir; YÜKLÜ eklentiden tazele ve "
                    "damgayı güncelle. Bu bir ENGEL DEĞİLDİR; görünürlüktür.")
        # B-5 (v0.5.14) — BEYAN ARTEFAKTLA DOĞRULANIR. VERSION.json bir
        # BEYANDIR; denetimde ölçüldü: gerçekten bayat bir kite elle
        # `{"surum": "<güncel>"}` yazmak bu kanalı tamamen susturuyordu.
        # Ailenin kendi doktrini "makbuz artefakta bağlanır, beyana değil"
        # der; beyan artık çantadaki çekirdeğin kendi damgasıyla sınanır.
        indeks = _eklenti_script_indeksi()
        yalanci = []
        for ad in sorted(os.listdir(araclar)):
            if not ad.endswith(".py") or ad not in indeks:
                continue
            durum, ayrinti = _kopya_taze_kaniti(
                ad, os.path.join(araclar, ad), indeks=indeks)
            if durum == "bayat":
                yalanci.append("%s (damga %s)" % (ad, ayrinti))
        if yalanci:
            return ("⛔ DOĞRULANMAYAN SÜRÜM BEYANI — `_oa/araclar/VERSION.json` "
                    f"`{OA_SURUM}` diyor ama çantadaki kopyaların kendi damgası "
                    "DAHA ESKİ:\n"
                    "  " + ", ".join(yalanci[:12])
                    + (" … (+%d)" % (len(yalanci) - 12) if len(yalanci) > 12 else "") + "\n"
                    "  Beyana değil ARTEFAKTA bakılır (B-5): kopyaları YÜKLÜ "
                    "eklentiden yeniden al.\n"
                    "  Bu bir ENGEL DEĞİLDİR; görünürlüktür.")
        return None
    except Exception:
        return None


# ── AĞ-İMPORT SAHA TARAMASI (v0.5.8.4 — bayat-tohum aşısının kardeşi) ──────
# YASAK-NÖBETÇİSİ (aile_dogrula.py, v0.5.8 P5) çekirdek scriptleri sürüm
# kapısında denetler — ama `_oa/araclar/` KOPYALARI o kapıdan hiç geçmez:
# sahada elle düzenlenmiş/komşudan miras bir kopyaya ağ importu eklenirse
# Layer 0 (müvekkil verisi python katmanından dışarı çıkamaz) o koşuda
# FİİLEN delinir ve hiçbir kapı görmez. Bu tarama aynı satır-başı deseni
# (aile_dogrula.py:135-137'deki listeyle BİREBİR — tek kaynak orasıdır,
# liste değişirse buraya da taşınır) saha kopyalarına uygular.
_AG_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|urllib3|socket|"
    r"openai|anthropic|groq|litellm|http\.client|urllib\.request)\b")


def _arac_ag_import_uyarisi(kok):
    """`_oa/araclar/*.py` kopyalarında satır-başı ağ-import var mı? Bulgu
    listesi varsa görünür uyarı metni, yoksa None. ASLA istisna fırlatmaz."""
    try:
        araclar = os.path.join(kok, "_oa", "araclar")
        if not os.path.isdir(araclar):
            return None
        bulgular = []
        for ad in sorted(os.listdir(araclar)):
            if not ad.endswith(".py"):
                continue
            try:
                with open(os.path.join(araclar, ad),
                          encoding="utf-8", errors="replace") as f:
                    icerik = f.read()
            except OSError:
                continue
            for i, satir in enumerate(icerik.splitlines(), 1):
                m = _AG_IMPORT_RE.match(satir)
                if m:
                    bulgular.append(f"{ad}:{i} ({m.group(1)})")
        if not bulgular:
            return None
        return (
            "⚠ AĞ-İMPORT UYARISI — `_oa/araclar/` kopyalarında ağ kütüphanesi importu:\n"
            "  " + ", ".join(bulgular[:12])
            + (" … (+%d)" % (len(bulgular) - 12) if len(bulgular) > 12 else "") + "\n"
            "  Çekirdek script ağ kütüphanesi TAŞIYAMAZ (Layer 0 / m.0 devşirme\n"
            "  protokolü — müvekkil verisi python katmanından dışarı çıkamaz).\n"
            "  Kopyayı YÜKLÜ eklentinin `skills/*/scripts/` kökünden yeniden al;\n"
            "  elle eklenmiş importsa KALDIR. Bu bir ENGEL DEĞİLDİR; görünürlüktür.")
    except Exception:
        return None


# ── HOOK OLAY İZİ (v0.5.8.4 — 372 kanıtı: defterde hook tipli olay 0'dı) ───
# Hook gövdeleri fiilen iş yaptığında (enjeksiyon bastı / uyarı üretti / ask
# kararı verdi) izleri yan dosyalarda (.hook-son-iz.json, stderr) kayboluyordu
# — defter, oturumun TEK gerçeklik kaynağıyken hook nöbetinin hiç izi yoktu.
# Bu yardımcı, defter VARSA pipeline-olaylar.jsonl'e tek satırlık bir "hook"
# olayı APPEND eder (araç-imzalı — elle düşürülmüş satırdan ayırt edilir).
# `derle` bilinmeyen tipleri zaten yok sayar → durum derlemesi bozulmaz.
# Sessiz-başarısız: hiçbir hata dışarı sızmaz, hook ASLA bloklanmaz.
def _hook_olay_yaz(kok, olay_adi, not_metni, oturum=None):
    try:
        defter = os.path.join(kok, "_oa", "defter")
        if not os.path.isdir(defter):
            return
        olay = {"zaman": simdi(), "tip": "hook", "olay": olay_adi,
                "not": str(not_metni or "")[:200]}
        # v0.5.11 (1865-T4a): olay hangi oturumun ürünü — payload session_id.
        # Yoksa son-iz köprüsünden best-effort (kesinlik iddiasız).
        oturum = oturum or _son_oturum_oku(kok)
        if oturum:
            olay["oturum"] = str(oturum)[:64]
        olay["imza"] = _imza_hesapla(olay)
        olay_ekle(os.path.join(defter, OLAYLAR_ADI), olay)
    except Exception:
        pass


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
    (`NNN_...`/`NNNN_...` adlandırması), `_oa` kökü YA DA — C1 KLON İMZASI
    (v0.5.8.5, saha ölümü: UserPromptSubmit klon kökünde hiç ateşlemedi) —
    Yargı PRO klon kökü işaretleri: kökte `uyap-project.json` VEYA `evraklar/`
    dizini VEYA (`INDEX.md` ∧ `dava-analiz.md`) çifti. INDEX.md TEK BAŞINA
    yeterli DEĞİLDİR (her markdown deposu dava klasörü sanılmasın — yanlış-
    pozitif disiplini). ASLA istisna fırlatmaz."""
    try:
        if os.path.isdir(os.path.join(kok, "_oa")):
            return True
        # C1 — KLON İMZASI: klon köklerinde NNN_ evrak deseni YOKTUR; evraklar
        # alt klasörde durur ve kökte proje/indeks dosyaları bulunur.
        if os.path.isfile(os.path.join(kok, "uyap-project.json")):
            return True
        if os.path.isdir(os.path.join(kok, "evraklar")):
            return True
        if (os.path.isfile(os.path.join(kok, "INDEX.md"))
                and os.path.isfile(os.path.join(kok, "dava-analiz.md"))):
            return True
        sayac = 0
        for girdi in os.scandir(kok):
            # C1 — desen ^\d{3}[_-] → ^\d{3,4}[_-]: 4 haneli (yıl) önekli
            # evrak adları da UYAP indirmesi sayılır (ör. `2024_...`).
            if girdi.is_file() and re.match(r"^\d{3,4}[_-]", girdi.name):
                sayac += 1
                if sayac >= 3:      # üç numaralı evrak = UYAP indirmesi
                    return True
        return False
    except Exception:
        return False


# ── A4 (v0.5.9) — ZİNCİR DURUMU (UserPromptSubmit → kesintisiz akış özeti) ─
def _zincir_durumu_ozeti(kok):
    """Defter VARKEN her tura 2-3 satırlık MEKANİK zincir özeti: son
    UYGULANDI halka + sıradaki adım + bekleyen avukat kararı sayısı +
    mühürsüz/makbuz kısa durumu — model her turda zincirdeki YERİNİ bilerek
    düşünür (KESİNTİSİZ ilkesi: bağlantılı düşünme her turda akar).
    Kaynak: pipeline-durum.json (türev görünüm). Dosya yok/bozuksa None —
    boş kabuk defter dizini (durum hiç derlenmemiş) gürültü üretmez, mevcut
    sessizlik sözleşmeleri korunur. ASLA fırlatmaz."""
    try:
        durum_yol = os.path.join(kok, "_oa", "defter", DURUM_ADI)
        if not os.path.isfile(durum_yol):
            return None
        with open(durum_yol, encoding="utf-8") as f:
            d = json.load(f)
        if not isinstance(d, dict) or not isinstance(d.get("adimlar"), dict):
            return None
        # Son UYGULANDI halka — gunluk (append-only sıra) SONDAN taranır.
        son = None
        for kayit in reversed(d.get("gunluk") or []):
            if kayit.get("durum") == "UYGULANDI":
                if kayit.get("katman"):
                    son = f"katman {kayit['katman']}"
                else:
                    no = str(kayit.get("adim"))
                    ad = (d["adimlar"].get(no) or {}).get("ad") or f"ADIM-{no}"
                    son = f"adım {no} ({ad}) / {kayit.get('parca')}"
                break
        try:
            siradaki = _siradaki(d)
        except Exception:
            siradaki = "türetilemedi"
        try:
            bekleyen = len(_avukat_karari_bekleyen(d))
        except Exception:
            bekleyen = 0
        muhursuz_sayi = len([x for x in _muhursuz_teslim_listesi(kok)
                             if x.get("durum") in ("muhursuz", "bayat")])
        m, _hata = _makbuz_oku(kok)
        if m is None:
            makbuz = "YOK"
        elif m.get("exit_kodu") == 0:
            makbuz = "YEŞİL"
        else:
            makbuz = "KIRMIZI (exit≠0)"
        return "\n".join([
            "ZİNCİR DURUMU (v0.5.9 — pipeline-durum.json'dan mekanik özet):",
            f"  son UYGULANDI: {son or 'henüz yok'} · sıradaki: {siradaki}",
            f"  bekleyen avukat kararı: {bekleyen} · mühürsüz teslim ürünü: "
            f"{muhursuz_sayi} · teslim makbuzu: {makbuz}",
        ])
    except Exception:
        return None


def hook_prompt(kok=None):
    """UserPromptSubmit — devir yükümlülüğünü modelin bağlamına enjekte eder.
    Döner: her zaman 0 (ASLA bloklamaz). Hat açıksa hiçbir şey basmaz.

    A4 (v0.5.9) — KESİNTİSİZ AKIŞ: defter VARKEN (ve pipeline-durum.json
    derlenmişken) enjeksiyona 2-3 satırlık ZİNCİR DURUMU özeti eklenir —
    mevcut kısa-blok uyarılarıyla (bayat/ağ-import/kanonik-makbuz/teslim-
    disiplini) AYNI kanalda, tek enjeksiyon. Defter yokken mevcut tam devir
    bloğu AYNEN korunur.

    C2 (v0.5.8.5) — KÖK SİMETRİSİ: kök keşfi artık hook_denetle/hook_postwrite
    ile AYNI `_hook_kok_adaylarini_bul` üzerinden yapılır (stdin payload `cwd`
    + CLAUDE_PROJECT_DIR + süreç CWD'si). Üçüncü saha ölümünün nedeni tam
    buydu: süreç CWD'si dava klasörünün dışındayken bu gövde YALNIZ CWD'ye
    bakıyor ve sessiz no-op'a düşüyordu. Payload bu süreçte BİR KEZ okunur
    (UserPromptSubmit payload'ı tool_input taşımaz; pretool ayrı süreçtir —
    stdin çakışması yapısal olarak yoktur)."""
    try:
        try:
            kokler = _hook_kok_adaylarini_bul(kok)
        except Exception:
            kokler = [os.path.abspath(kok or ".")]
        k = next((aday for aday in kokler if _dosya_klasoru_mu(aday)), None)
        if k is None:
            return 0                                     # dava klasörü değil — sessiz
        # T12 — ÇİFT-KANAL DEDUP: aynı olay aynı saniyede ikinci kez
        # (plugin hooks.json + kullanıcı settings.json çift kaydı) →
        # yan-etkisiz sessiz kısa devre.
        if _hook_dedup_kisa_devre(k, "prompt"):
            return 0
        # C3 — HOOK NABZI: kanca ateşledi; damga defter varsa düşer (sessiz
        # turlarda bile — nabzın amacı tam da sessizlik/ölüm ayrımıdır).
        _hook_nabiz_damgala(k, "prompt", oturum=_payload_oturum())
        if os.path.isdir(os.path.join(k, "_oa", "defter")):
            # Hat açık — devir hatırlatması GEREKSİZ (gürültü disiplini).
            # Ama üç şey AYRICA söylenir (temiz durumda ÜÇÜ DE None → SESSİZ):
            # (a) BAYAT ARAÇ (v0.5.7 aşısı) — hat açıkken bayat kopyayla
            #     koşmak kapıları sessizce kaybetmektir;
            # (b) AĞ-İMPORT (v0.5.8.4) — kopyaya sızan ağ importu Layer 0'ı
            #     görünmez delmesin;
            # (c) TESLİM-DİSİPLİNİ (v0.5.8.4 — 372 dersi 23/0): mühürsüz
            #     teslim-sınıfı ürün varken defterin açık olması yetmez —
            #     mühür zinciri her turda hatırlatılır.
            parcalar = []
            # A4 (v0.5.9) — ZİNCİR DURUMU her turda İLK sırada akar (kısa,
            # gürültüsüz; durum dosyası yoksa None → mevcut sessizlik korunur).
            zincir = _zincir_durumu_ozeti(k)
            if zincir:
                parcalar.append(zincir)
            bayat = _bayat_arac_uyarisi(k)
            if bayat:
                parcalar.append(bayat)
                # H2a — BAYAT NESİL bulgusu deftere ayrı olay olarak düşer
                # (görünürlük izi; _hook_olay_yaz defter yoksa sessiz no-op).
                nesil = _bayat_nesil_listesi(k)
                if nesil:
                    _hook_olay_yaz(k, "bayat-arac",
                                   "BAYAT NESİL: " + "; ".join(nesil))
            ag = _arac_ag_import_uyarisi(k)
            if ag:
                parcalar.append(ag)
            # v0.5.10 (307-K1) — MÜHÜR-KIRIK ürün uyarısı: kök + 40-UYAP'taki
            # .udf ürünlerden mührü bayat/okunamaz olan varsa her turda kısa
            # uyarı akar (mühürsüz kök dosyaları SAYILMAZ — UYAP kaynak
            # evrakı olabilir; yanlış alarm amaç-çizgisi ihlalidir).
            kirik = _muhur_kirik_urun_listesi(k)
            if kirik:
                parcalar.append(
                    "MÜHÜR-KIRIK ÜRÜN (%d): %s — ürün mühürden sonra "
                    "değişmiş; teslimden önce udf_yaz ile yeniden üret "
                    "(mühür atomik tazelenir; FİLO-TAZELİK kapısı bunu "
                    "RED'ler)." % (len(kirik), "; ".join(kirik[:3])))
            # v0.5.11 — kit güvenlik katmanı (1865): kilit + çok-oturum +
            # sözleşme-dışı dizin + MANİFEST-önce. Hepsi advisory/sessiz-temiz.
            _cekirdek_kilitle(k)
            taze = _taze_oturum_uyarisi(
                (_PAYLOAD_ONBELLEK or {}).get("transcript_path"))
            if taze:
                parcalar.append(taze)
            sd = _sozlesme_disi_uyarisi(k)
            if sd:
                parcalar.append(sd)
            mo = _manifest_once_uyarisi(k)
            if mo:
                parcalar.append(mo)
            # H3a — kanonik olmayan makbuz (txt var / kanonik json yeşil değil).
            kanonik = _kanonik_olmayan_makbuz_uyarisi(k)
            if kanonik:
                parcalar.append(kanonik)
            muhursuz = _muhursuz_teslim_uyarisi(k)
            if muhursuz:
                parcalar.append(
                    "TESLİM-DİSİPLİNİ HATIRLATMASI (v0.5.8.4 — hat açık ama mühürsüz "
                    "teslim ürünü var; 372 dersi: 23 uyarı / 0 uygulama):\n"
                    + muhursuz + "\n"
                    "  Zincir: ürünü resmî hattan üret (udf_yaz.py / npx udf-cli "
                    "html2udf) → `oa-kontrol/scripts/muhur_yaz.py --kok . --urun "
                    "<yol> --girdi <girdi>` → makbuz için `teslim_paketi.py`. "
                    "Bu bir ENGEL DEĞİLDİR; görünürlüktür.")
            if parcalar:
                print(json.dumps({"hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": "\n\n".join(parcalar),
                }}, ensure_ascii=False))
                # Defter olayı yalnız GERÇEK uyarı varken düşer — rutin
                # ZİNCİR DURUMU satırı her turda olay yazsaydı append-only
                # defter turda-bir satırla şişerdi (gürültü disiplini).
                etiketler = [e for e, v in (("bayat", bayat), ("ağ-import", ag),
                                            ("kanonik-makbuz", kanonik),
                                            ("teslim-disiplini", muhursuz)) if v]
                if etiketler:
                    _hook_olay_yaz(k, "prompt", "enjeksiyon: " + "+".join(etiketler))
            return 0
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
            "tereddütte aç.\n"
            "TESLİM DİSİPLİNİ (v0.5.8.1 — pipeline kurulu OLMASA BİLE geçerli; 447 "
            "provası dersi: aile çağrılmadan inline koşulursa bu beşli kaybolur): bu "
            "koşuda bir TESLİM ÜRÜNÜ (dilekçe/mütalaa md-html-pdf-udf) üretilecekse — "
            "(1) her içtihat teyidinde 'bu karar sonradan AŞILMIŞ olabilir mi?' sorusu "
            "sorulur; aşılmışsa kayda **AŞAN-KAYNAK:** işlenir; (2) dilekçedeki her "
            "künyenin YANINA kütükteki KAYNAK-URL erişim linki yazılır (linksiz künye "
            "EKSİK atıftır); (3) karşı tarafın MUHTEMEL savunmalarının analizi "
            "DİLEKÇEYE YAZILMAZ — yalnız `_oa/cikti/07-antitez-cephanelik.md` iç "
            "dosyasına yazılır (m.6: savunma hattı karşı tarafa hediye edilmez); "
            "(4) her ürünün İLK satırlarına KAYNAK-BLOĞU yazılır "
            "(`<!-- kaynaklar: yol@sha8 -->`); (5) üretimden sonra "
            "`oa-kontrol/scripts/muhur_yaz.py --kok . --urun <yol> --girdi <girdi>` ve "
            "`oa-kontrol/scripts/ictihat_muhakeme_denetim.py <taslak.md> --kok .` koşulur."
        )
        # AĞ-İMPORT (v0.5.8.4): defter yokken de `_oa/araclar` kopyası
        # bulunabilir (_oa kökü klasörü dava klasörü sayar) — bulgu varsa
        # devir metnine EKLENİR (ayrı kanal açılmaz, tek enjeksiyon).
        ag = _arac_ag_import_uyarisi(k)
        if ag:
            metin = f"{metin}\n\n{ag}"
        # H3a (v0.5.8.6) — 777'nin ta kendisi: defter HİÇ açılmamışken kökte
        # makbuz-şekilli .txt durabilir (bayat teslim_paketi stdout yönlendirmesi).
        # Kanonik makbuz defter olmadan var OLAMAZ — uyarı devir metnine eklenir.
        kanonik = _kanonik_olmayan_makbuz_uyarisi(k)
        if kanonik:
            metin = f"{metin}\n\n{kanonik}"
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": metin,
        }}, ensure_ascii=False))
        return 0
    except Exception:
        return 0                                          # sessiz başarısızlık — asla bloklamaz


def _udf_icinde_imza_var_mi(yol):
    """B5 — ürün (zip/udf) içinde `sign.sgn` (UYAP e-imza kaydı) var mı?
    Zip değilse/okunamazsa False. ASLA fırlatmaz."""
    try:
        import zipfile
        with zipfile.ZipFile(yol) as zf:
            return any(a.lower().endswith("sign.sgn") for a in zf.namelist())
    except Exception:
        return False


def _muhursuz_teslim_listesi(kok):
    """v0.5.8.4/v0.5.8.5 — TESLİM-SINIFI ürün taraması. Döner: kayıt listesi
    `[{"yol": "cikti/x.udf", "durum": "muhursuz"|"bayat"|"imzali-bilgi",
    "eski_sha": str|None}]` (sıralı, `_oa`ya göreli yol).

    B5 — BAYATLIK: yan `.prov.json`daki `artifact_sha256` ürünün GÜNCEL
    sha'sıyla uyuşmuyorsa kayıt "bayat" işaretiyle girer (mühür var ama eski
    ürünü anlatıyor — kriptografik zincir kopmuş). İSTİSNA: ürün `sign.sgn`
    taşıyorsa (e-imzalı türev) BAYAT SAYILMAZ — mühür tazeleme kararı
    teslim_paketi/muhur_yaz kuralına bırakılır, yalnız "imzali-bilgi" satırı
    üretilir. Uyarı metni (`_muhursuz_teslim_uyarisi`) ve otomatik mühür
    (`_otomatik_muhurle`) AYNI listeden beslenir — iki ayrı tarama mantığı
    sapamaz. ASLA fırlatmaz (hata → boş liste)."""
    kayitlar = []
    try:
        for alt in ("cikti", "teslim"):
            d = os.path.join(kok, "_oa", alt)
            if not os.path.isdir(d):
                continue
            for ad in sorted(os.listdir(d)):
                if not ad.lower().endswith((".udf", ".pdf")):
                    continue
                if ad.startswith(("TEST", "_")):
                    continue                       # prova/gecici urunler haric
                yol = os.path.join(d, ad)
                goreli = f"{alt}/{ad}"
                prov_yolu = yol + ".prov.json"
                if not os.path.isfile(prov_yolu):
                    kayitlar.append({"yol": goreli, "durum": "muhursuz",
                                     "eski_sha": None})
                    continue
                # B5 — BAYATLIK taraması (mühür VAR — hâlâ bu ürünü mü anlatıyor?)
                try:
                    with open(prov_yolu, encoding="utf-8") as f:
                        prov = json.load(f) or {}
                    eski_sha = prov.get("artifact_sha256") if isinstance(prov, dict) else None
                except Exception:
                    eski_sha = None
                if not eski_sha:
                    continue   # sha'sız/okunamayan prov — mühürlü sayılır (mevcut davranış)
                guncel = _sha256_dosya(yol)
                if guncel is None or guncel == eski_sha:
                    continue
                if _udf_icinde_imza_var_mi(yol):
                    kayitlar.append({"yol": goreli, "durum": "imzali-bilgi",
                                     "eski_sha": eski_sha})
                else:
                    kayitlar.append({"yol": goreli, "durum": "bayat",
                                     "eski_sha": eski_sha})
    except Exception:
        pass
    return kayitlar


def _muhursuz_teslim_uyarisi(kok):
    """v0.5.8.1 (447 provası dersi) + v0.5.8.5/B5 — TESLİM-SINIFI ürün
    (cikti/teslim'de .udf/.pdf) mühürsüz VEYA mührü BAYAT ise görünür uyarı
    metni döndürür; yoksa None. Yalnız `imzali-bilgi` kayıtları varsa da None
    (bilgi satırı hook-denetle'de basılır — her turda tekrarlanan gürültü
    olmaz). Model-bağımsız, deterministik; ASLA fırlatmaz."""
    try:
        kayitlar = _muhursuz_teslim_listesi(kok)
        eylemli = [k for k in kayitlar if k.get("durum") in ("muhursuz", "bayat")]
        if not eylemli:
            return None
        satirlar = []
        for k in eylemli[:8]:
            if k["durum"] == "bayat":
                satirlar.append(f"  ✗ {k['yol']} [BAYAT mühür — .prov.json sha "
                                "güncel ürünle uyuşmuyor]")
            else:
                satirlar.append(f"  ✗ {k['yol']}")
        for k in [x for x in kayitlar if x.get("durum") == "imzali-bilgi"][:4]:
            satirlar.append(f"  ℹ {k['yol']} [sign.sgn'li e-imzalı türev — BAYAT "
                            "sayılmadı; teslim_paketi/muhur_yaz kuralına bırakıldı]")
        return ("MÜHÜRSÜZ TESLİM UYARISI (v0.5.8.1 — oa-mühür/P1; B5 bayatlık dahil): "
                "aşağıdaki teslim-sınıfı ürünlerin `.prov.json` doğum belgesi YOK ya da "
                "BAYAT — hangi girdiden üretildikleri kriptografik olarak kanıtlanamaz; "
                "UYAP'a yüklemeden önce `oa-kontrol/scripts/muhur_yaz.py --kok . --urun "
                "<yol>` koşulmalı ve `--dogrula` ile teyit edilmelidir:\n"
                + "\n".join(satirlar))
    except Exception:
        return None


def _makbuz_sekilli_txt_mi(ad):
    """H3a — dosya adı makbuz-şekilli bir .txt mi? (TESLIM-MAKBUZU*.txt VEYA
    *makbuz*.txt sınıfı; büyük/küçük harf duyarsız)."""
    kucuk = str(ad).lower()
    if not kucuk.endswith(".txt"):
        return False
    return kucuk.startswith("teslim-makbuzu") or "makbuz" in kucuk


def _kanonik_olmayan_makbuz_uyarisi(kok):
    """H3a (v0.5.8.6 — 777 saha dersi): bayat `teslim_paketi` stdout'u bir
    `TESLIM-MAKBUZU.txt`ye yönlendirilip "yeşil makbuz" BEYAN edildi — kanonik
    `_oa/defter/teslim-makbuz.json` hiç yoktu. Kökte (veya `_oa`/`_oa/defter`
    altında) makbuz-şekilli .txt VAR ama kanonik makbuz (exit_kodu=0) YOKSA
    görünür uyarı metni döndürür; kanonik makbuz yeşilse (txt yalnız fazlalık)
    None. ASLA fırlatmaz, ASLA bloklamaz."""
    try:
        kok = kok or "."
        adaylar = []
        for dizin, onek in ((kok, ""), (os.path.join(kok, "_oa"), "_oa/"),
                            (os.path.join(kok, "_oa", "defter"), "_oa/defter/")):
            if not os.path.isdir(dizin):
                continue
            try:
                for girdi in os.scandir(dizin):
                    if girdi.is_file() and _makbuz_sekilli_txt_mi(girdi.name):
                        adaylar.append(onek + girdi.name)
            except OSError:
                continue
        if not adaylar:
            return None
        m, _hata = _makbuz_oku(kok)
        if m is not None and m.get("exit_kodu") == 0:
            return None                # kanonik makbuz yeşil — txt zararsız fazlalık
        return ("⚠ KANONİK OLMAYAN MAKBUZ — makbuz-şekilli dosya var ("
                + ", ".join(sorted(adaylar)[:6])
                + (" … (+%d)" % (len(adaylar) - 6) if len(adaylar) > 6 else "")
                + ") ama kanonik `_oa/defter/teslim-makbuz.json` (exit_kodu=0) YOK — "
                "teslim beyanına dayanak OLAMAZ (tek ölçüt: defter/teslim-makbuz.json "
                "exit 0). Stdout'u bir .txt'ye yönlendirmek makbuz DEĞİLDİR (777 saha "
                "bulgusu); makbuz yalnız `teslim_paketi.py` zincirinin SONUNDA doğar.")
    except Exception:
        return None


def _istisna_kaydi_yaz(kok, tur, ilgili, gerekce, onay="otomatik-kural"):
    """İSTİSNA DEFTERİ (ortak şema, append-only — birden çok araç yazar):
    `_oa/defter/istisna-kayitlari.jsonl` satırı = {"zaman": ISO, "tur": ...,
    "ilgili": ..., "gerekce": ..., "onay": "avukat"|"otomatik-kural",
    "imza": araç-imzası}. Aynı (tur, ilgili) çifti zaten kayıtlıysa TEKRAR
    yazılmaz (her hook koşusunda defter şişmesin — append-only bozulmaz,
    yalnız mükerrer önlenir). ASLA fırlatmaz, ASLA bloklamaz."""
    try:
        defter = os.path.join(kok, "_oa", "defter")
        if not os.path.isdir(defter):
            return
        yol = os.path.join(defter, "istisna-kayitlari.jsonl")
        if os.path.isfile(yol):
            with open(yol, encoding="utf-8") as f:
                for satir in f:
                    try:
                        k = json.loads(satir)
                    except Exception:
                        continue
                    if k.get("tur") == tur and k.get("ilgili") == ilgili:
                        return
        kayit = {"zaman": simdi(), "tur": tur, "ilgili": str(ilgili),
                 "gerekce": gerekce, "onay": onay}
        ham = "|".join([kayit["zaman"], tur, str(ilgili), str(gerekce), OA_SURUM])
        kayit["imza"] = hashlib.sha256(
            ham.encode("utf-8", errors="replace")).hexdigest()[:16]
        with open(yol, "a", encoding="utf-8") as f:
            f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _otomatik_muhurle(kok, kayitlar):
    """v0.5.8.4 — OTOMATİK MÜHÜR (372 kanıtı: Stop hook 23 kez MÜHÜRSÜZ
    uyardı, model 0 kez uyguladı — uyarı işlemiyor, otomasyon gerek).
    Her mühürsüz/bayat teslim-sınıfı kayıt (`_muhursuz_teslim_listesi`
    çıktısı) için `oa-kontrol/scripts/muhur_yaz.py` İN-PROCESS (importlib)
    çağrılır — subprocess YASAK: P0-4 Gate G dairesel bağımlılık kırıcısı bu
    modülden subprocess sınıfını kökten kaldırmıştır ve test_gate_g_dongu
    bunu kilitler. PROV DÜRÜSTLÜĞÜ: sonradan (post-hoc) basılan mühür üretim
    yolunu İDDİA EDEMEZ — was_generated_by bunu açıkça beyan eder.
    B5 — BAYAT üründe mühür `was_derived_from=eski-sha` ile TAZELENİR (zincir
    kopmaz, eski sha görünür kalır); `imzali-bilgi` kayıtlarına DOKUNULMAZ.
    Döner: fiilen mühürlenen ürün sayısı. Hata olursa o ürün atlanır (uyarı
    davranışına geri düşülür); ASLA fırlatmaz, ASLA bloklamaz."""
    sayi = 0
    try:
        import importlib.util
        skills_kok = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        muhur = os.path.join(skills_kok, "oa-kontrol", "scripts", "muhur_yaz.py")
        if not os.path.isfile(muhur):
            return 0
        spec = importlib.util.spec_from_file_location("_oa_muhur_hook", muhur)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for k in kayitlar:
            try:
                if k.get("durum") == "imzali-bilgi":
                    continue           # e-imzalı türev — otomatik tazeleme YASAK
                u = k["yol"]
                yol = os.path.join(kok, "_oa", *u.split("/"))
                if not os.path.isfile(yol):
                    continue
                kayit = mod.muhur_uret(
                    kok, yol, tip="teslim_urunu",
                    kimlik="hook-otomatik:" + u, girdiler=[],
                    onceki=k.get("eski_sha"),
                    arac="hook-otomatik (post-hoc); üretim yolu beyan edilmedi",
                    llm="beyan edilmedi (hook-otomatik post-hoc mühür)")
                mod.muhur_yaz(kok, yol, kayit)
                if os.path.isfile(yol + ".prov.json"):
                    sayi += 1
            except Exception:
                continue
    except Exception:
        return sayi
    return sayi


# ── B3 (v0.5.8.5) — ZİNCİR-DIŞI GÖRÜNÜRLÜK: mühürsüz/makbuzsuz UDF'de
# udf_yaz.udf_dogrula İN-PROCESS advisory. subprocess YASAK (P0-4 Gate G
# dairesel bağımlılık kırıcısı bu modülden subprocess sınıfını kaldırmıştır;
# test_gate_g_dongu kaynak taramasıyla kilitler) — bu yüzden importlib +
# `resmi_okuyucu=False` (npx/ağ bacağı hook'ta koşmaz; o bacak udf_yaz.py'nin
# kendi CLI'sinin işidir). pageFormat 4x42.52 (No. 2646 m.8) kontrolü de
# burada yapılır. Sonuç uyarıya + deftere {tip:"hook", olay:"denetle-udf"}
# olarak yazılır. Advisory — ASLA bloklamaz.
_UDF_YAZ_MOD = None


def _udf_yaz_modulu():
    """udf_yaz.py'yi (kardeş skill `oa-dilekce/scripts/`) İN-PROCESS import
    eder (subprocess YOK). Bulunamaz/çökerse None."""
    global _UDF_YAZ_MOD
    if _UDF_YAZ_MOD is not None:
        return _UDF_YAZ_MOD
    skills_kok = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    betik = os.path.join(skills_kok, "oa-dilekce", "scripts", "udf_yaz.py")
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_oa_pipeline_udf_inproc", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _UDF_YAZ_MOD = mod
    return _UDF_YAZ_MOD


def _udf_kenar_kontrol(yol, kenar_pt=None):
    """B3 — üretilmiş UDF'in pageFormat dört kenarı 42.52 pt mi (Resmî
    Yazışma Yönetmeliği No. 2646 m.8 — 1,5 cm)? Temizse None, aksi hâlde
    kısa bulgu metni döner. Eşik tek kaynaktan (udf_yaz._KENAR_PT) okunur;
    modül yoksa "42.52" sabitine düşer. ASLA fırlatmaz."""
    try:
        if kenar_pt is None:
            mod = _udf_yaz_modulu()
            kenar_pt = getattr(mod, "_KENAR_PT", "42.52") if mod else "42.52"
        import zipfile
        with zipfile.ZipFile(yol) as zf:
            ad = next((a for a in zf.namelist() if a.endswith("content.xml")), None)
            if ad is None:
                return "content.xml yok"
            metin = zf.read(ad).decode("utf-8", errors="replace")
        m = re.search(r"<pageFormat\b[^>]*>", metin)
        if not m:
            return "pageFormat yok"
        etiket = m.group(0)
        eksik = [k for k in ("leftMargin", "rightMargin", "topMargin", "bottomMargin")
                 if '%s="%s"' % (k, kenar_pt) not in etiket]
        if eksik:
            return "kenarlar 4x%s pt DEĞİL (%s — No. 2646 m.8)" % (kenar_pt, ", ".join(eksik))
        return None
    except Exception as e:
        return f"kenar kontrolü yapılamadı ({e})"


def _hook_udf_dogrula_advisory(kok, goreli_udfler, azami=3):
    """B3 — verilen (mühürsüz/bayat/makbuzsuz) UDF'ler için udf_dogrula
    (in-process, resmi_okuyucu=False) + pageFormat 4x42.52 kontrolü koşar;
    bulgu satırlarının listesini döndürür (boş olabilir). ASLA fırlatmaz."""
    satirlar = []
    try:
        mod = _udf_yaz_modulu()
        for u in list(goreli_udfler)[:azami]:
            yol = os.path.join(kok, "_oa", *str(u).split("/"))
            if not os.path.isfile(yol):
                continue
            parca = []
            if mod is not None and hasattr(mod, "udf_dogrula"):
                try:
                    sonuc = mod.udf_dogrula(yol, resmi_okuyucu=False)
                    if sonuc.get("gecerli"):
                        parca.append("yapı: GEÇERLİ")
                    else:
                        hatalar = "; ".join(sonuc.get("hatalar") or [])[:200] or "?"
                        parca.append(f"yapı: GEÇERSİZ ({hatalar})")
                except Exception as e:
                    parca.append(f"yapı: doğrulanamadı ({e})")
            else:
                parca.append("yapı: udf_yaz.py bulunamadı — doğrulama atlandı")
            kenar = _udf_kenar_kontrol(yol)
            parca.append("kenar: 4x42.52 pt OK" if kenar is None else f"kenar: {kenar}")
            satirlar.append(f"  {u}: " + " · ".join(parca))
    except Exception:
        pass
    return satirlar


def hook_denetle(kok=None):
    """P0-7 — Stop/SessionEnd hook komutu. Döner: her zaman 0 (ASLA
    bloklamaz)."""
    try:
        kokler = _hook_kok_adaylarini_bul(kok)
    except Exception:
        kokler = [os.path.abspath(kok or ".")]
    for kok_aday in kokler:
        # T12 — ÇİFT-KANAL DEDUP (ayirt=durum parmak izi): aynı saniyede,
        # arada HİÇBİR dosya değişmeden gelen ikinci `denetle` koşusu (çift
        # kanal kaydı) bu kök için yan-etkisiz atlanır — çıktı yok, defter
        # olayı yok, otomatik mühür yok. Arada _oa/cikti'ya dilekçe/UDF
        # yazıldıysa iz değişir → denetim AYNEN koşar (durum-körü dedup
        # Paket-B atlatma-tespitini öldürmesin).
        if _hook_dedup_kisa_devre(kok_aday, "denetle",
                                  ayirt=_hook_denetle_ayirt(kok_aday)):
            continue
        # C3 — HOOK NABZI: kapanış-sınıfı koşu kendi damgasını basar. Ölü-
        # prompt uyarısının BASIMI `_hook_govde_calistir` içindedir — parmak
        # izine (`_hook_cikti_degisti_mi`) girer ki mevcut gürültü disiplini
        # (defter değişmeden ikinci koşu SESSİZ kısa devre) bozulmasın.
        _hook_nabiz_damgala(kok_aday, "denetle", oturum=_payload_oturum())
        # A4.8b — RED GİZLENEMEZ: makbuz RED dosyası varken bu satır zorunlu.
        try:
            red_yolu = os.path.join(kok_aday, "_oa", "defter", "teslim-makbuz-RED.json")
            if os.path.isfile(red_yolu):
                print("⚠ TESLİM MAKBUZU: RED (sebep-kapısı) — _oa/defter/"
                      "teslim-makbuz-RED.json duruyor: son teslim denemesi "
                      "REDDEDİLMİŞ. Sebep giderilmeden teslim edilemez; "
                      "teslim_paketi.py'yi yeniden koş.")
        except Exception:
            pass
        # ATLANMIŞ HAT NÖBETÇİSİ — defter denetiminden ÖNCE. `_hook_govde_calistir`
        # defter yoksa sessizce döner; oysa "defter YOK + ürün VAR" hâli tam da
        # görünmesi gereken hâldir (bkz. `_hat_atlandi_uyarisi` notu).
        atlandi = _hat_atlandi_uyarisi(kok_aday)
        if atlandi:
            print("═" * 66)
            print(atlandi)
            print("═" * 66)
        bayat = _bayat_arac_uyarisi(kok_aday)
        if bayat:
            print("═" * 66)
            print(bayat)
            print("═" * 66)
            # H2a — BAYAT NESİL bulgusu deftere ayrı olay olarak düşer.
            nesil = _bayat_nesil_listesi(kok_aday)
            if nesil:
                _hook_olay_yaz(kok_aday, "bayat-arac",
                               "BAYAT NESİL: " + "; ".join(nesil))
        # H2b — VERSION damgası (damgasız/bayat araç çantası).
        surum_damga = _arac_version_uyarisi(kok_aday)
        if surum_damga:
            print("═" * 66)
            print(surum_damga)
            print("═" * 66)
        ag = _arac_ag_import_uyarisi(kok_aday)
        if ag:
            print("═" * 66)
            print(ag)
            print("═" * 66)
        # H3a — kanonik olmayan makbuz (txt var / kanonik json yeşil değil).
        kanonik = _kanonik_olmayan_makbuz_uyarisi(kok_aday)
        if kanonik:
            print("═" * 66)
            print(kanonik)
            print("═" * 66)
        muhursuz_kayitlar = _muhursuz_teslim_listesi(kok_aday)
        eylemli = [k for k in muhursuz_kayitlar
                   if k.get("durum") in ("muhursuz", "bayat")]
        bilgi = [k for k in muhursuz_kayitlar if k.get("durum") == "imzali-bilgi"]
        muhur_sayi = 0
        if eylemli:
            muhursuz = _muhursuz_teslim_uyarisi(kok_aday)
            if muhursuz:
                print("═" * 66)
                print(muhursuz)
                print("═" * 66)
            # B3 — ZİNCİR-DIŞI GÖRÜNÜRLÜK: mühürsüz/bayat UDF'lerde yapı +
            # kenar advisory'si (in-process; otomatik mühürden ÖNCE koşar ki
            # bulgu, mühürlense bile görünür kalsın).
            udf_adaylari = [k["yol"] for k in eylemli
                            if k["yol"].lower().endswith(".udf")]
            advisory = _hook_udf_dogrula_advisory(kok_aday, udf_adaylari)
            if advisory:
                print("═" * 66)
                print("UDF DOĞRULAMA (advisory — udf_yaz.udf_dogrula in-process, "
                      "resmî okuyucu bacağı hariç):")
                for satir in advisory:
                    print(satir)
                print("═" * 66)
                _hook_olay_yaz(kok_aday, "denetle-udf",
                               "advisory: " + "; ".join(udf_adaylari[:3]))
            # v0.5.8.4 — uyarıyla KALMA: mührü kendin bas (23/0 dersi);
            # B5 — bayat ürünler was_derived_from=eski-sha ile TAZELENİR.
            muhur_sayi = _otomatik_muhurle(kok_aday, eylemli)
            if muhur_sayi:
                print(f"OTOMATİK MÜHÜR: {muhur_sayi} ürün — post-hoc `.prov.json` "
                      "basıldı (üretim yolu beyan edilmedi; `--dogrula` ile teyit et).")
        elif bilgi:
            # B5 — yalnız e-imzalı türev(ler): bilgi satırı basılır, mühür
            # OTOMATİK tazelenmez (teslim_paketi/muhur_yaz kuralına bırakılır).
            for k in bilgi[:4]:
                print(f"ℹ {k['yol']}: sign.sgn'li e-imzalı türev — mühür sha'sı "
                      "güncel değil ama BAYAT sayılmadı (otomatik tazeleme yok; "
                      "teslim_paketi/muhur_yaz kuralına bırakıldı).")
        # B5 — sign.sgn toleransı istisna defterine işlenir (ortak şema;
        # mükerrer yazılmaz — bkz. `_istisna_kaydi_yaz`).
        for k in bilgi:
            _istisna_kaydi_yaz(
                kok_aday, "dogrulama-toleransi", k["yol"],
                "sign.sgn'li e-imzalı türev BAYAT sayılmadı — mühür tazeleme "
                "teslim_paketi/muhur_yaz kuralına bırakıldı (B5).")
        if bayat or surum_damga or ag or kanonik or eylemli or bilgi:
            _hook_olay_yaz(kok_aday, "denetle",
                           "uyarı: " + "+".join(
                               e for e, v in (("bayat", bayat),
                                              ("sürüm-damga", surum_damga),
                                              ("ağ-import", ag),
                                              ("kanonik-makbuz", kanonik),
                                              ("mühürsüz", eylemli),
                                              ("imzalı-bilgi", bilgi)) if v)
                           + (f"; otomatik mühür {muhur_sayi}" if muhur_sayi else ""))
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


# ── A2 (v0.5.9) — İNLİNE ZİNCİR (PostToolUse → dilekce_denetim hızlı kip) ──
# 777 kanıtı: PostToolUse çıktısı modele GERİ AKAR (model [M] uyarısına renum
# scriptiyle cevap verdi). Taslak yazımının HEMEN ardından koşan hızlı bir
# denetim, bulguyu bir SONRAKİ turda modelin bağlamına taşır (KESİNTİSİZ:
# zincirdeki yer + önceki halka ürünleri akar; TAMAMLAYICI: script denetler,
# muhakemeyi üretmez/zorlamaz). dilekce_denetim.py İN-PROCESS import edilir
# (subprocess YASAK — test_gate_g_dongu kilidi); `hizli_denetim` fonksiyonu
# yoksa SESSİZ atlanır (eski sürüm uyumu). Çağrı 2sn'yi aşarsa VAZGEÇİLİR
# (timeout koruması — hook ASLA bloklamaz).
INLINE_DENETIM_ZAMAN_SINIRI_SN = 2.0
_DILEKCE_DENETIM_MOD = None


def _dilekce_denetim_modulu():
    """dilekce_denetim.py'yi (kardeş skill `oa-dilekce/scripts/`) İN-PROCESS
    import eder (_udf_yaz_modulu ile AYNI desen — subprocess YOK).
    Bulunamaz/çökerse None."""
    global _DILEKCE_DENETIM_MOD
    if _DILEKCE_DENETIM_MOD is not None:
        return _DILEKCE_DENETIM_MOD
    skills_kok = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    betik = os.path.join(skills_kok, "oa-dilekce", "scripts", "dilekce_denetim.py")
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "_oa_pipeline_dilekce_denetim_inproc", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _DILEKCE_DENETIM_MOD = mod
    return _DILEKCE_DENETIM_MOD


def _dilekce_taslak_sinifi_mi(kok, yol):
    """Yazılan dosya DİLEKÇE-TASLAK sınıfı mı? Ad deseni (*dilekce*/
    *dilekçe*/*taslak*) + `.md` uzantısı + `_oa/cikti` altında olma — üçü
    birden. ASLA fırlatmaz."""
    try:
        ad = os.path.basename(str(yol)).lower()
        if not ad.endswith(".md"):
            return False
        if not ("dilekce" in ad or "dilekçe" in ad or "taslak" in ad):
            return False
        tam = str(yol)
        if not os.path.isabs(tam):
            tam = os.path.join(kok, tam)
        tam = os.path.abspath(tam)
        cikti = os.path.abspath(os.path.join(kok, "_oa", "cikti"))
        return tam.startswith(cikti + os.sep)
    except Exception:
        return False


def _inline_bulgu_listesi(sonuc):
    """`hizli_denetim` dönüşünü SAVUNMACI normalize eder — kardeş ajan
    sözleşmesi list[str]'dir; dict({'bulgular': [...]}) ve tekil değer de
    tolere edilir (paralel geliştirme toleransı)."""
    if sonuc is None:
        return []
    if isinstance(sonuc, dict):
        sonuc = sonuc.get("bulgular") or []
    if isinstance(sonuc, (list, tuple)):
        return [str(b) for b in sonuc if str(b).strip()]
    return [str(sonuc)] if str(sonuc).strip() else []


def _hook_inline_dilekce_denetim(kok, veri, zaman_siniri_sn=None):
    """A2 gövdesi: payload'daki YENİ yazılan dosya dilekçe-taslak sınıfıysa
    `hizli_denetim(metin, kok)`'u İN-PROCESS + zaman sınırlı koşar; bulgu
    özetini (başlık + en çok 5 bulgu satırı = toplam ≤6 satır) stdout'a
    basar — PostToolUse çıktısı modele geri akar. Bulgu yoksa TEK satır
    'inline denetim: temiz' (sessiz-yeşil ölçümü için). Defter varsa
    {tip:hook, olay:inline-denetim, not:'N bulgu'} olayı düşer.
    `hizli_denetim` yoksa/çökerse/zaman aşarsa SESSİZ vazgeçer —
    ASLA fırlatmaz, ASLA bloklamaz."""
    try:
        if zaman_siniri_sn is None:
            zaman_siniri_sn = INLINE_DENETIM_ZAMAN_SINIRI_SN
        if not isinstance(veri, dict):
            return
        dosya = None
        ti = veri.get("tool_input")
        if isinstance(ti, dict):
            dosya = ti.get("file_path")
        if not dosya:
            tr = veri.get("tool_response")
            if isinstance(tr, dict):
                dosya = tr.get("filePath")
        if not dosya or not _dilekce_taslak_sinifi_mi(kok, dosya):
            return
        tam = str(dosya)
        if not os.path.isabs(tam):
            tam = os.path.join(kok, tam)
        mod = _dilekce_denetim_modulu()
        if mod is None:
            return
        fn = getattr(mod, "hizli_denetim", None)
        if not callable(fn):
            return                          # eski sürüm uyumu — sessiz atla
        try:
            with open(tam, encoding="utf-8", errors="replace") as f:
                metin = f.read()
        except OSError:
            return
        import threading                    # yerel import — ağ/alt-süreç değil
        kutu = {}

        def _calistir():
            try:
                kutu["sonuc"] = fn(metin, kok)
            except Exception:
                kutu["hata"] = True

        is_ipligi = threading.Thread(target=_calistir, daemon=True)
        is_ipligi.start()
        is_ipligi.join(zaman_siniri_sn)
        if is_ipligi.is_alive() or kutu.get("hata") or "sonuc" not in kutu:
            return                          # zaman aşımı/çökme — vazgeç
        bulgular = _inline_bulgu_listesi(kutu["sonuc"])
        if not bulgular:
            print("inline denetim: temiz")
            _hook_olay_yaz(kok, "inline-denetim", "0 bulgu")
            return
        print(f"İNLİNE DENETİM ({os.path.basename(str(dosya))} — "
              f"dilekce_denetim.hizli_denetim): {len(bulgular)} bulgu")
        for b in bulgular[:5]:
            print("  " + b[:200])
        _hook_olay_yaz(kok, "inline-denetim", f"{len(bulgular)} bulgu")
    except Exception:
        pass                                # sessiz başarısızlık — asla bloklamaz


def hook_postwrite(kok=None):
    """GÖREV B / P0-B (v0.5.5) — PostToolUse(Write|Edit) hook komutu. Bu
    kökte (veya keşfedilen aday köklerden herhangi birinde)
    `_hook_postwrite_tetikle_mi` True DÖNMEDİKÇE hiçbir ağır iş yapmaz
    (hızlı erken çıkış). Döner: her zaman 0 (ASLA bloklamaz).

    A2 (v0.5.9) — İNLİNE ZİNCİR: payload BİR KEZ okunur (C2 kök-simetrisi ile
    aynı ilke) ve hem kök keşfine hem `_hook_inline_dilekce_denetim`e AYNI
    nesne verilir; yazılan dosya dilekçe-taslak sınıfıysa hızlı denetim
    bulguları PostToolUse çıktısıyla modele GERİ AKAR."""
    veri = _hook_stdin_payload_oku()        # TTY'de/boşta/bozukta None — asla bekleme
    try:
        kokler = _hook_kok_adaylarini_bul(kok, payload=veri)
    except Exception:
        kokler = [os.path.abspath(kok or ".")]
    for kok_aday in kokler:
        # T12 — ÇİFT-KANAL DEDUP (ayirt=payload parmak izi): aynı saniyede
        # BİT-BİT AYNI payload'la ikinci koşu (çift kanal kopyası) atlanır;
        # farklı payload'lı meşru ardışık Write/Edit'ler ETKİLENMEZ.
        if _hook_dedup_kisa_devre(kok_aday, "postwrite",
                                  ayirt=_hook_payload_ayirt(veri)):
            continue
        _hook_nabiz_damgala(kok_aday, "postwrite",
                            oturum=(veri or {}).get("session_id"))   # C3 + T4a
        _hook_inline_dilekce_denetim(kok_aday, veri)  # A2 — asla fırlatmaz/bloklamaz
        try:
            tetik = _hook_postwrite_tetikle_mi(kok_aday)
        except Exception as e:
            _hook_basarisizlik_isaretle(kok_aday, f"--hook-postwrite ön-denetimi çöktü: {e}")
            continue
        if not tetik:
            continue
        _hook_govde_calistir(kok_aday, "PostToolUse")
    return 0


# ── PreToolUse ELLE-UDF KAPISI (v0.5.8.4 — 372 dersi 10-D) ─────────────────
# SAHA ÖLÇÜMÜ (372 Torbalı, A/B testli): elle kurulan content.xml'li UDF'ler
# UYAP editöründe AÇILMIYOR; html2udf ürünleri açılıyor. A/B, python re-zip'i
# ve pageFormat kenar yamasını AKLADI — fark yalnız content.xml içeriği
# (yerel motor `<elements resolver="hvl-default">` yazıyor ama styles
# bloğunda o adda STİL TANIMI yok). Bu kapı elle-zip girişimini "ask"
# kararıyla AVUKATA görünür kılar — BLOKLAMAZ (permissionDecision=ask;
# devam etmek avukatın kararıdır). Diğer TÜM hâllerde (dava-dışı klasör,
# desensiz girdi, bozuk stdin, her istisna) ÇIKTI YOK + exit 0.

def _pretool_elle_udf_deseni_mi(metin):
    """Elle-UDF kurulum deseni: ('zipfile' VE 'content.xml') VEYA
    ('ZipFile(' VE '.udf'). Ucuz alt-dizi denetimi — regex gerekmez."""
    return (("zipfile" in metin and "content.xml" in metin)
            or ("ZipFile(" in metin and ".udf" in metin))


# ── A1 (v0.5.9) — SUNUM KİLİDİ (PreToolUse → SendUserFile) ─────────────────
# v0.5.9 çekirdeği: "çıktı tüm süreçten FİZİKSEL geçmeden avukata SUNULMAZ".
# Model SendUserFile ile teslim-sınıfı bir ürünü (.udf/.pdf/.docx) avukata
# gönderirken yeşil makbuz (_oa/defter/teslim-makbuz.json, exit_kodu==0 —
# TEK ÖLÇÜT) yoksa karar 'ask' ile AVUKATA devredilir — BLOKLANMAZ (dört
# ilke: sürtünmesiz — sessiz ret yok, gerekçe ne-yapmalıyı söyler). Yeşil
# makbuz varsa kapı SESSİZDİR (çıktı yok, exit 0). Elle-UDF deseni ile AYNI
# gövdede yaşar; öncelik elle-UDF desenindedir (mevcut davranış AYNEN).

_SUNUM_TESLIM_UZANTILAR = (".udf", ".pdf", ".docx")
# Kök teslim ürünü deseni: dava KÖKÜNDE duran, adından teslim ürünü olduğu
# belli dosyalar (dilekçe/taslak/teslim/mütalaa/istinaf/temyiz/cevap/itiraz).
_SUNUM_KOK_URUN_RE = re.compile(
    r"dilek[cç]e|taslak|teslim|m[uü]talaa|istinaf|temyiz|cevap|itiraz", re.I)


def _sunum_teslim_sinifi_mi(kok, yol):
    """Gönderilen dosya TESLİM-SINIFI ürün mü? (a) uzantı .udf/.pdf/.docx VE
    (b) `_oa` altında (orada her teslim uzantısı üründür) VEYA dava kökünde
    teslim-ürünü adlı (`_SUNUM_KOK_URUN_RE`). UYAP indirme evrakı
    (^NNN_/^YYYY_ önekli orijinal) ürün DEĞİLDİR — orijinal evrak göndermek
    kilide takılmaz (yanlış-pozitif disiplini). ASLA fırlatmaz."""
    try:
        ad = os.path.basename(str(yol))
        if not ad.lower().endswith(_SUNUM_TESLIM_UZANTILAR):
            return False
        if re.match(r"^\d{3,4}[_-]", ad):
            return False                    # UYAP indirmesi — orijinal evrak
        tam = str(yol)
        if not os.path.isabs(tam):
            tam = os.path.join(kok, tam)
        tam = os.path.abspath(tam)
        oa = os.path.abspath(os.path.join(kok, "_oa"))
        if tam.startswith(oa + os.sep):
            return True
        if (os.path.dirname(tam) == os.path.abspath(kok)
                and _SUNUM_KOK_URUN_RE.search(ad)):
            return True
        return False
    except Exception:
        return False


def _sunum_adi_teslim_sinifi_mi(yol):
    """B-4 (v0.5.14) — KÖKSÜZ ad denetimi: dava kökü HİÇ bulunamadığında bile
    gönderilen dosyanın teslim-sınıfı görünüp görünmediğini söyler
    (uzantı + teslim-ürünü adı VEYA yolunda `_oa` segmenti). Kök gerektiren
    `_sunum_teslim_sinifi_mi`nin ikamesi DEĞİLDİR; yalnız 'denetim
    YAPILAMADI' uyarısının yanlış-pozitif eşiğidir. ASLA fırlatmaz."""
    try:
        ad = os.path.basename(str(yol))
        if not ad.lower().endswith(_SUNUM_TESLIM_UZANTILAR):
            return False
        if re.match(r"^\d{3,4}[_-]", ad):
            return False                    # UYAP indirmesi — orijinal evrak
        parcalar = [p.lower() for p in re.split(r"[/\\]", str(yol))]
        if "_oa" in parcalar:
            return True
        return bool(_SUNUM_KOK_URUN_RE.search(ad))
    except Exception:
        return False


def _muhur_kirik_urun_listesi(kok):
    """v0.5.10 — kök (maxdepth 1) + 40-UYAP altındaki .udf'lerden mührü
    KIRIK olanların köke-göreli listesi. Mühürsüz KÖK dosyaları listeye
    GİRMEZ (UYAP kaynak evrakı olabilir); 40-UYAP'ta mühürsüz dahil her
    kırık girer (o dizin yalnız bizimdir). Asla fırlatmaz."""
    kirik = []
    try:
        dizinler = [(kok, False), (os.path.join(kok, "40-UYAP"), True),
                    (os.path.join(kok, "40-uyap"), True)]
        for dizin, bizim in dizinler:
            try:
                girdiler = sorted(os.scandir(dizin), key=lambda g: g.name.lower())
            except OSError:
                continue
            for g in girdiler:
                try:
                    if not g.is_file() or not g.name.lower().endswith(".udf"):
                        continue
                    provlu = os.path.isfile(g.path + ".prov.json")
                    if not provlu and not bizim:
                        continue          # kökte mühürsüz → kaynak evrak olabilir
                    if _muhur_kirik_mi(g.path):
                        try:
                            kirik.append(os.path.relpath(g.path, kok))
                        except ValueError:
                            kirik.append(g.name)
                except OSError:
                    continue
    except Exception:
        pass
    return kirik


def _muhur_kirik_mi(yol, muhursuz_sayilir=True):
    """v0.5.10 (307-K1 penceresi): teslim-sınıfı .udf ürünün mührü kırık mı?
    - .udf değilse → False (bu sensör yalnız UDF ürünlere bakar).
    - .prov.json yoksa → `muhursuz_sayilir` (varsayılan True: mühürsüz ürün
      kırık sayılır — üretim/mühür atomiktir). SUNUM KİLİDİ'nin yeşil-makbuz
      dalı False ile çağırır: yeşil makbuz filo kapısından geçmiştir, kökteki
      mühürsüz .udf kaynak evrak olabilir; orada yalnız GERÇEK bayatlık
      (mühür VAR + sha uyuşmaz — 307'nin birebir durumu) 'ask' doğurur.
    - mühürdeki artifact_sha256 güncel sha ile uyuşmuyorsa → True; TEK
      istisna imzalı nüsha (zip'te sign.sgn): e-imza baytları değiştirir,
      uyuşmazlık TÜREV'dir (B5b) → False.
    Okuma hatası → True (fail-closed; 'ask' engel değil, karar devridir)."""
    try:
        if not str(yol).lower().endswith(".udf") or not os.path.isfile(yol):
            return False
        prov_yolu = str(yol) + ".prov.json"
        if not os.path.isfile(prov_yolu):
            return bool(muhursuz_sayilir)
        with open(prov_yolu, encoding="utf-8") as f:
            muhur = json.load(f)
        h = hashlib.sha256()
        with open(yol, "rb") as f:
            for parca in iter(lambda: f.read(1 << 20), b""):
                h.update(parca)
        if muhur.get("artifact_sha256") == h.hexdigest():
            return False
        try:
            import zipfile as _zf
            with _zf.ZipFile(yol) as z:
                if any(ad.lower().endswith("sign.sgn") for ad in z.namelist()):
                    return False            # imzalı türev — B5b toleransı
        except Exception:
            pass
        return True
    except Exception:
        return True


def _sunum_kilidi_gerekli_mi(veri, kok):
    """A1 karar çekirdeği: payload SendUserFile mi + gönderilenler arasında
    teslim-sınıfı ürün var mı + yeşil makbuz YOK mu? Üçü de evetse True
    ('ask' basılır). Yeşil makbuz (exit_kodu==0) varsa False — kapı sessiz
    (deterministik: halka makbuz ARTEFAKTINA bağlanır, beyana değil).
    v0.5.10 (307-K1): yeşil makbuz VARKEN bile gönderilen teslim-sınıfı
    ürünün MÜHRÜ KIRIKSA (makbuz-sonrası değişiklik penceresi) kilit yine
    devreye girer — 307'de ürün makbuzdan 68 dk sonra mühür dışında değişti
    ve hiçbir katman ateşlemedi; bu koşul o pencereyi kapatır.
    ASLA fırlatmaz."""
    try:
        if not isinstance(veri, dict) or veri.get("tool_name") != "SendUserFile":
            return False
        ti = veri.get("tool_input")
        if not isinstance(ti, dict):
            return False
        dosyalar = ti.get("files")
        if isinstance(dosyalar, str):
            dosyalar = [dosyalar]
        if not isinstance(dosyalar, (list, tuple)):
            return False
        teslim_sinifi = [f for f in dosyalar if _sunum_teslim_sinifi_mi(kok, f)]
        if not teslim_sinifi:
            return False
        m, _hata = _makbuz_oku(kok)
        if m is not None and m.get("exit_kodu") == 0:
            # yeşil makbuz VAR — ama gönderilen üründe GERÇEK bayatlık
            # (mühür var + sha uyuşmaz + imzasız = makbuz-sonrası değişiklik,
            # 307-K1) varsa kilit yine gerekir. Mühürsüz dosya bu dalda
            # SESSİZDİR (kaynak evrak olabilir; filo kapısı zaten geçti).
            return any(_muhur_kirik_mi(f, muhursuz_sayilir=False)
                       for f in teslim_sinifi)
        return True
    except Exception:
        return False


def hook_pretool(kok=None):
    """PreToolUse(Write|Edit|Bash|PowerShell|SendUserFile) hook komutu —
    stdin'deki payload'ın tool_input metnini (content + new_string + command)
    tarar; A1 (v0.5.9) SendUserFile payload'larında SUNUM KİLİDİ'ni denetler.
    YALNIZ dava klasöründe ve kural ateşlerse 'ask' kararı basar; her durumda
    exit 0 (ASLA bloklamaz — 'ask' bir karar devri, engel değildir).
    Kural önceliği: (1) elle-UDF deseni (v0.5.8.4 — AYNEN), (2) SUNUM KİLİDİ.

    C2 (v0.5.8.5) — KÖK SİMETRİSİ: payload BİR KEZ okunur
    (`_hook_stdin_payload_oku`) ve hem içerik taramasına hem kök keşfine
    (`_hook_kok_adaylarini_bul(payload=...)`) AYNI nesne verilir — stdin
    ikinci kez OKUNMAZ (tek kullanımlık akış; hook_prompt ile çakışma
    yapısal olarak imkânsız: her hook kendi sürecinde koşar, bu kural aynı
    süreç İÇİNDE çift okumayı yasaklar)."""
    try:
        veri = _hook_stdin_payload_oku()   # TTY'de/boşta/bozukta None — asla bekleme
        if veri is None:
            return 0
        ti = veri.get("tool_input")
        if not isinstance(ti, dict):
            return 0
        metin = "\n".join(str(ti.get(a) or "")
                          for a in ("content", "new_string", "command"))
        # Kök çözümü: hook_denetle/hook_postwrite ile SİMETRİK keşif (açık
        # --kok > payload cwd/file_path > CLAUDE_PROJECT_DIR > süreç CWD'si).
        # Kapı yalnız DAVA klasöründe nöbet tutar — kod deposunda zipfile
        # meşru iştir.
        try:
            kokler = _hook_kok_adaylarini_bul(kok, payload=veri)
        except Exception:
            kokler = [os.path.abspath(kok or ".")]
        k = next((aday for aday in kokler if _dosya_klasoru_mu(aday)), None)
        if k is None:
            # B-4 (v0.5.14) — SESSİZ GEÇME YOK. Dava kökü bulunamadığında
            # makbuz denetimi YAPILAMAZ; gönderilen dosya teslim-sınıfı
            # görünüyorsa bu bilinmezlik avukata GÖRÜNÜR kılınır (karar
            # devri; hook yine exit 0 — ASLA bloklamaz).
            # ENTEGRATÖR ŞERHİ (v0.5.14): B-4 ile v0.5.9-A1 ("dava dışı
            # klasörde SESSİZ") çatışıyordu. Ayrım şudur: denetlenecek bir
            # ÜRÜN fiilen var mı? Diskte OLMAYAN bir yol için denetlenecek
            # bir şey de yoktur — orada susmak gürültü disiplinidir, sessiz
            # ölüm değil. Uyarı yalnız ürün DİSKTE VARKEN ve kökü
            # bulunamadığında çıkar (B-4'ün asıl vakası: SendUserFile'ın
            # 'files' listesiyle gelen gerçek teslim ürünü).
            if (isinstance(veri, dict)
                    and veri.get("tool_name") == "SendUserFile"
                    and any(_sunum_adi_teslim_sinifi_mi(y) and os.path.isfile(y)
                            for y in _payload_dosya_yollari(veri))):
                print(json.dumps({"hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": (
                        "SUNUM KİLİDİ DOĞRULANAMADI (v0.5.14 — B-4): "
                        "gönderilen dosya teslim-sınıfı görünüyor ama dava "
                        "kökü bulunamadı; yeşil makbuz (_oa/defter/"
                        "teslim-makbuz.json) DENETLENEMEDİ. Ürünün kendi "
                        "dava klasöründen gönderildiğini doğrulayın ya da "
                        "oturumu dava kökünde açın. Yine de göndermek "
                        "avukatın kararıdır."),
                }}, ensure_ascii=False))
            return 0
        # T12 — ÇİFT-KANAL DEDUP (ayirt=payload parmak izi): yalnız aynı
        # saniyedeki AYNI payload (çift kanal kopyası) susturulur — aynı
        # saniyedeki farklı araç çağrıları kapı denetiminden AYNEN geçer
        # (elle-UDF/sunum-kilidi kapısı kaybolmaz).
        if _hook_dedup_kisa_devre(k, "pretool", ayirt=_hook_payload_ayirt(veri)):
            return 0
        _hook_nabiz_damgala(k, "pretool",
                            oturum=(veri or {}).get("session_id"))   # C3 + T4a
        # KURAL 1 (öncelik — mevcut v0.5.8.4 davranışı AYNEN): elle-UDF deseni.
        if _pretool_elle_udf_deseni_mi(metin):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": (
                    "ELLE-UDF ENGELİ (372 dersi 10-D): elle kurulan content.xml "
                    "UYAP editöründe AÇILMIYOR. Geçerli tek yol resmî hat: "
                    "udf_yaz.py veya npx udf-cli html2udf. Yine de devam etmek "
                    "avukatın kararıdır."),
            }}, ensure_ascii=False))
            _hook_olay_yaz(k, "pretool-ask", "elle-UDF deseni yakalandı (ask basıldı)")
            return 0
        # KURAL 1.5a — P0-1 RPM KARANTİNASI (v0.5.11, 1865-T1): rpm anlık-
        # görüntü yolundan `_oa/araclar`a kopya girişimi karar devri ister.
        if _pretool_rpm_karantina_mi(metin):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": (
                    "RPM KARANTİNASI (v0.5.11 — 1865/777 kök nedeni): "
                    "uygulamanın rpm anlık-görüntü yolu araç KAYNAĞI olarak "
                    "yasaktır — bayat nesil taşır (eski teslim_paketi makbuz "
                    "yazmaz, eski udf_yaz açılamayan UDF üretir). Meşru "
                    "kaynak: YÜKLÜ eklentinin skills/*/scripts/ kökü. Yine "
                    "de devam etmek avukatın kararıdır."),
            }}, ensure_ascii=False))
            _hook_olay_yaz(k, "pretool-ask",
                           "RPM karantinası: rpm→araclar kopya girişimi",
                           oturum=(veri.get("session_id")
                                   if isinstance(veri, dict) else None))
            return 0
        # KURAL 1.5b — P0-2 KİLİTLİ ÇEKİRDEK (v0.5.11, 1865-T3): çekirdek
        # script elle yazılmaz/ezilmez — kaynaktan kopyalanır.
        if _pretool_cekirdek_yazimi_mi(veri):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": (
                    "KİLİTLİ ÇEKİRDEK (v0.5.11 — 1865: üç çekirdek script "
                    "14-20KB taklitlerle ezilmişti): _oa/araclar çekirdeği "
                    "(pipeline_kayit/teslim_paketi/udf_yaz) Write/Edit ile "
                    "DEĞİŞTİRİLMEZ; eksikse yüklü eklentinin "
                    "skills/*/scripts/ kökünden KOPYALA. Yine de devam "
                    "etmek avukatın kararıdır."),
            }}, ensure_ascii=False))
            _hook_olay_yaz(k, "pretool-ask",
                           "kilitli çekirdek: araclar çekirdeğine Write/Edit",
                           oturum=(veri.get("session_id")
                                   if isinstance(veri, dict) else None))
            return 0
        # KURAL 2 — A1 SUNUM KİLİDİ (v0.5.9): makbuzsuz teslim-sınıfı gönderim.
        if _sunum_kilidi_gerekli_mi(veri, k):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": (
                    "SUNUM KİLİDİ (v0.5.9): yeşil makbuz yok — çıktı tüm "
                    "süreçten geçmeden avukata sunulamaz. Önce teslim_paketi "
                    "zincirini yeşile bağlayın (tek ölçüt: _oa/defter/"
                    "teslim-makbuz.json exit 0). Yine de göndermek avukatın "
                    "kararıdır."),
            }}, ensure_ascii=False))
            _hook_olay_yaz(k, "pretool-ask",
                           "SUNUM KİLİDİ: makbuzsuz teslim-sınıfı gönderim (ask basıldı)")
        return 0
    except Exception:
        return 0                        # sessiz başarısızlık — asla bloklamaz


# ── C4 (v0.5.8.5) — AÇILIŞ ENVANTERİ (SessionStart → hook-acilis) ──────────
# Saha deseni: model, kurulu script hattını BİLMEDEN oturuma başlıyor ve
# elden/doğaçlama yollara sapıyor (elle UDF, deftersiz koşu). SessionStart
# enjeksiyonu envanteri modelin bağlamına OTURUM AÇILIRKEN koyar — çağrı
# beklemez, SKILL.md gibi "ancak çağrılırsa yüklenir" tuzağına düşmez.
# Dava-dışı klasörde SESSİZDİR; ASLA bloklamaz (exit 0).
ACILIS_ENVANTERI = (
    ("oa_ingest.py", "evrak külliyatını en ucuz doğru yoldan metne çevirir "
                     "(_oa/metin + künye + indeks)"),
    ("tam_tur.py", "uçtan uca pipeline turunu koşturur, dosya-analiz.md working-memory'yi türetir"),
    ("oa_hafiza.py", "oturum/devir hafızasını ve _oa dizin sözleşmesini yönetir"),
    ("teslim_paketi.py", "teslim öncesi zinciri denetler, TESLİM MAKBUZUNU basar"),
    ("dilekce_denetim.py", "taslak dilekçeyi usul+şekil+atıf kapılarından geçirir"),
    ("udf_yaz.py", "HTML/MD'den UYAP UDF üretir (makbuz + doğrulama + kenar katmanlı)"),
    ("muhur_yaz.py", "ürüne .prov.json mührü basar/doğrular (sha soy zinciri)"),
    ("kaynak_blogu.py", "ürünün ilk satırlarına kaynak bloğunu (yol@sha8) yazar/denetler"),
    ("grafik_denetim.py", "illiyet grafını yapısal boşluk/kopukluk için denetler"),
    ("vakia_matris.py", "iddia↔delil matrisi + ispat boşluğu raporu üretir"),
    ("gizlilik_tara.py", "dışa çıkacak metinde müvekkil verisi/UYAP desenlerini tarar (Layer 0)"),
)


def hook_acilis(kok=None):
    """C4 — SessionStart hook komutu: dava klasöründeyse (C1 imzası dahil)
    kurulu script envanterini modelin bağlamına enjekte eder; dava-dışı
    klasörde SESSİZ; ASLA bloklamaz (her zaman 0)."""
    try:
        try:
            kokler = _hook_kok_adaylarini_bul(kok)
        except Exception:
            kokler = [os.path.abspath(kok or ".")]
        k = next((aday for aday in kokler if _dosya_klasoru_mu(aday)), None)
        if k is None:
            return 0                                     # dava klasörü değil — sessiz
        # T12 — ÇİFT-KANAL DEDUP: çift kayıtlı SessionStart aynı saniyede
        # iki kez ateşlerse ikinci enjeksiyon + defter olayı bastırılır.
        if _hook_dedup_kisa_devre(k, "acilis"):
            return 0
        _hook_nabiz_damgala(k, "acilis", oturum=_payload_oturum())   # C3 + T4a
        _cekirdek_kilitle(k)   # v0.5.11 P0-2 — idempotent, asla fırlatmaz
        satirlar = [
            "ORTAK AVUKAT — AÇILIŞ ENVANTERİ (SessionStart; bu klasör bir dava "
            "klasörü). Kurulu script hattı:",
        ]
        satirlar += [f"  · {ad} — {islev}" for ad, islev in ACILIS_ENVANTERI]
        satirlar.append(
            "UDF üretimi HER ZAMAN udf_yaz.py üzerinden yapılır — doğrudan npx "
            "udf-cli çağrısı makbuz/doğrulama/kenar katmanlarını atlar.")
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(satirlar),
        }}, ensure_ascii=False))
        _hook_olay_yaz(k, "acilis", "açılış envanteri enjekte edildi")
        return 0
    except Exception:
        return 0                        # sessiz başarısızlık — asla bloklamaz


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
    ap.add_argument("--adim-batch", dest="adim_batch", metavar="JSON_DOSYA",
                    help="G3a (v0.5.8.6): TEK çağrıda çok adım kaydı — JSON listesi "
                         '([{"adim":1,"parca":"oa-interview","durum":"UYGULANDI",'
                         '"kanit":"..."}]). Her kayıt --isle ile AYNI koddan geçer: '
                         "kanıt/önkoşul kuralları AYNEN (kanıtsız UYGULANDI yine RET), "
                         "tümü araç-imzalı yazılır.")
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
    ap.add_argument("--hook-acilis", action="store_true", dest="hook_acilis",
                     help="C4 (v0.5.8.5): model-bağımsız SessionStart hook komutu — "
                          "dava klasöründeyse (C1 klon imzası dahil) kurulu script "
                          "envanterini modelin BAĞLAMINA enjekte eder; dava-dışı "
                          "klasörde SESSİZDİR; ASLA bloklamaz (her zaman exit 0).")
    ap.add_argument("--hook-pretool", action="store_true", dest="hook_pretool",
                     help="v0.5.8.4 (372 dersi 10-D): model-bağımsız PreToolUse "
                          "hook komutu — stdin payload'ında elle-UDF kurulum "
                          "deseni (zipfile+content.xml / ZipFile(+.udf) varsa ve "
                          "kök bir DAVA klasörüyse 'ask' kararı basar; A1 "
                          "(v0.5.9) SUNUM KİLİDİ: SendUserFile ile makbuzsuz "
                          "teslim-sınıfı ürün gönderimi de 'ask' kararına düşer "
                          "(yeşil makbuz varsa sessiz); diğer tüm "
                          "hâllerde sessiz. ASLA bloklamaz (her zaman exit 0).")
    ap.add_argument("--avukat-karari", dest="avukat_karari", default=None,
                     help="M7 (Paket D): AVUKAT KARARI BEKLEYEN'deki bir çatalı "
                          "((--adim+--parca) VEYA --katman ile hedeflenir) NİHAİ "
                          "karar metniyle kaydeder — --gerekce ZORUNLU.")
    args = ap.parse_args()

    if args.hook_acilis:
        sys.exit(hook_acilis(args.kok))

    if args.hook_pretool:
        sys.exit(hook_pretool(args.kok))

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
    elif args.adim_batch:
        adim_batch(args)
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
