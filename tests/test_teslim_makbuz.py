# -*- coding: utf-8 -*-
"""P0-5 (v0.5.5) — TESLİM MAKBUZU testleri (teslim_paketi.py).

Kapsam: makbuz şema/sha doğruluğu, RED dosyası (başarısız deneme İZLİDİR),
adım-9 önkoşul kapısıyla (pipeline_kayit.py) uçtan uca etkileşim, sha
değişince exit 1, desen-dışı ad dokunmaz (ad-deseni TEK tetik DEĞİL —
pipeline_kayit tarafında ayrıca ad-bağımsız uyarı vardır), OA_SKILLS_KOK
fallback, --udf-yok makbuzda görünür, ve EN ÖNEMLİSİ: dairesel-bağımlılık
regresyon testi (teslim_paketi kendi üreteceği makbuzun YOKLUĞU yüzünden
kendine engel koymamalı).
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
TP_SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol"
             / "scripts" / "teslim_paketi.py")
PK_SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline"
             / "scripts" / "pipeline_kayit.py")
TT_SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline"
             / "scripts" / "tam_tur.py")
SKILLS_KOK = REPO / "plugins" / "ortak-avukat" / "skills"


def _teslim_paketi_modulu():
    """teslim_paketi.py'yi in-process yükler — makbuza yazılan sürüm damgasının
    TEK KAYNAĞI (testte sabit sürüm yazmak ikiz-liste yaratırdı)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_test_makbuz_teslim_paketi", TP_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_test_makbuz_teslim_paketi"] = mod
    spec.loader.exec_module(mod)
    return mod

TAM_TEMIZ_TASLAK = """İSTANBUL 4. ASLİYE HUKUK MAHKEMESİ HAKİMLİĞİ'NE

DAVACI: Ayşe Yılmaz (T.C. Kimlik No: 12345678901)
Adres: Örnek Mahallesi No:1 İstanbul

DAVALI: Mehmet Kaya

KONU: Alacağın tahsili talebimizden ibarettir.

AÇIKLAMALAR (VAKIALAR):
1. Taraflar arasındaki ticari ilişkiden doğan alacak vakıası aşağıda özetlenmiştir.
2. Davalı, sözleşme kapsamındaki edimini yerine getirmemiştir.

HUKUKİ SEBEPLER:
İlgili mevzuat hükümleri ve genel hukuk kuralları dayanak alınmıştır.

DELİLLER:
Tanık beyanları, bilirkişi incelemesi ve yazılı belgeler ispat vasıtasıdır.

NETİCE-İ TALEP:
Yukarıda açıklanan nedenlerle davanın kabulüne karar verilmesini saygılarımla talep ederim.

Tarih: 01.07.2026

Av. Ayşe Yılmaz
Vekil
İmza
"""

EKSIK_TASLAK = "Bu kısa bir taslaktır ve zorunlu unsurları içermez.\n"


def _tp(args, cwd=None, env=None):
    cp = subprocess.run(
        [sys.executable, str(TP_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(cwd) if cwd else None, env=env,
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _pk(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(PK_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _tt(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(TT_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


@pytest.fixture
def izole_kok():
    tmp = tempfile.mkdtemp()
    return pathlib.Path(tmp)


# ── (1) başarılı zincir → makbuz şema/sha doğru ─────────────────────────

def test_basarili_zincir_makbuz_yazar_sema_ve_sha_dogru(izole_kok):
    taslak = izole_kok / "temiz.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    kod, cikti = _tp([str(taslak), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod == 0, cikti

    makbuz_yol = izole_kok / "_oa" / "defter" / "teslim-makbuz.json"
    assert makbuz_yol.is_file()
    m = json.loads(makbuz_yol.read_text(encoding="utf-8"))
    assert m["exit_kodu"] == 0
    assert m["taslak_yol"] == str(taslak)
    assert m["taslak_sha256"] and len(m["taslak_sha256"]) == 64
    # Sürümü testte SABİTLEMEK ikiz-liste yaratır (her yama sürümünde test
    # kırılır ve "0.5.5" beklentisi sessizce bayatlar); damganın tek kaynağı
    # teslim_paketi.OA_SURUM'dur — dört-damga eşzamanlılığını zaten
    # test_hooks_wiring kilitler.
    assert m["surum"] == _teslim_paketi_modulu().OA_SURUM
    assert m["ictihat_muhakeme_kanali"] == "b2-tekil"
    assert isinstance(m["kapilar"], list) and len(m["kapilar"]) >= 4
    for k in m["kapilar"]:
        assert k["durum"] in ("OK", "BLOK", "ATLA", "BILGI")
    assert m["udf_yolu"]
    assert pathlib.Path(m["udf_yolu"]).is_file()


# ── (2) kapı kapanınca RED makbuzu var, başarı makbuzu yok/bayat ────────

def test_engellenen_zincir_red_makbuzu_yazar(izole_kok):
    taslak = izole_kok / "eksik.md"
    taslak.write_text(EKSIK_TASLAK, encoding="utf-8")

    kod, cikti = _tp([str(taslak), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod != 0, cikti

    red_yol = izole_kok / "_oa" / "defter" / "teslim-makbuz-RED.json"
    basari_yol = izole_kok / "_oa" / "defter" / "teslim-makbuz.json"
    assert red_yol.is_file()
    assert not basari_yol.is_file()
    m = json.loads(red_yol.read_text(encoding="utf-8"))
    assert m["exit_kodu"] == 1
    assert m["durdu"]


# ── (3) v0.5.5-defterli kökte makbuzsuz adım-9 UYGULANDI → hem --denetle
#        hem tam_tur --kaydet exit 1 ──────────────────────────────────────

def _defter_kur_ve_adim9_uygulandi_isle(kok):
    _pk(["--baslat", "Test Dosyası", "--kok", str(kok)], cwd=kok)
    uzun_kanit = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
    metin = kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(json.dumps({"toplam_evrak": 0, "kayitlar": []}),
                                          encoding="utf-8")
    defter = kok / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    (defter / "teslim-makbuz.json").write_text(json.dumps({"exit_kodu": 0}), encoding="utf-8")
    kod, cikti = _pk(
        ["--isle", "--adim", "9", "--parca", "oa-kontrol", "--durum", "UYGULANDI",
         "--kanit", uzun_kanit, "--kok", str(kok)],
        cwd=kok,
    )
    assert kod == 0, f"adım-9 gecerli-makbuzla isle edilemedi: {cikti}"
    # Makbuzu SİL — 'adım-9 UYGULANDI ama makbuz artık yok' senaryosu.
    (defter / "teslim-makbuz.json").unlink()


def test_makbuzsuz_adim9_ile_denetle_teslim_engeli(izole_kok):
    _defter_kur_ve_adim9_uygulandi_isle(izole_kok)
    kod, cikti = _pk(["--denetle", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod == 1, f"adım-9 UYGULANDI ama makbuz yokken --denetle TEMİZ geçmemeliydi:\n{cikti}"
    assert "TESLİM MAKBUZU" in cikti


# ── (4) TESLİM sonrası dosya değişti → sha uyumsuz → exit 1 ─────────────

def test_teslim_sonrasi_taslak_degisince_sha_uyumsuz_denetle_engeller(izole_kok):
    taslak = izole_kok / "temiz.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")
    kod, cikti = _tp([str(taslak), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod == 0, cikti

    # Taslağı SESSİZCE değiştir — makbuz "önce" hâlini taşıyor.
    taslak.write_text(TAM_TEMIZ_TASLAK + "\nEK PARAGRAF — sessizce eklendi.\n",
                       encoding="utf-8")

    _pk(["--baslat", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    uzun_kanit = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
    metin = izole_kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(json.dumps({"toplam_evrak": 0, "kayitlar": []}),
                                          encoding="utf-8")

    # P0-5 DÜZELTME(a) sinav-turu — bu artık DAHA ERKEN yakalanır: `--isle
    # --adim 9` KENDİSİ (makbuz↔taslak sha bağı `_makbuz_onkosul_saglam_mi`'ye
    # taşındığı için) sha uyumsuzluğunu YAZIM ANINDA reddeder; --serh OLMADAN
    # UYGULANDI yazılamaz.
    kod_isle, cikti_isle = _pk(
        ["--isle", "--adim", "9", "--parca", "oa-kontrol", "--durum", "UYGULANDI",
         "--kanit", uzun_kanit, "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_isle != 0, (
        f"sha uyumsuz makbuzla adım-9 UYGULANDI --serh'SİZ geçmemeliydi:\n{cikti_isle}")
    assert "sha" in cikti_isle.lower() or "DEĞİŞTİRİLMİŞ" in cikti_isle

    # --serh ile ZORLA geçilirse, --denetle'nin BAĞIMSIZ makbuz bütünlüğü
    # denetimi (`_makbuz_denetim_hesapla`) sha uyumsuzluğunu YİNE yakalamalı
    # (iki katman ayrı ayrı çalışır — biri diğerini SUBSTITUE etmez).
    gerekce = "Test amaçlı: sha uyumsuzluğuna rağmen ŞERH ile zorla geçiliyor."
    kod_serh, cikti_serh = _pk(
        ["--isle", "--adim", "9", "--parca", "oa-kontrol", "--durum", "UYGULANDI",
         "--kanit", uzun_kanit, "--serh", gerekce, "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_serh == 0, cikti_serh

    kod, cikti = _pk(["--denetle", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod == 1, f"taslak sessizce değişince --denetle sha uyumsuzluğunu yakalamalıydı:\n{cikti}"
    assert "sha" in cikti.lower() or "DEĞİŞTİRİLMİŞ" in cikti


# ── (5) eski (v0.5.5 öncesi) defterde aynı durum yalnız UYARI, exit 0 ───
# Doğrudan `_makbuz_denetim_hesapla` fonksiyon-seviyesinde test edilir —
# CLI --denetle exit kodu diğer adım/katmanların BEKLIYOR olmasından da
# etkilenir (bu testin odağı DEĞİL); modül-seviyesi test odaklı ve kırılgan
# olmayan doğrulama sağlar.

def _pk_modulu():
    import importlib.util
    spec = importlib.util.spec_from_file_location("pk_makbuz_test", PK_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_eski_defterde_makbuz_eksikligi_yalniz_uyari(izole_kok):
    """Geçiş supabı (T1): defterde HİÇ v0.5.5+ olay yoksa (surum_gorulen boş)
    makbuz eksikliği BLOKLEYICI değil, yalnız UYARIdır."""
    pk = _pk_modulu()
    d_eski = {
        "adimlar": {"9": {"parcalar": {"oa-kontrol": {"durum": "UYGULANDI"}}}},
        "surum_gorulen": [],  # eski defter — hiç v0.5.5+ olay yok
    }
    sorun, uyari = pk._makbuz_denetim_hesapla(str(izole_kok), d_eski)
    assert sorun is None, f"eski defterde makbuz eksikliği BLOKLEYICI olmamalıydı: {sorun}"
    assert uyari is not None and "eski/önceki-sürüm" in uyari


def test_v055_defterde_makbuz_eksikligi_blokleyici(izole_kok):
    """Aynı eksiklik, defterde EN AZ BİR v0.5.5+ olay VARSA (migrate olmuş)
    BLOKLEYICI olmalı."""
    pk = _pk_modulu()
    d_yeni = {
        "adimlar": {"9": {"parcalar": {"oa-kontrol": {"durum": "UYGULANDI"}}}},
        "surum_gorulen": ["0.5.5"],
    }
    sorun, uyari = pk._makbuz_denetim_hesapla(str(izole_kok), d_yeni)
    assert sorun is not None, "v0.5.5+ olay varken makbuz eksikliği BLOKLEYICI olmalıydı"
    assert uyari is None


def test_yama_surumu_gecis_supabini_GEVSETMEZ(izole_kok):
    """REGRESYON (v0.5.5.1): supap eşiği bir zamanlar `_OA_SURUM_TUPLE`ye
    bağlıydı — 0.5.5 → 0.5.5.1 yaması çıktığı anda SAHADAKİ TÜM v0.5.5
    defterleri "eski defter" sayılıp makbuz kapısı SESSİZCE gevşiyordu.
    Supabın sorusu "bu defter tam güncel sürümde mi" DEĞİL, "bu defter P0-5
    çağına geçmiş mi"dir; eşik bu yüzden çağın açıldığı sürüme sabittir ve
    sürüm artışıyla kaymaz."""
    pk = _pk_modulu()
    assert pk._MAKBUZ_CAG_ESIGI == (0, 5, 5), "çağ eşiği kaymamalı"
    assert pk._surum_tuple(pk.OA_SURUM) >= pk._MAKBUZ_CAG_ESIGI

    # Güncel sürümden ESKİ ama çağ-içi her defter blokleyici kalmalı.
    for gorulen in ("0.5.5", "0.5.5.1", "0.6.0"):
        d = {
            "adimlar": {"9": {"parcalar": {"oa-kontrol": {"durum": "UYGULANDI"}}}},
            "surum_gorulen": [gorulen],
        }
        sorun, _uyari = pk._makbuz_denetim_hesapla(str(izole_kok), d)
        assert sorun is not None, f"surum_gorulen={gorulen!r} çağ içinde — kapı gevşememeli"

    # Çağ ÖNCESİ defter hâlâ yalnız uyarı üretir (geçiş supabı korunur).
    d_onceki = {
        "adimlar": {"9": {"parcalar": {"oa-kontrol": {"durum": "UYGULANDI"}}}},
        "surum_gorulen": ["0.5.4"],
    }
    sorun, uyari = pk._makbuz_denetim_hesapla(str(izole_kok), d_onceki)
    assert sorun is None and uyari is not None


# ── (6) desen-dışı ad ('taslak-v3.md' gibi) → pipeline_kayit adım-9 kapısı
#        yine de makbuz arar (ad-bağımsız); teslim_paketi kendisi HER taslak
#        adında da çalışır (ad-deseni teslim_paketi tarafında hiç kullanılmaz)

def test_desen_disi_ad_teslim_paketini_engellemez(izole_kok):
    taslak = izole_kok / "taslak-v3.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")
    kod, cikti = _tp([str(taslak), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod == 0, cikti
    assert (izole_kok / "_oa" / "defter" / "teslim-makbuz.json").is_file()


# ── (7) OA_SKILLS_KOK ile farklı cwd'den script çözümü ──────────────────

def test_oa_skills_kok_fallback_ile_script_bulunur(izole_kok):
    """Alt scriptleri GEÇİCİ bir dizine kopyalayıp `OA_SKILLS_KOK` ile
    işaret ederek path-fix fallback'inin çalıştığını doğrular."""
    import os
    fallback_kok = tempfile.mkdtemp()
    for skill in ("oa-dilekce", "oa-kontrol", "oa-gizlilik", "oa-pipeline"):
        kaynak = SKILLS_KOK / skill / "scripts"
        hedef = pathlib.Path(fallback_kok) / skill / "scripts"
        hedef.mkdir(parents=True, exist_ok=True)
        for dosya in kaynak.glob("*.py"):
            shutil.copy2(dosya, hedef / dosya.name)

    taslak = izole_kok / "temiz.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    env = dict(os.environ)
    env["OA_SKILLS_KOK"] = fallback_kok
    kod, cikti = _tp([str(taslak), "--tip", "genel", "--kok", str(izole_kok)], env=env)
    assert kod == 0, cikti


# ── (8) --udf-yok makbuzda görünür ───────────────────────────────────────

def test_udf_yok_bayragi_makbuza_yazilir(izole_kok):
    taslak = izole_kok / "temiz.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")
    kod, cikti = _tp([str(taslak), "--tip", "genel", "--kok", str(izole_kok), "--udf-yok"])
    assert kod == 0, cikti
    udf_yolu = taslak.with_suffix(taslak.suffix + ".udf")
    assert not udf_yolu.exists()

    m = json.loads((izole_kok / "_oa" / "defter" / "teslim-makbuz.json").read_text(encoding="utf-8"))
    assert m["udf_atlandi_istekle"] is True
    assert m["udf_yolu"] is None


# ── (9) Dairesel-bağımlılık regresyon testi (sinav'ın doğrudan istediği) ─

_ADIM_PARCALARI_TEST = {
    0: ["manifest"],
    1: ["oa-interview", "oa-illiyet", "oa-sure"],
    2: ["oa-alan"],
    3: ["oa-ictihat"],
    4: ["oa-vakia"],
    5: ["oa-kiyas"],
    6: ["oa-strateji"],
    7: ["oa-antitez"],
    8: ["oa-dilekce"],
}
_GEREKCE_TEST = "Test amaçlı: bu senaryoda bu adım/katman gereksiz kabul edildi."


def test_dairesel_bagimlilik_yok_teslim_pattern_dosya_ile_zorlasiz_tamamlanir(izole_kok):
    """P0-5×P0-6 dairesel-KİLİT BLOKER regresyonu (Paket B sinav bulgusu):
    GERÇEK bir pipeline_kayit defterinde (0-8 adım/katmanlar işlenmiş, 9/10
    hâlâ BEKLIYOR) teslim_paketi'nin (d) kapısı --serh'SİZ/--zorla'SIZ
    tamamlanabilmeli; ardından adım-9 UYGULANDI da (makbuz artık ÜRETİLMİŞ
    olduğundan) exit 0 dönmeli. ESKİ TEST yalnız TESLİM-desenli DOSYA
    VARLIĞINI sınıyordu — `pipeline_kayit.py --baslat` hiç çağrılmadığından
    (d) kapısı `_defter_var_mi()==False` dalına düşüp GERÇEK denetim hiç
    çalışmıyordu (BLOKER-1 tam da bu boşluktan geçmişti). Bu sürüm gerçek
    bir defter açıp (d) kapısını FİİLEN tetikler."""
    metin = izole_kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 1,
                    "kayitlar": [{"kaynak": "dilekce.pdf", "sha": "a" * 16}]}),
        encoding="utf-8")
    (izole_kok / "dilekce.pdf").write_text("plasöy-holder", encoding="utf-8")

    kod_b, cikti_b = _pk(["--baslat", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_b == 0, cikti_b

    for adim, parcalar in sorted(_ADIM_PARCALARI_TEST.items()):
        for parca in parcalar:
            kod, cikti = _pk(
                ["--isle", "--adim", str(adim), "--parca", parca, "--durum", "GEREKSIZ",
                 "--gerekce", _GEREKCE_TEST, "--kok", str(izole_kok)], cwd=izole_kok)
            assert kod == 0, cikti
    for katman in ("oa-usul", "oa-illiyet", "oa-gizlilik"):
        kod, cikti = _pk(["--katman", katman, "--durum", "GEREKSIZ",
                           "--gerekce", _GEREKCE_TEST, "--kok", str(izole_kok)], cwd=izole_kok)
        assert kod == 0, cikti

    cikti_dizin = izole_kok / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    taslak = cikti_dizin / "08-dilekce-TESLIM.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    # teslim_paketi --serh'SİZ/--zorla'SIZ tamamlanabiliyor mu? (adım 9/10 hâlâ
    # BEKLIYOR — (d) kapısı bunu TESLİM-ÖNCESİ kipte artık sorun SAYMAMALI.)
    kod_tp, cikti_tp = _tp([str(taslak), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod_tp == 0, f"gerçek defterli kökte teslim_paketi tamamlanamadı:\n{cikti_tp}"
    assert "--serh" not in cikti_tp
    assert "--zorla" not in cikti_tp

    # adım-9 UYGULANDI artık (makbuz üretilmiş) exit 0 dönmeli — DAİRESEL KİLİT
    # (BLOKER-1) buradaydı: eski davranışta bu satır --serh olmadan asla geçmezdi.
    uzun_kanit = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
    kod_9, cikti_9 = _pk(
        ["--isle", "--adim", "9", "--parca", "oa-kontrol", "--durum", "UYGULANDI",
         "--kanit", uzun_kanit, "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_9 == 0, (
        "P0-5+P0-6 dairesel kilit REGRESYONU — teslim makbuzu üretilmişken "
        f"adım-9 UYGULANDI reddedilmemeliydi:\n{cikti_9}"
    )
    assert "--serh" not in cikti_9


# ── (10) makbuz↔taslak bağı — BAŞKA bir dosya için üretilmiş makbuz BU
#         dosyayı teslime yetkilendirmez (P0-5 DÜZELTME(a) sinav-turu) ──────

def test_makbuz_baska_dosya_icin_yeniyken_yeni_dilekce_adim9u_yetkilendirmez(izole_kok):
    """A dosyası için BAŞARILI bir teslim (makbuz exit0) üretildikten SONRA
    tamamen FARKLI, hiç teslim edilmemiş bir B dosyası (`08-dilekce-son.md`)
    yazılırsa: (1) --denetle 'makbuzsuz dilekçe adayı' uyarısı ÜRETMELİ,
    (2) adım-9 UYGULANDI da (B dosyası fiilen teslim edilmediği için)
    REDDEDİLMELİ — bayat/yanlış-dosya makbuzu B'yi yetkilendirmemeli (sinav
    bulgusunun doğrudan istediği kabul kriteri: 'A için makbuz + B adlı yeni
    dilekçe → uyarı ÜRETİLİR ve adım-9 RET edilir')."""
    cikti_dizin = izole_kok / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    taslak_a = cikti_dizin / "taslak-A.md"
    taslak_a.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    kod_tp, cikti_tp = _tp([str(taslak_a), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod_tp == 0, cikti_tp

    # A tamamen farklı, HİÇ teslim edilmemiş bir B dosyası yazılıyor.
    import time
    time.sleep(0.01)
    taslak_b = cikti_dizin / "08-dilekce-son.md"
    taslak_b.write_text(TAM_TEMIZ_TASLAK.replace("Ayşe Yılmaz", "Fatma Demir"),
                         encoding="utf-8")

    metin = izole_kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(json.dumps({"toplam_evrak": 0, "kayitlar": []}),
                                          encoding="utf-8")
    kod_b, cikti_b = _pk(["--baslat", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_b == 0, cikti_b

    kod_d, cikti_d = _pk(["--denetle", "--kok", str(izole_kok)], cwd=izole_kok)
    assert "makbuzsuz dilekçe adayı" in cikti_d, (
        f"BAŞKA dosya için üretilmiş makbuz varken B için de uyarı basılmalıydı:\n{cikti_d}")
    assert str(taslak_b) in cikti_d or taslak_b.name in cikti_d

    uzun_kanit = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
    kod_9, cikti_9 = _pk(
        ["--isle", "--adim", "9", "--parca", "oa-kontrol", "--durum", "UYGULANDI",
         "--kanit", uzun_kanit, "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_9 != 0, (
        "P0-5 DÜZELTME(a) REGRESYONU — A için üretilmiş makbuz, B adlı FARKLI "
        f"bir dilekçeyi adım-9 UYGULANDI için yetkilendirmemeliydi:\n{cikti_9}")
    assert "makbuzsuz dilekçe adayı" in cikti_9 or taslak_b.name in cikti_9


# ── (10-b) DOĞAL SIRA regresyonu (Paket-B sinav-turu BLOKER giderimi):
#          teslim A → adım-9 UYGULANDI (makbuz A ile UYUMLU) → SONRA B yazılır
#          — bu (10)'un TERSİ değil, en sık gerçek akıştır. Eski davranışta
#          `_makbuz_denetim_hesapla` yalnız makbuzun İÇ tutarlılığına (exit_kodu
#          + sha) bakıyordu, `_dilekce_sekilli_makbuzsuz_uyarisi`'ni HİÇ
#          çağırmıyordu — bu yüzden bu doğal sıra hem `--denetle` hem
#          `tam_tur --kaydet`'i TEMİZ geçiyordu (tam yeşil tabloyla kapanan
#          hiç teslim edilmemiş bir revize).

def test_dogal_sira_teslim_sonrasi_revize_hem_denetle_hem_kaydet_engeller(izole_kok):
    cikti_dizin = izole_kok / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    taslak_a = cikti_dizin / "taslak-A.md"
    taslak_a.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    kod_tp, cikti_tp = _tp([str(taslak_a), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod_tp == 0, cikti_tp

    metin = izole_kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(json.dumps({"toplam_evrak": 0, "kayitlar": []}),
                                          encoding="utf-8")

    kod_b, cikti_b = _pk(["--baslat", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_b == 0, cikti_b

    # adım-9 UYGULANDI — bu ANDA makbuz A ile TAM uyumlu (yazım-anı kapısından
    # --serh GEREKMEDEN geçer).
    uzun_kanit = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
    kod_9, cikti_9 = _pk(
        ["--isle", "--adim", "9", "--parca", "oa-kontrol", "--durum", "UYGULANDI",
         "--kanit", uzun_kanit, "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_9 == 0, f"adım-9 UYGULANDI, makbuz A ile UYUMLUYKEN reddedilmemeliydi:\n{cikti_9}"

    # SONRA — A'nın teslimiyle İLGİSİZ — B (revize/yeni sürüm) yazılır.
    import time
    time.sleep(0.01)
    taslak_b = cikti_dizin / "08-dilekce-son.md"
    taslak_b.write_text(TAM_TEMIZ_TASLAK.replace("Ayşe Yılmaz", "Fatma Demir"),
                         encoding="utf-8")

    kod_d, cikti_d = _pk(["--denetle", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_d == 1, (
        "DOĞAL SIRA REGRESYONU — teslim A → adım-9 UYGULANDI → SONRA B yazılınca "
        f"--denetle TEMİZ dönmemeliydi (makbuz artık B ile UYUMSUZ):\n{cikti_d}")
    assert "TESLİM MAKBUZU" in cikti_d
    assert "TESLİM ENGELİ" in cikti_d

    _tt(["--baslat", "--dosya", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    kod_kaydet, cikti_kaydet = _tt(["--kaydet", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_kaydet == 1, (
        "DOĞAL SIRA REGRESYONU — aynı senaryoda tam_tur --kaydet de BLOK "
        f"olmalıydı (defter kapısı bu sorunu devralmalı):\n{cikti_kaydet}")


def test_cikti_alt_klasordeki_dilekce_makbuzsuz_uyariyi_tetikler(izole_kok):
    """Ş9 (v0.5.5 şerh turu, ÖNEMLİ) — `_oa/cikti` ALT KLASÖR körlüğü: canlı
    sömürü kanıtı (Probe 3) — `_oa/cikti/01-notlar.md` (dilekçe-şekilli
    DEĞİL) İLE `_oa/cikti/dilekce/08-dava-dilekcesi.md` (GERÇEK dilekçe, bir
    ALT KLASÖRDE) birlikte VAR. DÜZELTME ÖNCESİ hem `tam_tur._cikti_topla`
    hem `pipeline_kayit._dilekce_sekilli_makbuzsuz_uyarisi` `os.listdir` ile
    ÖZYİNELEMESİZDİ — alt klasördeki GERÇEK dilekçe SESSİZCE atlanıyor, tüm
    P0-5 makbuz zinciri (ve kayıpsızlık invaryantı — dosya-analiz.md'ye hiç
    gömülmeme) bir alt klasöre dosya koymakla atlanabiliyordu. DÜZELTME
    SONRASI: her iki tarama noktası da `os.walk` ile ÖZYİNELEMELİDİR."""
    cikti_dizin = izole_kok / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "01-notlar.md").write_text(
        "Kısa bir çalışma notu, dilekçe değil.", encoding="utf-8")
    alt_dizin = cikti_dizin / "dilekce"
    alt_dizin.mkdir(parents=True, exist_ok=True)
    (alt_dizin / "08-dava-dilekcesi.md").write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    # (1) pipeline_kayit tarafı: alt klasördeki dilekçe ad-bağımsız uyarıyı
    # tetiklemeli (hiç teslim denemesi yok).
    kod_b, _c = _pk(["--baslat", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_b == 0
    kod_d, cikti_d = _pk(["--denetle", "--kok", str(izole_kok)], cwd=izole_kok)
    assert "makbuzsuz dilekçe adayı" in cikti_d, (
        f"alt klasördeki dilekçe pipeline_kayit tarafından GÖRÜLMELİYDİ:\n{cikti_d}")
    assert "dava-dilekcesi" in cikti_d

    # (2) tam_tur tarafı: _cikti_topla alt klasördeki dosyayı da TOPLAMALI —
    # hiç teslim denenmemiş bu dilekçe ile --kaydet BLOK olmalı.
    metin = izole_kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(json.dumps({"toplam_evrak": 0, "kayitlar": []}),
                                          encoding="utf-8")
    _tt(["--baslat", "--dosya", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    kod_kaydet, cikti_kaydet = _tt(["--kaydet", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_kaydet == 1, (
        f"alt klasördeki dilekçe --kaydet tarafından hiç TESLİM edilmeden "
        f"TAMAM damgalanmamalıydı:\n{cikti_kaydet}")


def test_deftersiz_akiste_doga_sira_bypass_kaydet_engeller(izole_kok):
    """Ş8 (v0.5.5 şerh turu, BLOKER) — P0-5(e) kabul ölçütü ayrışması: canlı
    sömürü kanıtı (Probe 2/D) — `_oa/defter` HİÇ AÇILMAMIŞ (pipeline_kayit
    --baslat/--isle HİÇ ÇAĞRILMAMIŞ; (iv-c) defter kapısı bu yüzden devreye
    GİRMEZ) bir kökte: teslim_paketi.py taslak-A için GEÇERLİ bir makbuz
    üretir; SONRA ondan daha yeni, HİÇ teslim denenmemiş bir REVİZE dosyası
    (`08-dilekce-v2-REVIZE.md`) yazılır. DÜZELTME ÖNCESİ `_teslim_final_
    kontrol` yalnız 'makbuzun taslağı ADAY KÜMESİNDE var mı' soruyordu — A
    hâlâ adaylardan biri olduğundan bu soru HER ZAMAN 'evet' dönüyor ve
    `tam_tur --kaydet` rc=0 ile TAMAM damgalıyordu (revize HİÇ teslim
    edilmeden). DÜZELTME SONRASI: ölçüt `pipeline_kayit._dilekce_sekilli_
    makbuzsuz_uyarisi` ile SİMETRİK — makbuz artık EN YENİ dilekçe-şekilli
    dosyaya ait olmadığından BLOK."""
    cikti_dizin = izole_kok / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    taslak_v1 = cikti_dizin / "08-dilekce-v1.md"
    taslak_v1.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    kod_tp, cikti_tp = _tp([str(taslak_v1), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod_tp == 0, cikti_tp

    metin = izole_kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(json.dumps({"toplam_evrak": 0, "kayitlar": []}),
                                          encoding="utf-8")

    # KRİTİK: _oa/defter HİÇ açılmıyor — pipeline_kayit --baslat/--isle HİÇ
    # ÇAĞRILMIYOR (deftersiz akış; (iv-c) defter kapısı devre dışı kalır).
    assert not (izole_kok / "_oa" / "defter" / "pipeline-olaylar.jsonl").exists()

    import time
    time.sleep(0.01)
    taslak_v2 = cikti_dizin / "08-dilekce-v2-REVIZE.md"
    taslak_v2.write_text(TAM_TEMIZ_TASLAK.replace("Ayşe Yılmaz", "Fatma Demir"),
                         encoding="utf-8")

    _tt(["--baslat", "--dosya", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    kod_kaydet, cikti_kaydet = _tt(["--kaydet", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_kaydet == 1, (
        "DEFTERSİZ DOĞAL-SIRA BYPASS REGRESYONU (Ş8) — v2-REVIZE hiç teslim "
        f"edilmeden tam_tur --kaydet TAMAM damgalamamalıydı:\n{cikti_kaydet}")
    assert "makbuzsuz dilekçe adayı" in cikti_kaydet or "teslim" in cikti_kaydet.lower()


def test_makbuzsuz_dilekce_uyarisi_cift_basilmaz(izole_kok):
    """Ş10 (v0.5.5 şerh turu, KUCUK) — `_makbuz_denetim_hesapla` (adım-9
    uyum kolu) ile bağımsız `_dilekce_sekilli_makbuzsuz_uyarisi` çağrısı AYNI
    metni İKİ KEZ (biri '✗ sorun', biri '⚠ uyarı' olarak) BASMAMALI. Aynı
    doğal-sıra senaryosu (teslim A → adım-9 UYGULANDI → SONRA B yazılır)
    kullanılır; bu kez tekrarsızlık doğrudan doğrulanır."""
    cikti_dizin = izole_kok / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    taslak_a = cikti_dizin / "taslak-A.md"
    taslak_a.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    kod_tp, cikti_tp = _tp([str(taslak_a), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod_tp == 0, cikti_tp

    metin = izole_kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(json.dumps({"toplam_evrak": 0, "kayitlar": []}),
                                          encoding="utf-8")

    kod_b, cikti_b = _pk(["--baslat", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_b == 0, cikti_b

    uzun_kanit = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
    kod_9, cikti_9 = _pk(
        ["--isle", "--adim", "9", "--parca", "oa-kontrol", "--durum", "UYGULANDI",
         "--kanit", uzun_kanit, "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_9 == 0, cikti_9

    import time
    time.sleep(0.01)
    taslak_b = cikti_dizin / "08-dilekce-son.md"
    taslak_b.write_text(TAM_TEMIZ_TASLAK.replace("Ayşe Yılmaz", "Fatma Demir"),
                         encoding="utf-8")

    kod_d, cikti_d = _pk(["--denetle", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_d == 1, cikti_d
    assert cikti_d.count("makbuzsuz dilekçe adayı") == 1, (
        f"'makbuzsuz dilekçe adayı' metni ✗ sorun VE ⚠ uyarı olarak İKİ KEZ "
        f"basılmamalıydı:\n{cikti_d}")


# ── (11) 'en yeni dosya' tetikleyicisi — dilekçe-şekilli OLMAYAN bir sonraki
#         dosya uyarıyı SUSTURMAMALI (P0-5 DÜZELTME(a) sinav-turu) ─────────

def test_dilekce_sonrasi_not_dosyasi_uyariyi_susturmaz(izole_kok):
    cikti_dizin = izole_kok / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "08-dilekce-TESLIM.md").write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    import time
    time.sleep(0.01)
    (cikti_dizin / "09-not.md").write_text("Kısa bir çalışma notu, dilekçe değil.",
                                            encoding="utf-8")

    kod_b, _c = _pk(["--baslat", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_b == 0
    kod_d, cikti_d = _pk(["--denetle", "--kok", str(izole_kok)], cwd=izole_kok)
    assert "makbuzsuz dilekçe adayı" in cikti_d, (
        "dilekçeden SONRA yazılmış dilekçe-şekilli-OLMAYAN bir dosya uyarıyı "
        f"susturmamalıydı:\n{cikti_d}")


# ── (12) [F] tam olarak BİR KEZ koşar (P0-5 DÜZELTME(c) çift-[F] tekilleştirme)

def test_ictihat_muhakeme_denetim_bir_kez_calisir(izole_kok):
    taslak = izole_kok / "temiz.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")
    kod, cikti = _tp([str(taslak), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod == 0, cikti
    imza = "İÇTİHAT MUHAKEME DENETİMİ — oa-kontrol (deterministik, YAPISAL)"
    assert cikti.count(imza) == 1, (
        f"ictihat_muhakeme_denetim.py TAM OLARAK BİR KEZ koşmalıydı (yalnız (b2)), "
        f"{cikti.count(imza)} kez koştu:\n{cikti}")


# ── (13) 'udf_yaz üretimi = TESLİM olayı' — makbuzsuz UDF advisory uyarısı ──

def test_makbuzsuz_udf_uretimi_uyarisi(izole_kok):
    taslak = izole_kok / "temiz.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")
    kod, cikti = _tp([str(taslak), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod == 0, cikti

    import time
    time.sleep(0.01)
    # teslim_paketi'nin ZİNCİRİNİ atlayarak elden bir .udf üretimi simüle edilir.
    ekstra_udf = izole_kok / "elden-uretilmis.md.udf"
    ekstra_udf.write_bytes(b"PK\x03\x04sahte-udf-icerigi")

    kod_b, _c = _pk(["--baslat", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_b == 0
    kod_d, cikti_d = _pk(["--denetle", "--kok", str(izole_kok)], cwd=izole_kok)
    assert "makbuzsuz UDF üretimi" in cikti_d, (
        f"zincir atlanarak üretilmiş .udf GÖRÜNÜR bir uyarı üretmeliydi:\n{cikti_d}")
    assert "elden-uretilmis.md.udf" in cikti_d


def test_normal_zincir_udf_uretimi_uyari_uretmez(izole_kok):
    """teslim_paketi'nin KENDİ ürettiği .udf (makbuzun `udf_yolu` alanındaki
    dosya) 'makbuzsuz UDF üretimi' uyarısını YANLIŞLIKLA TETİKLEMEMELİ."""
    taslak = izole_kok / "temiz.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")
    kod, cikti = _tp([str(taslak), "--tip", "genel", "--kok", str(izole_kok)])
    assert kod == 0, cikti
    assert (izole_kok / "temiz.md.udf").is_file()

    kod_b, _c = _pk(["--baslat", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod_b == 0
    kod_d, cikti_d = _pk(["--denetle", "--kok", str(izole_kok)], cwd=izole_kok)
    assert "makbuzsuz UDF üretimi" not in cikti_d, (
        f"teslim_paketi'nin KENDİ ürettiği UDF yanlışlıkla uyarı üretti:\n{cikti_d}")


def test_hic_teslim_denenmemis_teslim_pattern_dosya_kaydet_engeller(izole_kok):
    """HİÇ teslim_paketi koşulmamış (makbuz/RED yok) ama _oa/cikti'da
    TESLİM-desenli dosya varsa --kaydet BLOK olmalı (T1 önerisi: 'hiç
    denenmemiş teslimi blokla')."""
    metin = izole_kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 1,
                    "kayitlar": [{"kaynak": "dilekce.pdf", "sha": "a" * 16}]}),
        encoding="utf-8")
    (izole_kok / "dilekce.pdf").write_text("plasöy-holder", encoding="utf-8")
    cikti_dizin = izole_kok / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "08-dilekce-TESLIM.md").write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    _tt(["--baslat", "--dosya", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    kod, cikti = _tt(["--kaydet", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod == 1, f"hiç teslim denenmemişken --kaydet BLOK olmalıydı:\n{cikti}"
    assert "teslim" in cikti.lower()


def test_ad_desensiz_dilekce_sekilli_dosya_da_kaydet_engeller(izole_kok):
    """Paket-B sinav-turu BLOKER giderimi ('AD-DESENİ TEK TETİK DEĞİL' sınıfı):
    `_teslim_final_kontrol` artık yalnız `*TESLIM*`/`*FINAL*` ADINA değil,
    dilekçe-şekilli İÇERİĞE (pipeline_kayit._DILEKCE_DESEN) de bakar. Bu,
    yukarıdaki testin AD-DESENSİZ ikizidir: aynı içerik, `08-dilekce-son.md`
    adıyla (tam da sinav'ın kanıtladığı, gerçek oa-pipeline SKILL.md
    adlandırma şemasına uygun 've hiç ateşlenmeyen' kaçak ad)."""
    metin = izole_kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 1,
                    "kayitlar": [{"kaynak": "dilekce.pdf", "sha": "a" * 16}]}),
        encoding="utf-8")
    (izole_kok / "dilekce.pdf").write_text("plasöy-holder", encoding="utf-8")
    cikti_dizin = izole_kok / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "08-dilekce-son.md").write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    _tt(["--baslat", "--dosya", "Test Dosyası", "--kok", str(izole_kok)], cwd=izole_kok)
    kod, cikti = _tt(["--kaydet", "--kok", str(izole_kok)], cwd=izole_kok)
    assert kod == 1, (
        f"ad-deseni TAŞIMAYAN ama içeriği dilekçe-şekilli dosya da (hiç teslim "
        f"denenmemişken) --kaydet'i BLOK etmeliydi:\n{cikti}")
    assert "teslim" in cikti.lower()
