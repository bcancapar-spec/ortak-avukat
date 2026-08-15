# -*- coding: utf-8 -*-
"""v0.5.8.4 — teslim_paketi.py + muhur_yaz.py: 372 Torbalı saha derslerinin
mekanik karşılığı.

Kapsam (görev başına en az bir test):
  1) MEVCUT-UDF DEVRALMA  : geçerli aday → yeniden üretim YOK + makbuzda
     `udf_devralindi`; geçersiz (elle-üretim imzalı) aday → karantina + taze üretim.
  2) MAKBUZ GARANTİSİ     : erken çıkış (taslak yok) dahi RED makbuzu düşürür
     (zaman + sebep + argv).
  3) PROV-TAZELİK KAPISI  : bayat mühür → RED "PROV-BAYAT"; mühür hiç yoksa
     teslim_paketi KENDİSİ mühürler (mühürsüz teslim fiziksel imkânsız).
  4) YEREL-DAMGA KAPISI   : was_generated_by 'yerel' içeriyorsa RED.
  5) ŞEKİL KAPISI         : kenar != 42.52 → udf_yaz._sayfa_kenari_yonetmelik ile
     yamalanır + mühür sha'sı GÜNCELLENİR; LineSpacing istişari uyarı bloklamaz.
  6) TAZELİK BİLGİ KAPISI : tazelik_denetim BAYAT satırları makbuza girer,
     kapı KAPATMAZ.
  7) muhur_yaz.py         : llm_kullanimi otomatiği + --tasi ESKI YENI round-trip.

TEST MİMARİSİ (sahte-skills ağacı): teslim_paketi.py alt scriptleri kendi
__file__ konumundan GÖRELİ keşfeder. Gerçek scriptler (teslim_paketi, muhur_yaz,
tazelik_denetim) tmp_path altındaki bir sahte skills ağacına KOPYALANIR;
engelleyici kapılar (dilekce_denetim, kunye_teyit, ictihat_muhakeme_denetim)
hep-geçer SAHTELERLE, udf_yaz ise sentetik-ama-hafif-geçerli UDF üreten bir
sahteyle (kenar yaması GERÇEK udf_yaz._sayfa_kenari_yonetmelik'e delege eder)
değiştirilir. Böylece ağ/oturum (npx udf-cli) GEREKMEDEN üretim yolu da
deterministik sınanır. Tüm veriler sentetiktir (tmp_path — gizlilik m.7).
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

# hep-geçer sahte kapı (dilekce_denetim / kunye_teyit / ictihat_muhakeme_denetim)
SAHTE_GECER = "import sys\nprint('SAHTE-KAPI: OK')\nsys.exit(0)\n"

# Sentetik content.xml şablonu — {k}: kenar pt, {ls}: LineSpacing, {stil}:
# hvl-default stil tanımı (VARSA hafif-geçerli; YOKSA 372'nin elle-üretim imzası).
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


def _sentetik_udf(yol, hvl=True, kenar="42.52", ls="0.50"):
    """Sentetik .udf: zip + content.xml. hvl=False → stil tanımı yok
    (elle-üretim imzası — hafif geçerlilikten GEÇMEZ)."""
    xml = _CONTENT_SABLON.format(k=kenar, ls=ls, stil=(_HVL_STIL if hvl else ""))
    with zipfile.ZipFile(str(yol), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.xml", xml)


def _sha256(yol):
    h = hashlib.sha256()
    with open(str(yol), "rb") as f:
        for parca in iter(lambda: f.read(1 << 16), b""):
            h.update(parca)
    return h.hexdigest()


def _sahte_udf_yaz_kaynak():
    """Sahte udf_yaz.py: CLI --girdi/--cikti ile SENTETİK ama hafif-geçerli bir
    UDF yazar + kok'a URETIM-IZI.txt düşer (üretim çağrıldı mı kanıtı).
    `_sayfa_kenari_yonetmelik` ve `_KENAR_PT` GERÇEK udf_yaz.py'den delege
    edilir — kenar yaması testlerde GERÇEK fonksiyonla sınanır."""
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
        "    kenar = os.environ.get('OA_TEST_KENAR', '42.52')\n"
        "    xml = _SABLON.format(k=kenar, ls='0.50', stil=_STIL)\n"
        "    with zipfile.ZipFile(a.cikti, 'w', zipfile.ZIP_DEFLATED) as z:\n"
        "        z.writestr('content.xml', xml)\n"
        "    with open(os.path.join(os.getcwd(), 'URETIM-IZI.txt'), 'a',\n"
        "              encoding='utf-8') as f:\n"
        "        f.write(a.cikti + '\\n')\n"
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
    taslak.write_text("Sentetik taslak metni.\n", encoding="utf-8")
    return {"script": ok / "teslim_paketi.py", "kok": kok, "taslak": taslak}


def _tp(ortam, extra=(), env_ek=None, taslak=None):
    env = dict(os.environ)
    env.pop("OA_SKILLS_KOK", None)  # determinizm: fallback gerçek ağaca kaçmasın
    if env_ek:
        env.update(env_ek)
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


def _muhur_cli(*arglar):
    cp = subprocess.run([sys.executable, str(GERCEK_MUHUR), *arglar],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace")
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# ── GÖREV 1 — MEVCUT-UDF DEVRALMA ───────────────────────────────────────────

def test_gecerli_aday_devralinir_uretim_cagrilmaz(ortam):
    """Taslak yanında geçerli (hvl-default stil tanımlı) bir .udf VARSA:
    yeniden üretim YOK (372 çift-UDF tuzağı), makbuza `udf_devralindi` düşer."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    assert "DEVRALINDI" in cikti
    assert not (ortam["kok"] / "URETIM-IZI.txt").exists(), (
        "geçerli aday varken üretim ÇAĞRILMAMALIYDI:\n%s" % cikti)
    m = _makbuz(ortam)
    assert m["udf_devralindi"] is not None
    assert m["udf_devralindi"]["yol"].endswith("taslak.udf")
    assert m["udf_devralindi"]["sha256"] and len(m["udf_devralindi"]["sha256"]) == 64
    assert m["udf_yolu"].endswith("taslak.udf")


def test_cikti_klasorundeki_ayni_kok_adli_udf_devralinir(ortam):
    """_oa/cikti içindeki taslakla AYNI kök-adlı .udf de aday sayılır."""
    cikti_dizin = ortam["kok"] / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    aday = cikti_dizin / "taslak.udf"
    _sentetik_udf(aday)

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    m = _makbuz(ortam)
    assert m["udf_devralindi"] is not None
    assert "cikti" in m["udf_devralindi"]["yol"]
    assert not (ortam["kok"] / "URETIM-IZI.txt").exists()


def test_gecersiz_aday_karantinaya_tasinir_taze_uretilir(ortam):
    """Elle-üretim imzalı (stil tanımı YOK) aday: karantinaya taşınır
    (_oa/arsiv-yerel/gecersiz-elle-udf/), taze üretim yapılır."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday, hvl=False)

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    assert not aday.exists(), "geçersiz aday yerinde bırakılmamalıydı"
    karantina = ortam["kok"] / "_oa" / "arsiv-yerel" / "gecersiz-elle-udf"
    assert karantina.is_dir()
    tasinanlar = list(karantina.glob("*taslak.udf"))
    assert tasinanlar, "aday karantina klasöründe zaman damgalı adla durmalıydı"
    assert (ortam["kok"] / "URETIM-IZI.txt").exists(), (
        "geçersiz aday sonrası TAZE üretim çağrılmalıydı:\n%s" % cikti)
    m = _makbuz(ortam)
    assert m["udf_devralindi"] is None
    assert m["udf_yolu"].endswith("taslak.md.udf")


# ── GÖREV 2 — MAKBUZ GARANTİSİ (erken çıkış dahi izli) ─────────────────────

def test_erken_cikis_red_makbuzu_dusurur(ortam):
    """Taslak diskte YOKken bile RED makbuzu düşer (zaman + sebep + argv) —
    372'de erken çıkışlar makbuzsuz ölüyordu."""
    olmayan = ortam["kok"] / "boyle-bir-taslak-yok.md"

    kod, cikti = _tp(ortam, taslak=olmayan)

    assert kod != 0
    m = _makbuz(ortam, red=True)
    assert m["zaman"]
    assert "taslak bulunamadı" in m["sebep"]
    assert isinstance(m["argv"], list) and "--kok" in m["argv"]
    assert m["exit_kodu"] != 0


# ── GÖREV 3 — PROV-TAZELİK KAPISI ───────────────────────────────────────────

def test_bayat_muhur_prov_bayat_red(ortam):
    """Mühürdeki artifact_sha256 güncel sha ile uyuşmuyorsa teslim RED
    (372 kanıtı: cikti/10 mührü bayat kalmıştı)."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)
    (ortam["kok"] / "taslak.udf.prov.json").write_text(json.dumps({
        "prov_schema": "oa-muhur/1.0",
        "artifact_sha256": "0" * 64,  # bayat
        "was_generated_by": "udf_yaz v0.5.8 (html2udf)",
    }, ensure_ascii=False), encoding="utf-8")

    kod, cikti = _tp(ortam)

    assert kod != 0, cikti
    assert "PROV-BAYAT" in cikti
    m = _makbuz(ortam, red=True)
    assert "PROV-BAYAT" in m["sebep"]


def test_muhursuz_udf_otomatik_muhurlenir(ortam):
    """Mühür hiç yoksa teslim_paketi muhur_yaz'ı KENDİSİ koşturur — mühürsüz
    teslim fiziksel imkânsız (372: Stop hook 23 uyardı, model 0 uyguladı)."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    prov = ortam["kok"] / "taslak.udf.prov.json"
    assert prov.is_file(), "otomatik mühür üretilmeliydi"
    kayit = json.loads(prov.read_text(encoding="utf-8"))
    assert kayit["was_generated_by"] == "teslim_paketi (html2udf zinciri)"
    assert kayit["artifact_sha256"] == _sha256(aday)
    # GÖREV 7 sinerjisi: llm verilmedi → otomatik beyan
    assert kayit["llm_kullanimi"] == "mekanik üretim; içerik oturum LLM koşusundan"


def test_taze_uretim_de_otomatik_muhurlenir(ortam):
    """Devralma değil ÜRETİM yolunda da çıkan .udf mühürsüz kalamaz."""
    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    udf = ortam["kok"] / "taslak.md.udf"
    assert udf.is_file()
    assert (ortam["kok"] / "taslak.md.udf.prov.json").is_file()


# ── GÖREV 4 — YEREL-DAMGA KAPISI ────────────────────────────────────────────

def test_yerel_damgali_muhur_red(ortam):
    """was_generated_by 'yerel' içeriyorsa — sha TAZE olsa bile — teslim RED
    (üretilen .udf doğrulanmadan yüklenmez kuralı; yerel motor UYAP'ta açılmıyor)."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)
    (ortam["kok"] / "taslak.udf.prov.json").write_text(json.dumps({
        "prov_schema": "oa-muhur/1.0",
        "artifact_sha256": _sha256(aday),  # taze — yine de RED olmalı
        "was_generated_by": "udf_yaz --yerel-motor v1.1",
    }, ensure_ascii=False), encoding="utf-8")

    kod, cikti = _tp(ortam)

    assert kod != 0, cikti
    assert "YEREL-MOTOR ÜRÜNÜ TESLİME GİREMEZ" in cikti
    m = _makbuz(ortam, red=True)
    assert "YEREL" in m["sebep"]


# ── GÖREV 5 — ŞEKİL KAPISI (kenar 42.52 + istişari) ────────────────────────

def test_kenar_42_52_degilse_yamalanir_ve_muhur_guncellenir(ortam):
    """Kenar != 42.52 → udf_yaz._sayfa_kenari_yonetmelik ile DÜZELTİLİR (AB3
    tanığı: yamalı dosya UYAP'ta açıldı), makbuza `kenar_duzeltildi` yazılır,
    yama sha'yı değiştirdiği için mühür GÜNCELLENİR (bayat mühür kalmaz)."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday, kenar="70.87")
    eski_sha = _sha256(aday)
    (ortam["kok"] / "taslak.udf.prov.json").write_text(json.dumps({
        "prov_schema": "oa-muhur/1.0",
        "artifact_sha256": eski_sha,  # yama ÖNCESİ taze mühür
        "was_generated_by": "teslim_paketi (html2udf zinciri)",
    }, ensure_ascii=False), encoding="utf-8")

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    with zipfile.ZipFile(str(aday)) as z:
        xml = z.read("content.xml").decode("utf-8")
    for kenar_ad in ("leftMargin", "rightMargin", "topMargin", "bottomMargin"):
        assert '%s="42.52"' % kenar_ad in xml, xml
    m = _makbuz(ortam)
    assert m["kenar_duzeltildi"] is True
    kayit = json.loads((ortam["kok"] / "taslak.udf.prov.json").read_text(encoding="utf-8"))
    yeni_sha = _sha256(aday)
    assert yeni_sha != eski_sha, "yama sha'yı değiştirmiş olmalıydı"
    assert kayit["artifact_sha256"] == yeni_sha, "mühür yama SONRASI sha'ya güncellenmeliydi"
    assert kayit["was_derived_from"] == eski_sha


def test_linespacing_istisari_uyari_kapiyi_kapatmaz(ortam):
    """LineSpacing 0.50 yaygın değilse İSTİŞARİ satır basılır ama zincir GEÇER."""
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday, ls="0.90")

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    assert "İSTİŞARİ" in cikti
    assert "TESLİME HAZIR" in cikti


# ── GÖREV 6 — TAZELİK BİLGİ KAPISI (advisory) ──────────────────────────────

def test_tazelik_bayat_satirlari_makbuza_gecer_kapatmaz(ortam):
    """tazelik_denetim BAYAT bulursa satırlar makbuzda `tazelik_uyarilari`
    olarak görünür; kapı KAPATMAZ (amaç çizgisi: görünürlük, blok değil)."""
    metin = ortam["kok"] / "_oa" / "metin"
    metin.mkdir(parents=True)
    (metin / "00-kunye.json").write_text('{"sentetik": true}', encoding="utf-8")
    cikti_dizin = ortam["kok"] / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    (cikti_dizin / "01-analiz.md").write_text(
        "<!-- kaynaklar: metin/00-kunye.json@deadbeef -->\n\n# Sentetik analiz\n",
        encoding="utf-8")
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)

    kod, cikti = _tp(ortam)

    assert kod == 0, cikti
    m = _makbuz(ortam)
    assert isinstance(m["tazelik_uyarilari"], list) and m["tazelik_uyarilari"]
    assert any("BAYAT" in u for u in m["tazelik_uyarilari"])
    assert any("01-analiz.md" in u for u in m["tazelik_uyarilari"])


# ── GÖREV 7 — muhur_yaz.py: llm otomatiği + --tasi round-trip ──────────────

def test_muhur_llm_varsayilani_mekanik_uretim(tmp_path):
    """--llm verilmezse llm_kullanimi 'beyan edilmedi' değil, otomatik
    'mekanik üretim; içerik oturum LLM koşusundan' olur."""
    urun = tmp_path / "x.udf"
    urun.write_bytes(b"PK\x03\x04 sentetik")
    kod, out = _muhur_cli("--kok", str(tmp_path), "--urun", str(urun))
    assert kod == 0, out
    kayit = json.loads((tmp_path / "x.udf.prov.json").read_text(encoding="utf-8"))
    assert kayit["llm_kullanimi"] == "mekanik üretim; içerik oturum LLM koşusundan"


def test_muhur_tasi_round_trip(tmp_path):
    """--tasi ESKI YENI: dosya + mühür arşive taşınır, artifact_file güncellenir,
    sha AYNI kalır, yeni konumda --dogrula geçer."""
    teslim = tmp_path / "_oa" / "teslim"
    teslim.mkdir(parents=True)
    urun = teslim / "dilekce.udf"
    urun.write_bytes(b"PK\x03\x04 sentetik-icerik")
    kod, out = _muhur_cli("--kok", str(tmp_path), "--urun", str(urun),
                          "--tip", "dilekce_udf")
    assert kod == 0, out
    eski_kayit = json.loads((teslim / "dilekce.udf.prov.json").read_text(encoding="utf-8"))

    arsiv = tmp_path / "_oa" / "arsiv-yerel"
    arsiv.mkdir(parents=True)
    yeni = arsiv / "dilekce.udf"
    kod, out = _muhur_cli("--kok", str(tmp_path), "--tasi", str(urun), str(yeni))
    assert kod == 0, out

    assert yeni.is_file() and not urun.exists()
    assert not (teslim / "dilekce.udf.prov.json").exists(), "eski mühür kalmamalıydı"
    yeni_kayit = json.loads((arsiv / "dilekce.udf.prov.json").read_text(encoding="utf-8"))
    assert yeni_kayit["artifact_sha256"] == eski_kayit["artifact_sha256"], "sha AYNI kalmalı"
    assert "arsiv-yerel" in yeni_kayit["artifact_file"]

    kod, out = _muhur_cli("--kok", str(tmp_path), "--dogrula", str(yeni))
    assert kod == 0 and "uyumlu" in out


def test_muhur_tasi_sha_degismisse_reddeder(tmp_path):
    """Taşıma sırasında dosya içeriği mühürden farklıysa --tasi exit 1 —
    'sha aynı kalmalı' kuralı sessizce delinemez."""
    urun = tmp_path / "y.udf"
    urun.write_bytes(b"PK\x03\x04 birinci-icerik")
    kod, out = _muhur_cli("--kok", str(tmp_path), "--urun", str(urun))
    assert kod == 0, out
    urun.write_bytes(b"PK\x03\x04 DEGISTIRILMIS")  # mühürden sonra oynama
    yeni = tmp_path / "arsiv-y.udf"
    kod, out = _muhur_cli("--kok", str(tmp_path), "--tasi", str(urun), str(yeni))
    assert kod == 1, out


# ── makbuz şeması geriye-uyum (mevcut alanlar korunur) ─────────────────────

def test_basari_makbuzu_yeni_alanlarla_birlikte_eski_semayi_korur(ortam):
    aday = ortam["kok"] / "taslak.udf"
    _sentetik_udf(aday)
    kod, cikti = _tp(ortam)
    assert kod == 0, cikti
    m = _makbuz(ortam)
    for alan in ("zaman", "taslak_yol", "taslak_sha256", "tip", "taraf",
                 "kapilar", "exit_kodu", "udf_yolu", "udf_atlandi_istekle",
                 "ictihat_muhakeme_kanali", "surum", "durdu",
                 "udf_devralindi", "kenar_duzeltildi", "tazelik_uyarilari", "argv"):
        assert alan in m, "makbuzda alan eksik: %s" % alan
    for k in m["kapilar"]:
        assert k["durum"] in ("OK", "BLOK", "ATLA", "BILGI")
