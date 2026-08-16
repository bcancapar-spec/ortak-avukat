# -*- coding: utf-8 -*-
"""v0.5.8.5 dalgası — B4 (advisory tamamlanma) + B5a/B5b (e-imza mühür halkası).

Kapsam:
  B4  — İLK-ENGELDE-DUR exit davranışı DEĞİŞMEDEN, engelleyici kapı kapandığında
        engelleyici-OLMAYAN denetimler yine de koşulur ve RED makbuzu
        `advisory_denetimler` alanı kazanır: şekil (pageFormat 4x42.52 +
        LineSpacing istişari), prov-tazelik (yan .prov.json sha karşılaştırma),
        yerel-damga taraması, devralma-aday raporu, tazelik advisory.
        (Saha kanıtı: künye BLOK'u kenar ihlalini görünmez bıraktı; UDF
        yönetmelik-dışı kenarla teslim edildi.)
  B5a — muhur_yaz.py: sign.sgn tespiti (`sign_sgn_var_mi`) + "e-imzali-nusha"
        tipiyle mühür üretimi (`e_imza_muhur_uret`, was_derived_from =
        imza-öncesi sha) + --tasi uyumu.
  B5b — teslim_paketi.py: teslim-sınıfı UDF'de sign.sgn görülürse sha
        uyuşmazlığı BAYAT değil TÜREV'dir; was_derived_from zinciri kurulmuşsa
        YEŞİL, kurulmamışsa "imzalı türev mühürsüz" uyarısı + best-effort
        e-imzali-nusha mührü (istisna defterine dogrulama-toleransi satırı).

TEST MİMARİSİ: test_v0584_teslim_paketi.py'nin sahte-skills ağacı deseni —
gerçek teslim_paketi/muhur_yaz/tazelik_denetim kopyalanır, engelleyici kapılar
sahtelerle değiştirilir. Tüm veriler SENTETİKTİR (tmp_path — gizlilik m.7).
"""
import hashlib
import importlib.util
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
SAHTE_BLOK = "import sys\nprint('SAHTE-KAPI: BLOK — sentetik engel')\nsys.exit(1)\n"

_HVL_STIL = '<style name="hvl-default" parent="default" description="hvl"/>'
_CONTENT_SABLON = """<?xml version="1.0" encoding="UTF-8"?>
<template format_id="1.8">
<content><![CDATA[Sentetik dilekce metni.]]></content>
<properties>
<pageFormat mediaSizeName="1" leftMargin="{k}" rightMargin="{k}" topMargin="{k}" bottomMargin="{k}" paperOrientation="1" headerFOffset="20.0" footerFOffset="20.0"/>
</properties>
<elements resolver="hvl-default">
<paragraph LineSpacing="{ls}" FirstLineIndent="24"><content startOffset="0" length="23"/></paragraph>
</elements>
<styles>
<style name="default" description="varsayilan"/>
{stil}
</styles>
</template>
"""


def _sentetik_udf(yol, hvl=True, kenar="42.52", ls="0.50", imzali=False):
    """Sentetik .udf: zip + content.xml (+ imzali=True ise sign.sgn girdisi —
    UYAP e-imza nüshasının sentetik taklidi)."""
    xml = _CONTENT_SABLON.format(k=kenar, ls=ls, stil=(_HVL_STIL if hvl else ""))
    with zipfile.ZipFile(str(yol), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.xml", xml)
        if imzali:
            z.writestr("sign.sgn", b"SENTETIK-E-IMZA-BLOBU")


def _sha256(yol):
    h = hashlib.sha256()
    with open(str(yol), "rb") as f:
        for parca in iter(lambda: f.read(1 << 16), b""):
            h.update(parca)
    return h.hexdigest()


def _sahte_udf_yaz_kaynak():
    """Sahte udf_yaz.py — _KENAR_PT + _sayfa_kenari_yonetmelik GERÇEK
    udf_yaz.py'den delege (v0584 test deseniyle aynı)."""
    return (
        "# -*- coding: utf-8 -*-\n"
        "import argparse, importlib.util, os, sys, zipfile\n"
        "_spec = importlib.util.spec_from_file_location('_gercek_udf_yaz', %r)\n"
        "_g = importlib.util.module_from_spec(_spec)\n"
        "_spec.loader.exec_module(_g)\n"
        "_sayfa_kenari_yonetmelik = _g._sayfa_kenari_yonetmelik\n"
        "_KENAR_PT = _g._KENAR_PT\n"
        "_SABLON = %r\n"
        "_STIL = %r\n"
        "if __name__ == '__main__':\n"
        "    ap = argparse.ArgumentParser()\n"
        "    ap.add_argument('--girdi'); ap.add_argument('--cikti')\n"
        "    a, _bilinmeyen = ap.parse_known_args()\n"
        "    xml = _SABLON.format(k='42.52', ls='0.50', stil=_STIL)\n"
        "    with zipfile.ZipFile(a.cikti, 'w', zipfile.ZIP_DEFLATED) as z:\n"
        "        z.writestr('content.xml', xml)\n"
        "    print('SAHTE-URETIM: ' + a.cikti)\n"
        "    sys.exit(0)\n"
    ) % (str(GERCEK_UDF_YAZ), _CONTENT_SABLON, _HVL_STIL)


@pytest.fixture
def ortam(tmp_path):
    """Sahte skills ağacı + izole dava kökü + sentetik taslak."""
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
    (od / "udf_yaz.py").write_text(_sahte_udf_yaz_kaynak(), encoding="utf-8")
    kok = tmp_path / "dava"
    kok.mkdir()
    taslak = kok / "taslak.md"
    taslak.write_text("Sentetik taslak metni — 2024/123 Esas (uydurma).\n",
                      encoding="utf-8")
    return {"skills": skills, "script": ok / "teslim_paketi.py",
            "kok": kok, "taslak": taslak,
            "dilekce_denetim": od / "dilekce_denetim.py"}


def _tp(ortam, extra=(), taslak=None):
    env = dict(os.environ)
    env.pop("OA_SKILLS_KOK", None)  # determinizm: fallback gerçek ağaca kaçmasın
    hedef = str(taslak if taslak is not None else ortam["taslak"])
    cp = subprocess.run(
        [sys.executable, str(ortam["script"]), hedef,
         "--tip", "genel", "--kok", str(ortam["kok"]), *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _makbuz(ortam, red=False):
    ad = "teslim-makbuz-RED.json" if red else "teslim-makbuz.json"
    yol = ortam["kok"] / "_oa" / "defter" / ad
    assert yol.is_file(), "makbuz bulunamadı: %s" % yol
    return json.loads(yol.read_text(encoding="utf-8"))


def _muhur_modulu():
    """Gerçek muhur_yaz.py in-process (B5a fonksiyon-düzeyi sınama)."""
    spec = importlib.util.spec_from_file_location("_test_v0585_muhur", str(GERCEK_MUHUR))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _muhur_cli(*arglar):
    cp = subprocess.run([sys.executable, str(GERCEK_MUHUR), *arglar],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace")
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# ── B4 — RED MAKBUZUNDA ADVISORY DENETİMLER ────────────────────────────────

def test_red_makbuzda_advisory_denetimler_dolu(ortam):
    """Engelleyici kapı (a) kapanınca zincir yine İLK ENGELDE DURUR (exit
    davranışı değişmez) AMA advisory denetimler koşulur: kenar ihlali, bayat
    mühür, yerel damga ve devralma adayı RED makbuzunda GÖRÜNÜR."""
    ortam["dilekce_denetim"].write_text(SAHTE_BLOK, encoding="utf-8")
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday, kenar="70.87")  # yönetmelik-dışı kenar (372 kanıtı)
    eski_sha = _sha256(aday)
    (ortam["kok"] / "taslak.udf.prov.json").write_text(json.dumps({
        "prov_schema": "oa-muhur/1.0",
        "artifact_sha256": "0" * 64,  # bayat
        "was_generated_by": "udf_yaz --yerel-motor v1.1",  # yerel damga
    }, ensure_ascii=False), encoding="utf-8")

    kod, cikti = _tp(ortam)

    # exit davranışı DEĞİŞMEDİ: ilk engelde dur + sonraki kapılar koşmadı
    assert kod != 0, cikti
    assert "İLK KAPANAN KAPI" in cikti
    assert "SONRAKİ KAPILAR ÇALIŞTIRILMADI" in cikti

    m = _makbuz(ortam, red=True)
    adv = m.get("advisory_denetimler")
    assert adv is not None, "RED makbuzunda advisory_denetimler alanı yok"
    # devralma-aday raporu: hangi UDF adayı bulunurdu
    assert adv["devralma_adaylari"], "aday raporu boş olmamalıydı"
    assert adv["devralma_adaylari"][0]["yol"].endswith("taslak.udf")
    assert adv["devralma_adaylari"][0]["hafif_gecerli"] is True
    # şekil: kenar ihlali artık GÖRÜNÜR (372: künye BLOK'u görünmez bırakmıştı)
    assert adv["sekil"] is not None
    assert adv["sekil"]["kenarlar_uygun"] is False
    assert adv["sekil"]["kenar_pt"] == "42.52"
    # prov-tazelik: yan .prov.json sha karşılaştırması
    assert adv["prov_tazelik"] is not None
    assert adv["prov_tazelik"]["muhur_var"] is True
    assert adv["prov_tazelik"]["taze"] is False
    # yerel-damga taraması
    assert adv["yerel_damga"] is not None
    assert adv["yerel_damga"]["yerel"] is True
    # tazelik advisory alanı şemada mevcut (liste ya da None — asla KeyError)
    assert "tazelik_uyarilari" in adv


def test_advisory_yan_etkisiz_aday_dokunulmaz(ortam):
    """Advisory KAPI DEĞİLDİR: aday .udf karantinaya TAŞINMAZ, kenar
    YAMALANMAZ — dosya baytları aynen kalır (yalnız rapor)."""
    ortam["dilekce_denetim"].write_text(SAHTE_BLOK, encoding="utf-8")
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday, kenar="70.87")
    eski_sha = _sha256(aday)

    kod, cikti = _tp(ortam)

    assert kod != 0
    assert aday.is_file(), "advisory aday dosyasını taşımamalıydı"
    assert _sha256(aday) == eski_sha, "advisory aday dosyasına yazmamalıydı"
    assert not (ortam["kok"] / "_oa" / "arsiv-yerel").exists(), (
        "advisory karantina klasörü açmamalıydı")


def test_advisory_aday_yokken_sema_yine_mevcut(ortam):
    """Aday .udf hiç yokken de RED makbuzu advisory_denetimler alanını taşır
    (boş rapor; sekil/prov None) — şema koşula bağlı kaybolmaz."""
    ortam["dilekce_denetim"].write_text(SAHTE_BLOK, encoding="utf-8")

    kod, _cikti = _tp(ortam)

    assert kod != 0
    m = _makbuz(ortam, red=True)
    adv = m.get("advisory_denetimler")
    assert adv is not None
    assert adv["devralma_adaylari"] == []
    assert adv["sekil"] is None
    assert adv["prov_tazelik"] is None
    assert adv["yerel_damga"] is None


# ── B5a — muhur_yaz: sign.sgn tespiti + e-imzali-nusha mührü ───────────────

def test_sign_sgn_tespiti_sentetik_zip(tmp_path):
    """sign.sgn'li sentetik zip → True; imzasız zip → False; zip olmayan
    dosya → False (tespit engel değildir, fırlatmaz)."""
    mm = _muhur_modulu()
    imzali = tmp_path / "imzali.udf"
    _sentetik_udf(imzali, imzali=True)
    imzasiz = tmp_path / "imzasiz.udf"
    _sentetik_udf(imzasiz)
    duz = tmp_path / "duz.bin"
    duz.write_bytes(b"zip degil")

    assert mm.sign_sgn_var_mi(str(imzali)) is True
    assert mm.sign_sgn_var_mi(str(imzasiz)) is False
    assert mm.sign_sgn_var_mi(str(duz)) is False


def test_e_imzali_nusha_muhru_was_derived_from_ile(tmp_path):
    """e_imza_muhur_uret: entity_type='e-imzali-nusha', was_derived_from =
    imza-öncesi sha parametresi; mühür imzalı dosyanın GÜNCEL sha'sına basılır."""
    mm = _muhur_modulu()
    urun = tmp_path / "dilekce-imzali.udf"
    _sentetik_udf(urun, imzali=True)
    imza_oncesi = "a" * 64

    kayit = mm.e_imza_muhur_uret(str(tmp_path), str(urun), imza_oncesi)
    yol, hata = mm.muhur_yaz(str(tmp_path), str(urun), kayit)

    assert hata is None
    kayit2 = json.loads((tmp_path / "dilekce-imzali.udf.prov.json")
                        .read_text(encoding="utf-8"))
    assert kayit2["entity_type"] == "e-imzali-nusha"
    assert kayit2["was_derived_from"] == imza_oncesi
    assert kayit2["artifact_sha256"] == _sha256(urun)


def test_e_imza_cli_otomatik_tip_ve_tasi_uyumu(tmp_path):
    """CLI: sign.sgn'li ürün + varsayılan tip → otomatik 'e-imzali-nusha'
    (--onceki was_derived_from'a geçer); üretilen mühür --tasi ile taşınır ve
    yeni konumda --dogrula geçer (B5a: --tasi ile uyumlu)."""
    urun = tmp_path / "imzali.udf"
    _sentetik_udf(urun, imzali=True)
    imza_oncesi = "b" * 64
    kod, out = _muhur_cli("--kok", str(tmp_path), "--urun", str(urun),
                          "--onceki", imza_oncesi)
    assert kod == 0, out
    kayit = json.loads((tmp_path / "imzali.udf.prov.json").read_text(encoding="utf-8"))
    assert kayit["entity_type"] == "e-imzali-nusha"
    assert kayit["was_derived_from"] == imza_oncesi

    arsiv = tmp_path / "arsiv"
    arsiv.mkdir()
    yeni = arsiv / "imzali.udf"
    kod, out = _muhur_cli("--kok", str(tmp_path), "--tasi", str(urun), str(yeni))
    assert kod == 0, out
    kod, out = _muhur_cli("--kok", str(tmp_path), "--dogrula", str(yeni))
    assert kod == 0 and "uyumlu" in out
    yeni_kayit = json.loads((arsiv / "imzali.udf.prov.json").read_text(encoding="utf-8"))
    assert yeni_kayit["entity_type"] == "e-imzali-nusha"
    assert yeni_kayit["was_derived_from"] == imza_oncesi


def test_imzasiz_urun_tipi_otomatik_degismez(tmp_path):
    """Regresyon: sign.sgn içermeyen ürün varsayılan 'diger' tipinde kalır —
    otomatik tip yalnız imza tespitiyle devreye girer."""
    urun = tmp_path / "x.udf"
    urun.write_bytes(b"PK\x03\x04 sentetik")
    kod, out = _muhur_cli("--kok", str(tmp_path), "--urun", str(urun))
    assert kod == 0, out
    kayit = json.loads((tmp_path / "x.udf.prov.json").read_text(encoding="utf-8"))
    assert kayit["entity_type"] == "diger"


# ── B5b — teslim_paketi: imzalı türev BAYAT değildir ───────────────────────

def test_imzali_turev_bayat_sayilmaz_best_effort_muhurlenir(ortam):
    """sign.sgn'li UDF'de mühür sha'sı imza-öncesi kalmışsa bu BAYAT değil
    TÜREV'dir: zincir GEÇER, 'imzalı türev mühürsüz' uyarısı basılır,
    best-effort e-imzali-nusha mührü was_derived_from=imza-öncesi sha ile
    yazılır, istisna defterine dogrulama-toleransi satırı düşer."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday, imzali=True)
    imza_oncesi = "c" * 64  # imza-öncesi (artık uyuşmayan) mühür sha'sı
    (ortam["kok"] / "taslak.udf.prov.json").write_text(json.dumps({
        "prov_schema": "oa-muhur/1.0",
        "artifact_sha256": imza_oncesi,
        "was_generated_by": "udf_yaz v0.5.8 (html2udf)",
    }, ensure_ascii=False), encoding="utf-8")

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    assert "PROV-BAYAT" not in cikti, "imzalı türev BAYAT sayılmamalıydı"
    assert "imzalı türev" in cikti
    kayit = json.loads((ortam["kok"] / "taslak.udf.prov.json")
                       .read_text(encoding="utf-8"))
    assert kayit["entity_type"] == "e-imzali-nusha"
    assert kayit["was_derived_from"] == imza_oncesi
    assert kayit["artifact_sha256"] == _sha256(aday)
    # istisna defteri: dogrulama-toleransi satırı (ortak şema)
    defter = ortam["kok"] / "_oa" / "defter" / "istisna-kayitlari.jsonl"
    assert defter.is_file(), "istisna defteri satırı düşmeliydi"
    satirlar = [json.loads(s) for s in
                defter.read_text(encoding="utf-8").splitlines() if s.strip()]
    tol = [s for s in satirlar if s["tur"] == "dogrulama-toleransi"]
    assert tol, "dogrulama-toleransi kaydı yok"
    for alan in ("zaman", "tur", "ilgili", "gerekce", "onay", "imza"):
        assert alan in tol[0], "istisna şemasında alan eksik: %s" % alan
    assert tol[0]["onay"] == "otomatik-kural"


def test_imzali_zincir_kurulmussa_yesil(ortam):
    """was_derived_from zinciri KURULMUŞ e-imzali-nusha mührü (sha güncel) →
    YEŞİL: uyarı yok, mühür yeniden basılmaz (was_generated_by aynı kalır)."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday, imzali=True)
    mm = _muhur_modulu()
    kayit = mm.e_imza_muhur_uret(str(ortam["kok"]), str(aday), "d" * 64,
                                 arac="sentetik-imza-akisi v1")
    mm.muhur_yaz(str(ortam["kok"]), str(aday), kayit)

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    assert "imzalı türev mühürsüz" not in cikti
    assert "e-imzalı nüsha" in cikti  # zincir kurulmuş — YEŞİL satırı
    kayit2 = json.loads((ortam["kok"] / "taslak.udf.prov.json")
                        .read_text(encoding="utf-8"))
    assert kayit2["was_generated_by"] == "sentetik-imza-akisi v1", (
        "kurulmuş zincirde mühür yeniden basılmamalıydı")
    assert kayit2["was_derived_from"] == "d" * 64


def test_imzali_ama_muhursuz_udf_e_imza_muhru_alir(ortam):
    """sign.sgn'li ama hiç mühürsüz UDF: uyarı + best-effort e-imzali-nusha
    mührü (imza-öncesi sha bilinmediğinden was_derived_from=None)."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday, imzali=True)

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    assert "imzalı türev" in cikti
    kayit = json.loads((ortam["kok"] / "taslak.udf.prov.json")
                       .read_text(encoding="utf-8"))
    assert kayit["entity_type"] == "e-imzali-nusha"
    assert kayit["was_derived_from"] is None
    assert kayit["artifact_sha256"] == _sha256(aday)


def test_imzasiz_bayat_muhur_hala_prov_bayat_red(ortam):
    """Regresyon (mevcut kapı davranışı): sign.sgn YOKSA bayat mühür hâlâ
    PROV-BAYAT RED'dir — tolerans yalnız imzalı türev içindir."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)  # imzasız
    (ortam["kok"] / "taslak.udf.prov.json").write_text(json.dumps({
        "prov_schema": "oa-muhur/1.0",
        "artifact_sha256": "0" * 64,
        "was_generated_by": "udf_yaz v0.5.8 (html2udf)",
    }, ensure_ascii=False), encoding="utf-8")

    kod, cikti = _tp(ortam)

    assert kod != 0, cikti
    assert "PROV-BAYAT" in cikti


# ── v0.5.8.5 E-İMZA GUARD — imzalı nüsha ASLA yamalanmaz ───────────────────

def test_imzali_nushada_kenar_sapmasi_yamalanmaz_e_imza_korunur(ortam):
    """1. dalga ajan bulgusunun kapanışı: sign.sgn'li UDF'de kenarlar 42.52
    değilse kenar yaması UYGULANMAZ (zip yeniden yazımı e-imzayı bozar) —
    dosya BAYT-AYNI kalır, görünür uyarı basılır, makbuza
    sekil_imzali_sapma=true düşer, zincir RED'e düşmez (karar avukatındır)."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday, imzali=True, kenar="28.35")  # yönetmelik-dışı kenar
    onceki_sha = _sha256(aday)

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    assert "e-imzayı bozacağı için" in cikti and "UYGULANMADI" in cikti
    assert _sha256(aday) == onceki_sha, (
        "imzalı nüshanın baytları DEĞİŞMEMELİYDİ — yama e-imzayı bozar")
    makbuz = _makbuz(ortam)
    assert makbuz.get("sekil_imzali_sapma") is True
    assert makbuz.get("kenar_duzeltildi") is False
    # istisna defterine dogrulama-toleransi kaydı düşer
    defter = ortam["kok"] / "_oa" / "defter" / "istisna-kayitlari.jsonl"
    satirlar = [json.loads(s) for s in
                defter.read_text(encoding="utf-8").splitlines() if s.strip()]
    assert any(s["tur"] == "dogrulama-toleransi" and "kenar" in s["gerekce"]
               for s in satirlar)


def test_imzasiz_kenar_sapmasi_hala_yamalanir_regresyon(ortam):
    """Regresyon: guard yalnız İMZALI nüshaya özgüdür — imzasız UDF'de kenar
    yaması aynen uygulanır (v0.5.8.4 GÖREV 5 davranışı korunur)."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday, kenar="28.35")  # imzasız + yönetmelik-dışı
    onceki_sha = _sha256(aday)

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    assert "kenarlar düzeltildi" in cikti
    assert _sha256(aday) != onceki_sha, "imzasızda yama dosyayı değiştirmeli"
    makbuz = _makbuz(ortam)
    assert makbuz.get("kenar_duzeltildi") is True
    assert makbuz.get("sekil_imzali_sapma") is False
