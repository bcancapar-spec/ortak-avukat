# -*- coding: utf-8 -*-
"""oa-pipeline / oa_metrik.py için testler.

Bu script Fable-tespitli TESTSİZ release-kapısı scriptlerinden biridir: üç
kanıt dosyasını (00-kunye.json, dosya-analiz.json, pipeline-durum.json)
okuyup token/verimlilik telemetrisi üreten bu "ölçer" (kapı değil) hiçbir
test doğrulamıyordu — sessizce sayı uydurmaya başlasa yakalanmazdı.

İki senaryo: (1) örnek/gerçekçi bir `_oa` iskeletinde metrik.json GERÇEKTEN
üretilir ve çökmez; (2) hiçbir kanıt dosyası yokken hiçbir sayı UYDURULMAZ —
ilgili bölümler 'yok'/'ölçülemedi' olarak damgalanır (script her koşulda
exit 0 döner; bu bir kapı değil, ölçerdir).
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline"
          / "scripts" / "oa_metrik.py")


def _cli(kok, cikti=None):
    args = [sys.executable, str(SCRIPT), "--kok", str(kok)]
    if cikti is not None:
        args += ["--cikti", str(cikti)]
    cp = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


@pytest.fixture
def izole_kok():
    return pathlib.Path(tempfile.mkdtemp())


def _ornek_iskelet_kur(kok):
    """Gerçekçi minimal _oa iskeleti: künye + tam-tur analiz + pipeline defteri
    (üç kaynağın da 'olculdu' bölümü üretmesi için birbirine tutarlı)."""
    metin_d = kok / "_oa" / "metin"
    analiz_d = kok / "_oa" / "analiz"
    defter_d = kok / "_oa" / "defter"
    for d in (metin_d, analiz_d, defter_d):
        d.mkdir(parents=True, exist_ok=True)

    kunye = {
        "toplam_evrak": 2,
        "toplam_karakter": 300,
        "kayitlar": [
            {"kaynak": "a.pdf", "md": "001-a.md", "karakter": 150, "sha": "abc123"},
            {"kaynak": "b.pdf", "md": "002-b.md", "karakter": 150, "sha": "def456"},
        ],
    }
    (metin_d / "00-kunye.json").write_text(json.dumps(kunye, ensure_ascii=False), encoding="utf-8")

    analiz = {
        "tam_tur_durumu": "TAMAM",
        "tam_tur_tarihi": "2026-07-01",
        "kunye_snapshot": {"toplam_evrak": 2, "imzalar": {"a.pdf": "sha:abc123", "b.pdf": "sha:def456"}},
        "gelismeler": [],
        "notlar": "001-a.md okunmuş ve değerlendirilmiştir.",
    }
    (analiz_d / "dosya-analiz.json").write_text(json.dumps(analiz, ensure_ascii=False), encoding="utf-8")

    defter = {
        "dosya": "Test Dosyası",
        "adimlar": {"1": {"parcalar": {"oa-alan": {"durum": "UYGULANDI"}}}},
        "katmanlar": {},
    }
    (defter_d / "pipeline-durum.json").write_text(json.dumps(defter, ensure_ascii=False), encoding="utf-8")


def test_script_mevcut():
    assert SCRIPT.is_file(), f"oa_metrik.py bulunamadı: {SCRIPT}"


# ── (1) örnek _oa iskeletinde metrik.json üretir, çökme yok ────────────────

def test_ornek_iskelette_metrik_json_uretilir_cokme_yok(izole_kok):
    _ornek_iskelet_kur(izole_kok)

    kod, cikti = _cli(izole_kok)

    assert kod == 0, f"oa_metrik her koşulda exit 0 dönmeli (ölçer, kapı değil); çıktı:\n{cikti}"
    metrik_yolu = izole_kok / "_oa" / "defter" / "metrik.json"
    assert metrik_yolu.is_file(), "metrik.json üretilmedi"

    metrik = json.loads(metrik_yolu.read_text(encoding="utf-8"))
    assert metrik["kulliyat"]["durum"] == "olculdu"
    assert metrik["kulliyat"]["toplam_evrak"] == 2
    assert metrik["kulliyat"]["toplam_karakter"] == 300
    assert metrik["secicilik"]["durum"] == "olculdu"
    assert metrik["secicilik"]["uretilen_md"] == 2
    assert metrik["tam_tur"]["durum"] == "yapildi"
    assert metrik["tam_tur"]["bekleyen_delta"] == {"yeni": 0, "degisen": 0, "toplam": 0}
    assert metrik["defter"]["durum"] == "olculdu"
    assert metrik["defter"]["toplam_parca"] == 1


def test_ornek_iskelette_ozet_stdouta_basilir(izole_kok):
    _ornek_iskelet_kur(izole_kok)
    kod, cikti = _cli(izole_kok)
    assert kod == 0
    assert "TOKEN / VERİMLİLİK TELEMETRİSİ" in cikti
    assert "KÜLLİYAT" in cikti
    assert "SEÇİCİLİK" in cikti
    assert "TAM TUR" in cikti
    assert "DEFTER" in cikti


def test_ozel_cikti_yoluna_yazilir(izole_kok):
    _ornek_iskelet_kur(izole_kok)
    hedef = izole_kok / "ozel-metrik.json"
    kod, _cikti = _cli(izole_kok, cikti=hedef)
    assert kod == 0
    assert hedef.is_file()
    json.loads(hedef.read_text(encoding="utf-8"))  # geçerli JSON olmalı


# ── (2) eksik dosyalarda 'ölçülemedi' der (uydurma sayı yok) ────────────────

def test_bos_kokte_kanit_yok_uydurma_sayi_olusmaz(izole_kok):
    """_oa hiç kurulmamış boş bir kökte: script çökmemeli (exit 0), ama
    hiçbir bölüm sayı UYDURMAMALI — durum 'yok' (kanıt dosyası hiç yok)
    olarak damgalanmalı ve toplam_evrak/toplam_karakter gibi alanlar hiç
    üretilmemeli."""
    kod, cikti = _cli(izole_kok)

    assert kod == 0, f"kanıt yokken de exit 0 (ölçer çökmez); çıktı:\n{cikti}"
    metrik_yolu = izole_kok / "_oa" / "defter" / "metrik.json"
    assert metrik_yolu.is_file()
    metrik = json.loads(metrik_yolu.read_text(encoding="utf-8"))

    for bolum in ("kulliyat", "secicilik", "tam_tur", "defter"):
        durum = metrik[bolum]["durum"]
        assert durum in ("yok", "olculemedi"), f"{bolum}: beklenmeyen ölçülmüş durum '{durum}'"

    # Uydurma sayı yok: kanıt olmayan bölümlerde sayısal alanlar hiç yok.
    assert "toplam_evrak" not in metrik["kulliyat"]
    assert "toplam_karakter" not in metrik["kulliyat"]
    assert "uretilen_md" not in metrik["secicilik"]
    assert "toplam_parca" not in metrik["defter"]

    # stdout'ta da uydurma sayı yerine "YOK"/açıklayıcı not var.
    assert "YOK" in cikti or "yok" in cikti.lower()


def test_kunye_var_ama_analiz_defter_yok_kismi_olculur(izole_kok):
    """Yalnız künye varsa: kulliyat ölçülür, ama tam_tur/defter 'yok' kalır
    (kanıt yok diye sıfır ya da tahmini sayı UYDURULMAZ)."""
    metin_d = izole_kok / "_oa" / "metin"
    metin_d.mkdir(parents=True, exist_ok=True)
    kunye = {"toplam_evrak": 1, "toplam_karakter": 90, "kayitlar": [
        {"kaynak": "tek.pdf", "md": "001-tek.md", "karakter": 90, "sha": "xyz"},
    ]}
    (metin_d / "00-kunye.json").write_text(json.dumps(kunye, ensure_ascii=False), encoding="utf-8")

    kod, _cikti = _cli(izole_kok)
    assert kod == 0
    metrik = json.loads((izole_kok / "_oa" / "defter" / "metrik.json").read_text(encoding="utf-8"))

    assert metrik["kulliyat"]["durum"] == "olculdu"
    assert metrik["kulliyat"]["toplam_evrak"] == 1
    assert metrik["tam_tur"]["durum"] == "yok"
    assert metrik["defter"]["durum"] == "yok"
    assert "toplam_parca" not in metrik["defter"]


def test_klasor_yok_hata_ile_cikar(izole_kok):
    olmayan = izole_kok / "olmayan-klasor"
    kod, cikti = _cli(olmayan)
    assert kod != 0
    assert "HATA" in cikti
