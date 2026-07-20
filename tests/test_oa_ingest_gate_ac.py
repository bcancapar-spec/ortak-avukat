# -*- coding: utf-8 -*-
"""oa-ingest — Gate A (sayfa/bölüm haritası) + Gate C (mekanik tür~ tahmini) testleri.

M1-2 Gate A+C paketi:
  Gate A: karakter > eşik (varsayılan 40000, testte --buyuk-esik ile küçültülür) olan
    evrak için md YANINA deterministik, KAYIPSIZ bir sayfa/bölüm haritası
    (`<taban>.harita.json`) üretilir. Mevcut sayfa ayracı (`<!-- --- sayfa N --- -->`)
    varsa birim='sayfa' (PDF/OCR); yoksa (duz-metin/udf/docx gibi) birim='bolum' (tüm
    gövde tek birim — içerik kaybı YOK, yalnız yapısal bölme). 00-INDEX.md 'büyük'
    bayrağını ve harita linkini taşır.
  Gate C: dosya adı/anahtar-kelimeden MEKANİK 'tur~' TAHMİNİ (ör. tebligat/karar/
    dilekce/bilirkişi/sicil/bilanço) — İÇERİK OKUMAZ, advisory'dir; eşleşme yoksa
    None (uydurulmuş varsayılan YOK). 00-INDEX.md'de '<tür> (tahmini)' diye işaretli.

Her iki kapı da DETERMİNİSTİK olmalı (seri==paralel çıktıyı bozmamalı) — bu dosya
ayrıca --isci 1 ile --isci 4 arasında künye YAPISAL özdeşliğini de doğrular.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "oa_ingest.py"

KAR_PER_TOKEN = 3


def _anlamli(s):
    return len(re.sub(r"\s+", "", s or ""))


def _kos(klasor, buyuk_esik=None, isci=None, ekstra=None):
    args = [sys.executable, str(SCRIPT), str(klasor), "--ocr", "kapali"]
    if buyuk_esik is not None:
        args += ["--buyuk-esik", str(buyuk_esik)]
    if isci is not None:
        args += ["--isci", str(isci)]
    if ekstra:
        args += ekstra
    cp = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, f"oa_ingest.py hata:\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    return cp


def _metin_dizin(klasor):
    return pathlib.Path(klasor) / "_oa" / "metin"


def _kunye(klasor):
    return json.loads((_metin_dizin(klasor) / "00-kunye.json").read_text(encoding="utf-8"))


def _index(klasor):
    return (_metin_dizin(klasor) / "00-INDEX.md").read_text(encoding="utf-8")


# ==================== GATE A — sayfa/bölüm haritası ====================

def test_kucuk_evrak_buyuk_bayragi_almaz_harita_uretilmez(tmp_path):
    (tmp_path / "001-kisa.txt").write_text("kısa gövde", encoding="utf-8")
    _kos(tmp_path)   # varsayılan eşik (40000) — hiç aşılmaz

    kayit = _kunye(tmp_path)["kayitlar"][0]
    assert kayit["buyuk"] is False
    assert kayit["harita"] == ""
    assert not list(_metin_dizin(tmp_path).glob("*.harita.json"))
    idx = _index(tmp_path)
    assert "büyük (>40,000 kar): **0**" in idx


def test_buyuk_duz_metin_bolum_haritasi_uretilir(tmp_path):
    """Ayraçsız (duz-metin) kaynak → tüm gövde TEK 'bölüm' — içerik kaybı YOK."""
    govde = "BAŞLIK SATIRI\n" + ("hukuki metin gövdesi tekrar ediyor. " * 20)
    (tmp_path / "001-buyuk.txt").write_text(govde, encoding="utf-8")
    _kos(tmp_path, buyuk_esik=100)

    kunye = _kunye(tmp_path)
    kayit = kunye["kayitlar"][0]
    assert kayit["buyuk"] is True
    assert kayit["harita"] == "001-buyuk.harita.json"

    harita_yol = _metin_dizin(tmp_path) / kayit["harita"]
    assert harita_yol.exists()
    harita = json.loads(harita_yol.read_text(encoding="utf-8"))
    assert harita["kaynak_md"] == kayit["md"]
    assert harita["birim"] == "bolum"
    assert harita["adet"] == 1
    bolum = harita["bolumler"][0]
    assert bolum["sayfa"] is None
    assert bolum["baslik"] == "BAŞLIK SATIRI"

    md_metni = (_metin_dizin(tmp_path) / kayit["md"]).read_text(encoding="utf-8")
    # offset, üretilen .md dosyasındaki karakter konumudur — gövdenin başlangıcını göstermeli.
    assert md_metni[bolum["offset"]:].lstrip().startswith("BAŞLIK SATIRI")
    beklenen_kar = _anlamli(md_metni[bolum["offset"]:])
    assert bolum["karakter"] == beklenen_kar
    assert bolum["token"] == beklenen_kar // KAR_PER_TOKEN

    idx = _index(tmp_path)
    assert "büyük (>100 kar): **1**" in idx
    assert f"`{kayit['harita']}`" in idx


def test_buyuk_pdf_sayfa_haritasi_uretilir(tmp_path):
    """Mevcut '<!-- --- sayfa N --- -->' ayracı varsa (PDF/OCR) birim='sayfa'; her
    sayfa kendi offset/başlık/karakter/token'ıyla haritaya girer — özetleme YOK."""
    fitz = pytest.importorskip("fitz")
    pdf_yol = tmp_path / "001-cok-sayfali.pdf"
    doc = fitz.open()
    sayfa_govdeleri = []
    for i in range(3):
        gov = f"SAYFA {i + 1} BASLIGI\n" + (f"sayfa {i + 1} govde metni tekrar ediyor. " * 15)
        sayfa_govdeleri.append(gov)
        page = doc.new_page()
        page.insert_text((72, 72), gov, fontsize=11)
    doc.save(str(pdf_yol))
    doc.close()

    _kos(tmp_path, buyuk_esik=50)

    kunye = _kunye(tmp_path)
    kayit = kunye["kayitlar"][0]
    assert kayit["yontem"] == "pdf-metin(PyMuPDF)", kunye
    assert kayit["buyuk"] is True
    assert kayit["harita"], "büyük PDF için harita üretilmeliydi"

    harita = json.loads((_metin_dizin(tmp_path) / kayit["harita"]).read_text(encoding="utf-8"))
    assert harita["birim"] == "sayfa"
    assert harita["adet"] == 3
    sayfalar = sorted(harita["bolumler"], key=lambda b: b["sayfa"])
    assert [b["sayfa"] for b in sayfalar] == [1, 2, 3]

    md_metni = (_metin_dizin(tmp_path) / kayit["md"]).read_text(encoding="utf-8")
    for i, bolum in enumerate(sayfalar):
        assert f"SAYFA {i + 1} BASLIGI" in bolum["baslik"]
        # offset'ten başlayan dilim, kendi sayfa gövdesini içermeli; sonraki AYRAÇTAN
        # (marker'ın kendisi hariç, tıpkı içeride bit_ofs=eslesmeler[i+1].start() gibi)
        # önce bitmeli — sayfalar birbirine karışmamış = kayıpsız yapısal bölme.
        sonraki_ayrac = md_metni.find("<!-- --- sayfa ", bolum["offset"])
        bitis = sonraki_ayrac if sonraki_ayrac != -1 else len(md_metni)
        dilim = md_metni[bolum["offset"]:bitis]
        assert f"sayfa {i + 1} govde" in dilim
        if i + 1 < len(sayfalar):
            assert f"SAYFA {i + 2} BASLIGI" not in dilim
        assert bolum["karakter"] == _anlamli(dilim)


def test_gate_a_seri_paralel_yapisal_ozdes(tmp_path):
    """Harita üretimi de determinizmi bozmamalı: seri (--isci 1) == paralel (--isci 4)."""
    d1, d2 = tmp_path / "seri", tmp_path / "paralel"
    for d in (d1, d2):
        d.mkdir()
        govde = "BASLIK\n" + ("govde metni tekrar. " * 30)
        (d / "001-buyuk.txt").write_text(govde, encoding="utf-8")
        (d / "002-tebligat-ornegi.txt").write_text("kısa tebligat metni", encoding="utf-8")

    _kos(d1, buyuk_esik=50, isci=1)
    _kos(d2, buyuk_esik=50, isci=4)

    k1, k2 = _kunye(d1), _kunye(d2)
    k1.pop("klasor", None)
    k2.pop("klasor", None)
    assert k1 == k2, "Gate A/C alanları seri≠paralel — determinizm bozuk"

    def _md_sha(klasor, kunye):
        md = _metin_dizin(klasor)
        out = {}
        for k in kunye["kayitlar"]:
            if k.get("md"):
                out[k["md"]] = hashlib.sha256((md / k["md"]).read_bytes()).hexdigest()
            if k.get("harita"):
                out[k["harita"]] = hashlib.sha256((md / k["harita"]).read_bytes()).hexdigest()
        return out

    assert _md_sha(d1, k1) == _md_sha(d2, k2), "md/harita dosyalarının sha256'ları farklı"


# ==================== GATE C — mekanik tür~ tahmini ====================

def test_tur_tahmini_dosya_adindan_mekanik_eslesir(tmp_path):
    (tmp_path / "001-tebligat-belgesi.txt").write_text("içerik", encoding="utf-8")
    (tmp_path / "002-mahkeme-karari.txt").write_text("içerik", encoding="utf-8")
    (tmp_path / "003-dava-dilekcesi.txt").write_text("içerik", encoding="utf-8")
    (tmp_path / "004-bilirkisi-raporu.txt").write_text("içerik", encoding="utf-8")
    (tmp_path / "005-rastgele-isim.txt").write_text("içerik", encoding="utf-8")
    _kos(tmp_path)

    kayitlar = {pathlib.Path(k["kaynak"]).name: k for k in _kunye(tmp_path)["kayitlar"]}
    assert kayitlar["001-tebligat-belgesi.txt"]["tur_tahmini"] == "tebligat"
    assert kayitlar["002-mahkeme-karari.txt"]["tur_tahmini"] == "karar"
    assert kayitlar["003-dava-dilekcesi.txt"]["tur_tahmini"] == "dilekce"
    assert kayitlar["004-bilirkisi-raporu.txt"]["tur_tahmini"] == "bilirkisi"
    # eşleşme yoksa None — UYDURULMUŞ varsayılan ('diğer' vb.) YASAK.
    assert kayitlar["005-rastgele-isim.txt"]["tur_tahmini"] is None

    idx = _index(tmp_path)
    assert "tebligat (tahmini)" in idx
    assert "karar (tahmini)" in idx
    assert "dilekce (tahmini)" in idx
    assert "bilirkisi (tahmini)" in idx
    assert "> Tür~ = dosya adından MEKANİK tahmin (Gate C), kesinlik DEĞİLDİR" in idx


def test_tur_tahmini_arizali_kayitlarda_da_calisir(tmp_path):
    """Gate C içerik OKUMAZ — bilinmeyen uzantı/bozuk arşiv gibi 'hata' damgalı
    kayıtlarda bile dosya adından tahmin üretilebilmeli (advisory, hatayı gizlemez)."""
    (tmp_path / "001-tebligat-taslagi.xyz").write_bytes(b"desteklenmeyen")
    _kos(tmp_path)

    kayit = _kunye(tmp_path)["kayitlar"][0]
    assert kayit["yontem"] == "bilinmeyen"
    assert kayit["tur_tahmini"] == "tebligat"
    assert kayit["buyuk"] is False
    assert kayit["harita"] == ""
