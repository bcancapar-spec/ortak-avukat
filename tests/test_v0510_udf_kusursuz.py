# -*- coding: utf-8 -*-
"""v0.5.10 — KUSURSUZ UDF DÖNÜŞÜMÜ (307 karnesi K1/K2 + çift-uzantı onarımı).

Saha kanıtı (307 karnesi, elle doğrulanmış):
  K1 — teslim UDF'i yeşil makbuzdan ~68 dk SONRA yeniden üretildi; mühür
       (.prov.json) tazelenmedi → mühürdeki sha ile dosyanın gerçek sha'sı
       uyuşmaz hâle geldi ve HİÇBİR katman bunu yakalamadı.
  K2 — makbuzun ürün listesi yalnız dahilî adlı nüshayı saydı; avukatın
       fiilen yükleyeceği resmî adlı UDF makbuz kapsamına hiç girmedi.
  Çift uzantı — 40-UYAP kopyası "…TESLIM.md.udf" adıyla doğdu.

v0.5.10 sözleşmesi (bu testlerin kilitlediği):
  1. ATOMİK MÜHÜR: udf_yaz her başarılı üretimde .prov.json'u KOŞULSUZ
     yazar/tazeler (üretim ile mühür ayrık olamaz). E-imzalı nüshaya
     ASLA dokunmaz (e-imza halkası korunur).
  2. FİLO TAZELİĞİ: teslim zinciri yalnız seçili adayı değil, dava kökü +
     40-UYAP'taki TÜM teslim-sınıfı .udf'leri mühür-tazelik denetiminden
     geçirir; mühürsüz/bayat ürün → RED. Kayıtlar makbuza girer (K2).
  3. ÇİFT-UZANTI: ".md.udf" sınıfı adlar normalize edilir.
  4. SUNUM KİLİDİ: yeşil makbuz VARKEN bile mühür-kırık teslim-sınıfı ürün
     SendUserFile edilirse 'ask' doğar (makbuz-sonrası değişiklik penceresi).

Tamamen ağsız/deterministik; tüm veriler sentetiktir (tmp_path).
"""
import importlib.util
import json
import pathlib
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SK = REPO / "plugins" / "ortak-avukat" / "skills"


def _yukle(gorece, modul_adi):
    yol = SK / gorece
    assert yol.is_file(), f"bulunamadı: {yol}"
    spec = importlib.util.spec_from_file_location(modul_adi, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def udf_yaz():
    return _yukle("oa-dilekce/scripts/udf_yaz.py", "v0510_udf_yaz")


@pytest.fixture(scope="module")
def teslim():
    return _yukle("oa-kontrol/scripts/teslim_paketi.py", "v0510_teslim")


@pytest.fixture(scope="module")
def pk():
    return _yukle("oa-pipeline/scripts/pipeline_kayit.py", "v0510_pk")


def _udf_kur(yol, icerik=b"<content>x</content>", imzali=False):
    yol.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(yol, "w") as z:
        z.writestr("content.xml", icerik)
        if imzali:
            z.writestr("sign.sgn", b"\x00imza")
    return yol


def _sha(yol):
    import hashlib
    return hashlib.sha256(yol.read_bytes()).hexdigest()


def _prov_yaz(udf_yolu, sha, tip="dilekce"):
    kayit = {"prov_schema": "oa-muhur/1.0", "artifact_sha256": sha,
             "entity_type": tip, "artifact_file": udf_yolu.name,
             "was_generated_by": "test"}
    (pathlib.Path(str(udf_yolu) + ".prov.json")).write_text(
        json.dumps(kayit), encoding="utf-8")
    return kayit


# ────────────────────────── 1. ATOMİK MÜHÜR (K1) ──────────────────────────

def test_atomik_muhur_basilir(udf_yaz, tmp_path):
    """Üretim sonrası mühür KOŞULSUZ basılır ve sha gerçek dosyayla eşleşir."""
    kok = tmp_path
    (kok / "_oa").mkdir()
    u = _udf_kur(kok / "dilekce.udf")
    prov_yolu, hata = udf_yaz._prov_muhur_yaz(str(u), kok=str(kok),
                                              motor="html2udf")
    assert hata is None and prov_yolu
    kayit = json.loads(pathlib.Path(prov_yolu).read_text(encoding="utf-8"))
    assert kayit["artifact_sha256"] == _sha(u)
    assert "udf_yaz" in str(kayit.get("was_generated_by", ""))
    assert kayit.get("prov_schema") == "oa-muhur/1.0"


def test_atomik_muhur_tazelenir(udf_yaz, tmp_path):
    """K1'in tam senaryosu: dosya değişti → yeni üretim mührü TAZELER."""
    kok = tmp_path
    (kok / "_oa").mkdir()
    u = _udf_kur(kok / "dilekce.udf", b"<content>v1</content>")
    udf_yaz._prov_muhur_yaz(str(u), kok=str(kok))
    eski = json.loads((kok / "dilekce.udf.prov.json").read_text(encoding="utf-8"))
    _udf_kur(kok / "dilekce.udf", b"<content>v2 DEGISTI</content>")
    udf_yaz._prov_muhur_yaz(str(u), kok=str(kok))
    yeni = json.loads((kok / "dilekce.udf.prov.json").read_text(encoding="utf-8"))
    assert yeni["artifact_sha256"] == _sha(u)
    assert yeni["artifact_sha256"] != eski["artifact_sha256"]


def test_atomik_muhur_imzaliya_dokunmaz(udf_yaz, tmp_path):
    """E-imza halkası: imzalı nüshanın mührü ASLA ezilmez."""
    kok = tmp_path
    (kok / "_oa").mkdir()
    u = _udf_kur(kok / "imzali.udf", imzali=True)
    eski_kayit = _prov_yaz(u, "0" * 64, tip="e-imzali-nusha")
    prov_yolu, hata = udf_yaz._prov_muhur_yaz(str(u), kok=str(kok))
    assert prov_yolu is None and hata  # dokunulmadı, gerekçe döndü
    simdiki = json.loads((kok / "imzali.udf.prov.json").read_text(encoding="utf-8"))
    assert simdiki == eski_kayit


# ────────────────────────── 2. ÇİFT-UZANTI ──────────────────────────

@pytest.mark.parametrize("verilen,beklenen", [
    ("x.md.udf", "x.udf"),
    ("dilekce.html.udf", "dilekce.udf"),
    ("y.txt.udf", "y.udf"),
    ("temiz.udf", "temiz.udf"),          # dokunulmaz
    ("arsiv.tar.udf", "arsiv.tar.udf"),  # bilinmeyen ara uzantı — dokunulmaz
])
def test_cikti_adi_normalize(udf_yaz, verilen, beklenen):
    yeni, notu = udf_yaz._cikti_adi_normalize(verilen)
    assert pathlib.Path(yeni).name == beklenen
    if verilen != beklenen:
        assert notu  # düzeltme yapıldıysa görünür not döner
    else:
        assert notu is None


# ────────────────────────── 3. FİLO TAZELİĞİ (K1+K2) ──────────────────────────

def test_filo_listesi_kapsami(teslim, tmp_path):
    """Dava kökü + 40-UYAP taranır; _oa/cikti çalışma nüshaları filo DIŞI."""
    kok = tmp_path
    a = _udf_kur(kok / "resmi-ad.udf")
    b = _udf_kur(kok / "40-UYAP" / "kopya.udf")
    _udf_kur(kok / "_oa" / "cikti" / "calisma.udf")
    filo = teslim._teslim_sinifi_udf_listesi(str(kok))
    adlar = sorted(pathlib.Path(x).name for x in filo)
    assert adlar == ["kopya.udf", "resmi-ad.udf"]


def test_filo_muhursuz_urun_sorundur(teslim, tmp_path):
    """40-UYAP'ta mühürsüz = RED (o dizin yalnız bizim); kökte mühürsüz =
    ADVISORY (UYAP kaynak evrakı olabilir — yanlış-BLOK yasağı)."""
    kok = tmp_path
    _udf_kur(kok / "40-UYAP" / "muhursuz.udf")
    _udf_kur(kok / "kaynak-evrak.udf")   # karşı tarafın dilekçesi senaryosu
    sorunlar, uyarilar, kayitlar = teslim._filo_tazelik_denetimi(str(kok))
    assert any("muhursuz.udf" in s and "MÜHÜRSÜZ" in s for s in sorunlar)
    assert not any("kaynak-evrak" in s for s in sorunlar)
    assert any("kaynak-evrak" in u for u in uyarilar)


def test_filo_bayat_muhur_sorundur_taze_gecer(teslim, tmp_path):
    """K1 kilidi: bayat mühür RED-sınıfı sorun; taze mühür geçer ve
    kayıtlara K2 kapsamı (dosya+sha+durum) düşer."""
    kok = tmp_path
    taze = _udf_kur(kok / "taze.udf", b"<content>a</content>")
    _prov_yaz(taze, _sha(taze))
    bayat = _udf_kur(kok / "40-UYAP" / "bayat.udf", b"<content>b</content>")
    _prov_yaz(bayat, "f" * 64)   # yanlış sha = 307-K1
    sorunlar, uyarilar, kayitlar = teslim._filo_tazelik_denetimi(str(kok))
    assert any("bayat.udf" in s for s in sorunlar)
    assert not any("taze.udf" in s for s in sorunlar)
    durum = {k["dosya"]: k["muhur"] for k in kayitlar}
    assert durum[[d for d in durum if "taze" in d][0]] == "taze"
    assert durum[[d for d in durum if "bayat" in d][0]] == "bayat"
    assert all("sha12" in k for k in kayitlar)


def test_filo_imzali_turev_tolere(teslim, tmp_path):
    """E-imza baytları değiştirir: sign.sgn'li dosyada sha uyuşmazlığı
    BAYAT değil TÜREV'dir — sorun listesine girmez (B5b simetrisi)."""
    kok = tmp_path
    imzali = _udf_kur(kok / "imzali.udf", b"<content>c</content>", imzali=True)
    _prov_yaz(imzali, "a" * 64)
    sorunlar, uyarilar, kayitlar = teslim._filo_tazelik_denetimi(str(kok))
    assert not sorunlar
    assert kayitlar and kayitlar[0]["muhur"] == "turev"


# ────────────────────────── 4. SUNUM KİLİDİ GENİŞLEMESİ ──────────────────────────

def test_muhur_kirik_mi(pk, tmp_path):
    kok = tmp_path
    u = _udf_kur(kok / "a.udf", b"<content>a</content>")
    assert pk._muhur_kirik_mi(str(u)) is True          # mühürsüz = kırık
    _prov_yaz(u, _sha(u))
    assert pk._muhur_kirik_mi(str(u)) is False         # taze
    _udf_kur(kok / "a.udf", b"<content>DEGISTI</content>")
    assert pk._muhur_kirik_mi(str(kok / "a.udf")) is True   # bayat
    imzali = _udf_kur(kok / "b.udf", b"<content>b</content>", imzali=True)
    _prov_yaz(imzali, "9" * 64)
    assert pk._muhur_kirik_mi(str(imzali)) is False    # imzalı türev toleransı
    assert pk._muhur_kirik_mi(str(kok / "yok.pdf")) is False  # udf değil


def test_sunum_kilidi_yesil_makbuzda_bile_bayat_muhurde_ask(pk, tmp_path, monkeypatch):
    """307-K1 penceresinin kapanışı: yeşil makbuz VAR ama gönderilen ürünün
    mührü BAYAT (mühür var + sha uyuşmaz = makbuz-sonrası değişiklik) →
    kilit yine devreye girer. Mühürsüz dosya yeşil dalda SESSİZ (kaynak
    evrak olabilir — v0.5.9 davranışı korunur); taze mühür de sessiz."""
    kok = tmp_path
    defter = kok / "_oa" / "defter"
    defter.mkdir(parents=True)
    (defter / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 0}), encoding="utf-8")
    u = _udf_kur(kok / "urun.udf", b"<content>u</content>")
    monkeypatch.setattr(pk, "_sunum_teslim_sinifi_mi", lambda k, f: True)
    veri = {"tool_name": "SendUserFile",
            "tool_input": {"files": [str(u)]}}
    # mühürsüz + yeşil makbuz → sessiz (eski A1 davranışı; yanlış alarm yok)
    assert pk._sunum_kilidi_gerekli_mi(veri, str(kok)) is False
    # BAYAT mühür (307-K1'in birebir durumu) → ask
    _prov_yaz(u, "e" * 64)
    assert pk._sunum_kilidi_gerekli_mi(veri, str(kok)) is True
    # taze mühür → yine sessiz
    _prov_yaz(u, _sha(u))
    assert pk._sunum_kilidi_gerekli_mi(veri, str(kok)) is False
