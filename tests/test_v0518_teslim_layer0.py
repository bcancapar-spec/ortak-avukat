# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — teslim kapısı: UDF/udf-cli Layer 0'a DAHİL + sürüm sabitine bağ.

AVUKAT KARARI (2026-10-05): «udf-cli Layer 0'a DAHİL + sürüm sabitle».
NEDEN: `teslim_paketi.py` (c) gizlilik kapısını yalnız `--dis-arac` verilince
koşuyor, verilmezse «içerik dışarı çıkmıyor sayıldı» diyordu. Oysa UDF'i
üreten/okuyan tek yazıcı `npx udf-cli` AĞ + OTURUM kullanan bir dış araçtır;
dilekçe metninin sunucuya gidip gitmediği ölçülmedi → belirsizlikte
fail-closed (anayasa m.10: Layer 0 her dış-araç çağrısını sarar).

Sözleşme:
  - Teslim ürünü UDF (`--udf-yok` yok) + UDF yazıcısı udf-cli → Layer 0
    `--dis-arac` olmadan da ZORUNLU koşar; DENY/ASK → BLOK (teslim durur,
    UDF üretilmez); tetik makbuzda (`layer0_tetik`, (c) kaydında `tetik`).
  - `--udf-yok` (UDF'siz, dış araçsız) teslimde eski BİLGİ davranışı.
  - Yazıcı udf_yaz.py import EDİLMEDEN okunur; okunamazsa udf-cli varsayılır.
  - oa-kontrol'de `udf-cli@latest` kalmadı; sürüm udf_yaz.py sabitinden okunur.

AĞ YOK, GERÇEK npx YOK: sahte skills ağacında udf_yaz sahtesi sentetik UDF
yazar (udf-cli işaretli/işaretsiz iki biçim); gizlilik_tara GERÇEK kopyadır.
Tüm veriler SENTETİKTİR (anayasa m.7): sıfır dolgulu IBAN biçimi, tek haneli
tekrar dizisi — gerçek kişi/hesap değildir.
"""
import importlib.util
import json
import os
import pathlib
import re
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
GERCEK_GIZLILIK = SKILLS / "oa-gizlilik" / "scripts" / "gizlilik_tara.py"
GERCEK_UDF_YAZ = SKILLS / "oa-dilekce" / "scripts" / "udf_yaz.py"

SAHTE_GECER = "import sys\nprint('SAHTE-KAPI: OK')\nsys.exit(0)\n"

# Müvekkil verisi DESENİ (sentetik): sıfır dolgulu TR IBAN biçimi → gizlilik
# MUTLAK DENY; tekrar dizisi 11 hane (checksum tutmaz) → ASK.
IBAN_TASLAK = "Sentetik taslak.\nÖdeme hesabı: TR00 0000 0000 0000 0000 0000 00\n"
KIMLIK_TASLAK = "Sentetik taslak.\nKimlik: 11111111111\n"
TEMIZ_TASLAK = "Sentetik taslak metni.\n"

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


def _sahte_udf_yaz(udf_cli=True):
    """Sahte udf_yaz.py — CLI'da sentetik ama hafif-geçerli UDF yazar ve
    URETIM-IZI.txt düşer; ağa ÇIKMAZ. `udf_cli=True` biçimi gerçek yazıcının
    sütun-0 imzalarını taşır (`UDF_CLI_SURUM` / `UDF_CLI_PAKET` /
    `def npx_ile_udf_uret(`) ama npx'i ASLA çağırmaz. Şekil kapısının
    in-process kullandığı `_KENAR_PT` + `_sayfa_kenari_yonetmelik` gerçek
    udf_yaz.py'den delege edilir (v0584 test deseni)."""
    imza = ('UDF_CLI_SURUM = "9.9.9"\n'
            'UDF_CLI_PAKET = "udf-cli@" + UDF_CLI_SURUM\n'
            "def npx_ile_udf_uret(*a, **k):\n"
            "    raise RuntimeError('test: ag yok, npx cagrilmaz')\n") if udf_cli else ""
    return (
        "# -*- coding: utf-8 -*-\n"
        "import argparse, importlib.util, os, sys, zipfile\n"
        "_spec = importlib.util.spec_from_file_location('_gercek_udf_yaz_l0', %r)\n"
        "_g = importlib.util.module_from_spec(_spec)\n"
        "_spec.loader.exec_module(_g)\n"
        "_sayfa_kenari_yonetmelik = _g._sayfa_kenari_yonetmelik\n"
        "_KENAR_PT = _g._KENAR_PT\n"
        "%s"
        "_SABLON = %r\n"
        "_STIL = %r\n"
        "if __name__ == '__main__':\n"
        "    ap = argparse.ArgumentParser()\n"
        "    ap.add_argument('--girdi'); ap.add_argument('--cikti')\n"
        "    a, _b = ap.parse_known_args()\n"
        "    with zipfile.ZipFile(a.cikti, 'w', zipfile.ZIP_DEFLATED) as z:\n"
        "        z.writestr('content.xml', _SABLON.format(k='42.52', stil=_STIL))\n"
        "    with open(os.path.join(os.getcwd(), 'URETIM-IZI.txt'), 'a', encoding='utf-8') as f:\n"
        "        f.write(a.cikti + '\\n')\n"
        "    sys.exit(0)\n"
    ) % (str(GERCEK_UDF_YAZ), imza, _CONTENT_SABLON, _HVL_STIL)


@pytest.fixture
def ortam(tmp_path):
    """Sahte skills ağacı (gizlilik_tara GERÇEK kopya) + izole dava kökü."""
    skills = tmp_path / "skills"
    ok = skills / "oa-kontrol" / "scripts"
    od = skills / "oa-dilekce" / "scripts"
    og = skills / "oa-gizlilik" / "scripts"
    for d in (ok, od, og):
        d.mkdir(parents=True)
    shutil.copy2(str(GERCEK_TESLIM), str(ok / "teslim_paketi.py"))
    shutil.copy2(str(GERCEK_MUHUR), str(ok / "muhur_yaz.py"))
    shutil.copy2(str(GERCEK_TAZELIK), str(ok / "tazelik_denetim.py"))
    shutil.copy2(str(GERCEK_GIZLILIK), str(og / "gizlilik_tara.py"))
    (ok / "kunye_teyit.py").write_text(SAHTE_GECER, encoding="utf-8")
    (ok / "ictihat_muhakeme_denetim.py").write_text(SAHTE_GECER, encoding="utf-8")
    (od / "dilekce_denetim.py").write_text(SAHTE_GECER, encoding="utf-8")
    (od / "udf_yaz.py").write_text(_sahte_udf_yaz(udf_cli=True), encoding="utf-8")
    kok = tmp_path / "dava"
    kok.mkdir()
    return {"script": ok / "teslim_paketi.py", "kok": kok, "od": od, "og": og}


def _tp(ortam, metin, extra=()):
    taslak = ortam["kok"] / "taslak.md"
    taslak.write_text(metin, encoding="utf-8")
    env = dict(os.environ)
    env.pop("OA_SKILLS_KOK", None)   # determinizm: gerçek ağaca kaçış yok
    cp = subprocess.run(
        [sys.executable, str(ortam["script"]), str(taslak), "--tip", "genel",
         "--kok", str(ortam["kok"]), *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _makbuz(ortam, red=False):
    ad = "teslim-makbuz-RED.json" if red else "teslim-makbuz.json"
    return json.loads((ortam["kok"] / "_oa" / "defter" / ad).read_text(encoding="utf-8"))


def _kapi_c(makbuz):
    return [k for k in makbuz["kapilar"] if k["ad"].startswith("(c)")][0]


# ── UDF teslimi: Layer 0 ZORUNLU ────────────────────────────────────────────

@pytest.mark.parametrize("metin,beklenen_exit", [(IBAN_TASLAK, 2), (KIMLIK_TASLAK, 1)])
def test_udf_teslimde_layer0_zorunlu_muvekkil_deseni_blok(ortam, metin, beklenen_exit):
    kod, out = _tp(ortam, metin)
    assert kod == 1, out
    assert "[ZORUNLU]" in out and "udf-cli@9.9.9" in out, out
    assert "İLK KAPANAN KAPI: (c) GİZLİLİK / LAYER 0" in out, out
    # KATI ENGEL (avukat kararı): onay bayrağı yok — mesaj yerel yolu söyler
    assert "--udf-yok" in out and "UYAP editöründe" in out, out
    assert not (ortam["kok"] / "taslak.udf").exists()            # UDF ÜRETİLMEDİ
    assert not (ortam["kok"] / "URETIM-IZI.txt").exists()        # yazıcı çağrılmadı
    m = _makbuz(ortam, red=True)
    c = _kapi_c(m)
    assert m["layer0_tetik"] == "udf-cli"
    assert (c["durum"], c["exit"], c["tetik"]) == ("BLOK", beklenen_exit, "udf-cli")


def test_udf_teslimde_temiz_taslak_layer0_acik_teslim_tamam(ortam):
    kod, out = _tp(ortam, TEMIZ_TASLAK)
    assert kod == 0, out
    assert (ortam["kok"] / "taslak.udf").is_file()
    m = _makbuz(ortam)
    c = _kapi_c(m)
    assert m["layer0_tetik"] == "udf-cli" and c["durum"] == "OK" and c["tetik"] == "udf-cli"


def test_devralinan_udf_de_layer0_dan_gecer(ortam):
    """Mevcut geçerli .udf devralınacak olsa bile tarama ÖNCE koşar."""
    with zipfile.ZipFile(str(ortam["kok"] / "taslak.udf"), "w") as z:
        z.writestr("content.xml", _CONTENT_SABLON.format(k="42.52", stil=_HVL_STIL))
    kod, out = _tp(ortam, IBAN_TASLAK)
    assert kod == 1 and "DEVRALINDI" not in out, out
    assert _kapi_c(_makbuz(ortam, red=True))["durum"] == "BLOK"


# ── geriye uyum: UDF'siz teslim değişmez ────────────────────────────────────

def test_udf_yok_teslimde_eski_bilgi_davranisi(ortam):
    kod, out = _tp(ortam, IBAN_TASLAK, ["--udf-yok"])
    assert kod == 0, out
    assert "Layer 0 taraması ATLANDI" in out and "[ZORUNLU]" not in out
    m = _makbuz(ortam)
    assert m["layer0_tetik"] is None
    c = _kapi_c(m)
    assert c["durum"] == "BILGI" and "tetik" not in c


def test_dis_arac_bayragi_udfsiz_de_tarar_tetik_gorunur(ortam):
    kod, out = _tp(ortam, IBAN_TASLAK, ["--udf-yok", "--dis-arac"])
    assert kod == 1, out
    assert _makbuz(ortam, red=True)["layer0_tetik"] == "dis-arac"


# ── mekanik tespit + fail-closed ────────────────────────────────────────────

def test_yazici_udf_cli_degilse_zorunlu_tarama_yok(ortam):
    """Tespit MEKANİKTİR: yazıcı udf-cli imzası taşımıyorsa (yerel/sahte
    yazıcı) dış araç çağrısı yoktur — eski davranış sürer."""
    (ortam["od"] / "udf_yaz.py").write_text(_sahte_udf_yaz(udf_cli=False), encoding="utf-8")
    kod, out = _tp(ortam, IBAN_TASLAK)
    assert kod == 0, out
    assert _makbuz(ortam)["layer0_tetik"] is None


def test_yazici_okunamazsa_udf_cli_varsayilir_ve_latest_basilmaz(ortam):
    (ortam["od"] / "udf_yaz.py").unlink()
    kod, out = _tp(ortam, TEMIZ_TASLAK)
    assert kod == 1, out                       # üretim adımı: yazıcı yok → BLOK
    m = _makbuz(ortam, red=True)
    assert m["layer0_tetik"] == "udf-cli" and _kapi_c(m)["durum"] == "OK"
    assert "udf-cli@<udf_yaz.py UDF_CLI_SURUM>" in out and "udf-cli@latest" not in out


def test_gizlilik_scripti_yoksa_udf_teslimde_failclosed(ortam):
    (ortam["og"] / "gizlilik_tara.py").unlink()
    kod, out = _tp(ortam, TEMIZ_TASLAK)
    assert kod == 1, out
    c = _kapi_c(_makbuz(ortam, red=True))
    assert c["durum"] == "ATLA" and c["tetik"] == "udf-cli"


# ── sürüm sabiti: @latest yok, sürüm udf_yaz.py'den (import'suz) ───────────

def test_oa_kontrolde_udf_cli_latest_kalmadi():
    kalan = []
    for yol in (SKILLS / "oa-kontrol").rglob("*"):
        if yol.suffix in (".py", ".md") and yol.is_file():
            if "udf-cli@latest" in yol.read_text(encoding="utf-8", errors="replace"):
                kalan.append(str(yol.relative_to(REPO)))
    assert not kalan, kalan


def test_surum_udf_yaz_sabitinden_import_etmeden_okunur():
    spec = importlib.util.spec_from_file_location("v0518_l0_tp", GERCEK_TESLIM)
    tp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tp)
    beklenen = None
    for satir in GERCEK_UDF_YAZ.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^UDF_CLI_SURUM = "(\d+\.\d+\.\d+)"$', satir)
        if m:
            beklenen = m.group(1)
    assert beklenen, "udf_yaz.py'de sabitlenmiş UDF_CLI_SURUM satırı yok"
    assert tp._udf_cli_surumu() == beklenen
    assert tp._udf_cli_paket_metni() == "udf-cli@" + beklenen
    assert tp._udf_yazici_udf_cli_mi() is True        # gerçek yazıcı udf-cli'dir


def test_skill_ve_gunluk_kurali_anlatir():
    skill = (SKILLS / "oa-kontrol" / "SKILL.md").read_text(encoding="utf-8")
    gunluk = (SKILLS / "oa-kontrol" / "references" / "degisiklik-gunlugu.md").read_text(
        encoding="utf-8")
    assert "Layer 0 bayraksız da ZORUNLU" in skill and "layer0_tetik" in skill
    assert "udf-cli Layer 0'a DAHİL" in gunluk and "UDF_CLI_SURUM" in gunluk
    # avukat kararı + ölçüm (sayılarla, dosya adı/içerik olmadan)
    assert "KATI ENGEL" in skill and "KATI ENGEL" in gunluk
    assert "911" in gunluk and "908" in gunluk and "HMK m.119/1-c" in gunluk


# ── --taraf icra tarafları (v0.5.18) ────────────────────────────────────────

def _taraf_secenekleri(yol):
    """Kaynaktaki `add_argument("--taraf", ... choices=[...])` listesi (import yok)."""
    import ast as _ast
    kaynak = pathlib.Path(yol).read_text(encoding="utf-8")
    m = re.search(r'add_argument\(\s*"--taraf".*?choices=(\[.*?\])', kaynak, re.S)
    assert m, yol
    return set(_ast.literal_eval(m.group(1)))


def test_taraf_listesi_dilekce_denetimin_alt_kumesi_ve_icra_taraflarini_tasir():
    zincir = _taraf_secenekleri(GERCEK_TESLIM)
    dilekce = _taraf_secenekleri(SKILLS / "oa-dilekce" / "scripts" / "dilekce_denetim.py")
    assert zincir <= dilekce, sorted(zincir - dilekce)   # (a)'ya geçen değer reddedilmez
    assert {"alacakli", "borclu", "ucuncu-kisi", "musteki"} <= zincir


def test_dilekce_belgeleri_zincirin_icra_sifatlarini_tanidigini_soyler():
    """Bütünlük (2026-10-07, Fable 5.1 revizyonunun bulgusu): oa-dilekce SKILL.md ve icra
    rehberi, teslim zincirinin icra sıfatlarını "henüz tanımadığını" yazıp alacaklıya
    `--taraf davaci` vermeyi öğütlüyordu. Zincir v0.5.18'de bu sıfatları kabul ediyor; bayat
    yönerge icraya özgü müvekkil-aleyhi kalıplarını (a) kapısında devre dışı bırakırdı."""
    zincir = _taraf_secenekleri(GERCEK_TESLIM)
    icra = {"alacakli", "borclu", "ucuncu-kisi"}
    assert icra <= zincir
    for yol in (SKILLS / "oa-dilekce" / "SKILL.md",
                SKILLS / "oa-dilekce" / "references" / "icra-dilekce-ailesi.md"):
        metin = yol.read_text(encoding="utf-8")
        assert "henüz tanım" not in metin, "%s: bayat 'henüz tanımıyor' yönergesi" % yol.name
        assert not re.search(r"alacaklı için\s*`(?:--taraf )?davaci`", metin), yol.name
        assert "teslim_paketi.py --taraf alacakli" in metin, (
            "%s: teslim zincirinin icra sıfatıyla nasıl koşulacağı yazılı değil" % yol.name)


def test_icra_tarafi_a_kapisina_aynen_gecer_ve_makbuza_yazilir(ortam):
    (ortam["od"] / "dilekce_denetim.py").write_text(
        "import sys\nopen('DILEKCE-ARGV.txt', 'w', encoding='utf-8').write("
        "' '.join(sys.argv[1:]))\nsys.exit(0)\n", encoding="utf-8")
    kod, out = _tp(ortam, TEMIZ_TASLAK, ["--taraf", "alacakli", "--udf-yok"])
    assert kod == 0, out
    argv = (ortam["kok"] / "DILEKCE-ARGV.txt").read_text(encoding="utf-8")
    assert "--taraf alacakli" in argv
    assert _makbuz(ortam)["taraf"] == "alacakli"


def test_onay_bayragi_yok_kati_engel():
    """Avukat kararı: UDF Layer 0 için zincirde onay/aşma bayrağı YOKTUR."""
    cp = subprocess.run([sys.executable, str(GERCEK_TESLIM), "--help"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0
    assert "--udf-yok" in cp.stdout and "onay" not in cp.stdout.lower()
