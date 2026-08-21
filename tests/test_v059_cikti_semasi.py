# -*- coding: utf-8 -*-
"""v0.5.9 — ÇIKTI ŞEMASI paketi (40-UYAP dış-çıktı dizini, A2 kurucusu).

Kapsam (Can kararları):
  1) YEŞİL YOL: yeşil makbuz → 40-UYAP/ doğar + ürün KOPYASI (asıl yerinde,
     sha EŞİT — tek-nüsha ilkesi) + `_damga` alanlı teslim-makbuz-KOPYA.json
     + makbuzda `uyap_kopya` alanı.
  2) PDF eşlik: UDF'in yanındaki aynı kök-adlı .pdf de kopyalanır.
  3) RED YOL: kapı kapanınca 40-UYAP DOĞMAZ.
  4) KOPYA HATASI advisory: 40-UYAP kurulamazsa (adı çakışan DOSYA) teslim
     exit'i DEĞİŞMEZ (0 kalır) + görünür uyarı + makbuzda uyap_kopya=None.
  5) REGRESYON: mevcut makbuz şeması alanları aynen korunur.

TEST MİMARİSİ: test_v0584_teslim_paketi.py'nin sahte-skills ağacı birebir —
engelleyici kapılar hep-geçer sahtelerle, udf_yaz sentetik-ama-hafif-geçerli
UDF üreten sahteyle değiştirilir; ağ/oturum (npx udf-cli) GEREKMEZ. Tüm veriler
sentetiktir (tmp_path — gizlilik m.7).
"""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
GERCEK_TESLIM = SKILLS / "oa-kontrol" / "scripts" / "teslim_paketi.py"
GERCEK_MUHUR = SKILLS / "oa-kontrol" / "scripts" / "muhur_yaz.py"
GERCEK_TAZELIK = SKILLS / "oa-kontrol" / "scripts" / "tazelik_denetim.py"
GERCEK_UDF_YAZ = SKILLS / "oa-dilekce" / "scripts" / "udf_yaz.py"

SAHTE_GECER = "import sys\nprint('SAHTE-KAPI: OK')\nsys.exit(0)\n"
SAHTE_BLOK = "import sys\nprint('SAHTE-KAPI: BLOK')\nsys.exit(1)\n"
# udf_yaz sahtesi __main__ GUARD'lı olmak ZORUNDA: teslim_paketi şekil kapısı
# onu İN-PROCESS import eder (guard'sız sys.exit importta zinciri keserdi).
SAHTE_UDF_YAZ = ("_KENAR_PT = '42.52'\n"
                 "if __name__ == '__main__':\n"
                 "    import sys\n"
                 "    print('SAHTE-URETIM: kullanilmamali (testler devralma yolunda)')\n"
                 "    sys.exit(1)\n")

_HVL_STIL = '<style name="hvl-default" parent="default" description="hvl"/>'
_CONTENT_SABLON = """<?xml version="1.0" encoding="UTF-8"?>
<template format_id="1.8">
<content><![CDATA[Sentetik dilekce metni.]]></content>
<properties>
<pageFormat mediaSizeName="1" leftMargin="{k}" rightMargin="{k}" topMargin="{k}" bottomMargin="{k}" paperOrientation="1" headerFOffset="20.0" footerFOffset="20.0"/>
</properties>
<elements resolver="hvl-default">
<paragraph LineSpacing="0.50" FirstLineIndent="24"><content startOffset="0" length="23"/></paragraph>
</elements>
<styles>
<style name="default" description="varsayilan"/>
{stil}
</styles>
</template>
"""


def _sentetik_udf(yol, kenar="42.52"):
    xml = _CONTENT_SABLON.format(k=kenar, stil=_HVL_STIL)
    with zipfile.ZipFile(str(yol), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.xml", xml)


def _sha256(yol):
    h = hashlib.sha256()
    with open(str(yol), "rb") as f:
        for parca in iter(lambda: f.read(1 << 16), b""):
            h.update(parca)
    return h.hexdigest()


@pytest.fixture
def ortam(tmp_path):
    """Sahte skills ağacı + izole dava kökü + sentetik taslak
    (test_v0584_teslim_paketi.py mimarisi; üretim yolu gerekmediği için
    udf_yaz sahtesi de hep-geçerdir ama testler devralma yolunu kullanır)."""
    skills = tmp_path / "skills"
    ok = skills / "oa-kontrol" / "scripts"
    od = skills / "oa-dilekce" / "scripts"
    ok.mkdir(parents=True)
    od.mkdir(parents=True)
    shutil.copy2(str(GERCEK_TESLIM), str(ok / "teslim_paketi.py"))
    shutil.copy2(str(GERCEK_MUHUR), str(ok / "muhur_yaz.py"))
    shutil.copy2(str(GERCEK_TAZELIK), str(ok / "tazelik_denetim.py"))
    (ok / "kunye_teyit.py").write_text(SAHTE_GECER, encoding="utf-8")
    (ok / "ictihat_muhakeme_denetim.py").write_text(SAHTE_GECER, encoding="utf-8")
    (od / "dilekce_denetim.py").write_text(SAHTE_GECER, encoding="utf-8")
    (od / "udf_yaz.py").write_text(SAHTE_UDF_YAZ, encoding="utf-8")
    kok = tmp_path / "dava"
    kok.mkdir()
    taslak = kok / "taslak.md"
    taslak.write_text("Sentetik taslak metni.\n", encoding="utf-8")
    return {"skills": skills, "script": ok / "teslim_paketi.py",
            "kok": kok, "taslak": taslak}


def _tp(ortam, extra=()):
    env = dict(os.environ)
    env.pop("OA_SKILLS_KOK", None)  # determinizm: fallback gerçek ağaca kaçmasın
    cp = subprocess.run(
        [sys.executable, str(ortam["script"]), str(ortam["taslak"]),
         "--tip", "genel", "--kok", str(ortam["kok"]), *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _makbuz(ortam, red=False):
    ad = "teslim-makbuz-RED.json" if red else "teslim-makbuz.json"
    yol = ortam["kok"] / "_oa" / "defter" / ad
    assert yol.is_file(), "makbuz bulunamadı: %s" % yol
    return json.loads(yol.read_text(encoding="utf-8"))


# ── 1) YEŞİL YOL — 40-UYAP doğar, kopya + damga + makbuz alanı ─────────────

def test_yesil_yol_40_uyap_dogar_urun_kopyalanir_asil_yerinde(ortam):
    """Yeşil makbuz → 40-UYAP/ doğar; UDF KOPYALANIR (taşınmaz): asıl yerinde
    kalır ve sha'lar EŞİTTİR (tek-nüsha ilkesi)."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    uyap = ortam["kok"] / "40-UYAP"
    assert uyap.is_dir(), "yeşil makbuz sonrası 40-UYAP doğmalıydı:\n%s" % cikti
    kopya = uyap / "taslak.udf"
    assert kopya.is_file(), "UDF kopyası 40-UYAP'ta olmalıydı"
    assert aday.is_file(), "asıl UDF yerinden OYNAMAMALIYDI (kopya, taşıma değil)"
    assert _sha256(kopya) == _sha256(aday), "kopya ile asıl bayt-eş olmalı"


def test_yesil_yol_makbuz_kopyasi_damgali_ve_asil_makbuzda_alan(ortam):
    """40-UYAP/teslim-makbuz-KOPYA.json: `_damga` alanı taşır; asıl makbuzda
    `uyap_kopya` (köke-göreli yol) + `uyap_urun_kopyalari` alanları vardır."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    kopya_yolu = ortam["kok"] / "40-UYAP" / "teslim-makbuz-KOPYA.json"
    assert kopya_yolu.is_file(), "damgalı makbuz-kopyası yazılmalıydı:\n%s" % cikti
    kopya = json.loads(kopya_yolu.read_text(encoding="utf-8"))
    assert kopya["_damga"] == "KOPYA — asil: _oa/defter/teslim-makbuz.json"
    assert kopya["exit_kodu"] == 0

    m = _makbuz(ortam)
    assert m["uyap_kopya"] == "40-UYAP/teslim-makbuz-KOPYA.json"
    assert m["uyap_urun_kopyalari"] == ["40-UYAP/taslak.udf"]
    # asıl makbuz damga TAŞIMAZ (damga yalnız kopyanın kimliğidir)
    assert "_damga" not in m


# ── 2) PDF eşlik — aynı kök-adlı PDF de kopyalanır ─────────────────────────

def test_ayni_kok_adli_pdf_de_kopyalanir(ortam):
    """UDF'in yanındaki aynı kök-adlı .pdf de nihai teslim ürünü sayılır ve
    40-UYAP'a kopyalanır (asıl yerinde kalır)."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)
    pdf = ortam["kok"] / "taslak.pdf"
    pdf.write_bytes(b"%PDF-1.4 sentetik")

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    assert (ortam["kok"] / "40-UYAP" / "taslak.pdf").is_file()
    assert pdf.is_file(), "asıl PDF yerinde kalmalı"
    m = _makbuz(ortam)
    assert set(m["uyap_urun_kopyalari"]) == {"40-UYAP/taslak.udf",
                                             "40-UYAP/taslak.pdf"}


# ── 3) RED YOL — 40-UYAP doğmaz ────────────────────────────────────────────

def test_red_yolunda_40_uyap_dogmaz(ortam):
    """Bir kapı kapanırsa (RED makbuzu) 40-UYAP ÜRETİLMEZ — dışa çıkacak
    doğrulanmış ürün yoktur."""
    # (b) künye kapısını bloklayan sahte
    (ortam["skills"] / "oa-kontrol" / "scripts" / "kunye_teyit.py").write_text(
        SAHTE_BLOK, encoding="utf-8")
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)

    kod, cikti = _tp(ortam)

    assert kod != 0, cikti
    assert not (ortam["kok"] / "40-UYAP").exists(), (
        "RED yolunda 40-UYAP doğmamalıydı:\n%s" % cikti)
    m = _makbuz(ortam, red=True)
    assert "uyap_kopya" not in m, "RED makbuzu uyap_kopya alanı taşımaz"


# ── 4) KOPYA HATASI — advisory: exit değişmez + görünür uyarı ──────────────

def test_kopya_hatasi_teslimi_kirmaz_gorunur_uyari(ortam):
    """40-UYAP kurulamazsa (kökte adı çakışan DOSYA → os.makedirs hatası)
    teslim exit'i 0 KALIR, görünür uyarı basılır, makbuzda uyap_kopya=None
    (advisory doğuş — kopyalama hatası teslimi KIRMAZ)."""
    (ortam["kok"] / "40-UYAP").write_text("dizin degil DOSYA", encoding="utf-8")
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)

    kod, cikti = _tp(ortam)

    assert kod == 0, "kopya hatası teslimi KIRMAMALIYDI:\n%s" % cikti
    assert "TESLİME HAZIR" in cikti
    assert "KURULAMADI" in cikti, "görünür uyarı basılmalıydı:\n%s" % cikti
    m = _makbuz(ortam)
    assert m["uyap_kopya"] is None
    assert m["uyap_urun_kopyalari"] == []


# ── 4b) TARAYICI-DIŞLAMA SÖZLEŞMESİ — 40-UYAP gelen evrak DEĞİLDİR ─────────

def test_ham_evrak_tarayicilari_40_uyap_atlar():
    """`oa_ingest.py` / `tam_tur.py` / `manifest_olustur.py` ortak ATLA_DIZIN
    kümesi `40-uyap`ı (küçük-harf karşılaştırma) İÇERMELİ — aksi hâlde kurucu
    yeşil teslimden hemen sonra kendi kopyasıyla KUNYE BAYAT üretir
    (öz-bulaşma; doktrin: cikti-semasi.md §2)."""
    import importlib.util
    for skill, ad in (("oa-ingest", "oa_ingest.py"),
                      ("oa-pipeline", "tam_tur.py"),
                      ("oa-pipeline", "manifest_olustur.py")):
        betik = SKILLS / skill / "scripts" / ad
        spec = importlib.util.spec_from_file_location("_t40_" + ad[:-3], str(betik))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert "40-uyap" in mod.ATLA_DIZIN, "%s ATLA_DIZIN 40-uyap içermeli" % ad


# ── 5) REGRESYON — mevcut makbuz şeması aynen korunur ──────────────────────

def test_makbuz_eski_sema_alanlari_regresyonsuz(ortam):
    """v0.5.8.4/v0.5.8.5 makbuz alanları yeni uyap alanlarıyla BİRLİKTE aynen
    durur; kapı ENUM'u değişmedi."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)
    kod, cikti = _tp(ortam)
    assert kod == 0, cikti
    m = _makbuz(ortam)
    for alan in ("zaman", "taslak_yol", "taslak_sha256", "tip", "taraf",
                 "kapilar", "exit_kodu", "udf_yolu", "udf_atlandi_istekle",
                 "ictihat_muhakeme_kanali", "surum", "durdu", "argv",
                 "udf_devralindi", "kenar_duzeltildi", "sekil_imzali_sapma",
                 "tazelik_uyarilari", "uyap_kopya", "uyap_urun_kopyalari"):
        assert alan in m, "makbuzda alan eksik: %s" % alan
    for k in m["kapilar"]:
        assert k["durum"] in ("OK", "BLOK", "ATLA", "BILGI")
