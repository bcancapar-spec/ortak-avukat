# -*- coding: utf-8 -*-
"""v0.5.16 — GRUP E: oa-ingest OCR ARAÇ HATASI TEŞHİSİ (P0-2 / B-1 / B-8) +
okuma_kapisi KRİTİK EVRAK → SÜRE ADAYI (P1-10 / A-4).

Bulgular:
  P0-2/B-1/B-8  `ocr_png` Tesseract'ın returncode/stderr'ini OKUMUYORDU: dil paketi
                (tur.traineddata) yokken tesseract rc=1 + "Error opening data file"
                basıyor, script bunu BOŞ SAYFA sanıp P0-9 retry zincirini (DPI/PSM/
                yönelim × her sayfa) boşa koşturuyor, evrağı "OCR-BOŞ → GÖRSEL
                İNCELEME GEREK" diye damgalayıp PNG yazıyordu — ORTAM hatası EVRAK
                özelliği gibi raporlanıyordu (Linux denetiminde 2 kırmızı test).
  P1-10/A-4     Tebligat/gerekçeli karar/ödeme emri sınıfı evraklar künyede duruyor
                ama hiçbir mekanik adım bunları "süre başlatabilir" diye
                işaretlemiyordu; avukat süre flag'ini elle hatırlamak zorundaydı.

Test stratejisi — SAHTE TESSERACT: gerçek tesseract+tur bu makinede kurulu
olduğu için hata yolu ancak sahte bir ikiliyle sınanabilir. `OA_TESSERACT_YOL`
ortam değişkeni (yeni) modül sabitini geçersiz kılar; sahte ikili (Windows'ta
.cmd sarmalayıcı + python stub, POSIX'te sh sarmalayıcı) gerçek tesseract 5.x'in
dil-paketi-yok çıktısını (rc=1 + stderr imzaları) BİREBİR taklit eder. İki mod:
  - "dil-yok":  `--list-langs` tur'u LİSTELEMEZ → main() tek seferlik UYARI basar,
                OCR gerektiren her evrak damgayı alır, sayfa başına tesseract
                HİÇ çağrılmaz (israf yok).
  - "yalanci":  `--list-langs` tur'u listeler (ön-kontrol geçer) ama OCR çağrısı
                rc=1 + "Error opening data file" üretir → sayfa düzeyinde teşhis;
                retry zinciri ÇALIŞMAZ (tek çağrı), sonraki sayfa denenmez.
Her iki modda da: künye `ocr_bos_evrak == 0`, `ocr_arac_hatasi == 1`, damga
metni, görsel klasörü YOK, INDEX'te ayrı bölüm + kurulum önerisi; metin PDF/
düz-metin evraklar yine işlenir. Fikstürler tamamen sentetiktir (anayasa m.7).
"""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import textwrap

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
INGEST = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "oa_ingest.py"
KAPI = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "okuma_kapisi.py"

OCR_ARAC_HATA_DAMGA = "OCR YAPILAMADI — dil paketi/araç hatası (ortam hatası, evrak özelliği DEĞİL)"

_STUB_PY = textwrap.dedent('''\
    # SAHTE TESSERACT — yalnız test; gerçek tesseract 5.x'in dil-paketi-yok çıktısını taklit eder.
    import os, sys
    log = os.environ.get("OA_SAHTE_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as f:
            f.write(" ".join(sys.argv[1:]) + "\\n")
    mod = os.environ.get("OA_SAHTE_MOD", "yalanci")
    if "--list-langs" in sys.argv:
        diller = ["eng", "osd"] + (["tur"] if mod == "yalanci" else [])
        print('List of available languages in "/usr/share/tesseract-ocr/5/tessdata/" (%d):' % len(diller))
        print("\\n".join(diller))
        sys.exit(0)
    if "--version" in sys.argv:
        print("tesseract 5.4.0 (sahte)")
        sys.exit(0)
    sys.stderr.write(
        "Error opening data file /usr/share/tesseract-ocr/5/tessdata/tur.traineddata\\n"
        "Please make sure the TESSDATA_PREFIX environment variable is set to your \\"tessdata\\" directory.\\n"
        "Failed loading language 'tur'\\n"
        "Tesseract couldn't load any languages!\\n"
        "Could not initialize tesseract.\\n")
    sys.exit(1)
''')


def _sahte_tesseract(dizin):
    """Sahte tesseract ikilisini `dizin` altına kurar; çalıştırılabilir yolu döndürür."""
    dizin = pathlib.Path(dizin)
    dizin.mkdir(parents=True, exist_ok=True)
    stub = dizin / "sahte_tesseract.py"
    stub.write_text(_STUB_PY, encoding="utf-8")
    if os.name == "nt":
        ikili = dizin / "tesseract.cmd"
        ikili.write_text(f'@echo off\r\n"{sys.executable}" "{stub}" %*\r\nexit /b %ERRORLEVEL%\r\n',
                         encoding="utf-8")
    else:
        ikili = dizin / "tesseract"
        ikili.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{stub}" "$@"\n', encoding="utf-8")
        ikili.chmod(0o755)
    return ikili


def _ortam(ikili, mod, log):
    env = dict(os.environ)
    env["OA_TESSERACT_YOL"] = str(ikili)
    env["OA_SAHTE_MOD"] = mod
    env["OA_SAHTE_LOG"] = str(log)
    return env


def _kos(klasor, env, isci="1"):
    cp = subprocess.run(
        [sys.executable, str(INGEST), str(klasor), "--ocr", "auto", "--isci", isci],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return cp


def _kunye(klasor):
    return json.loads((pathlib.Path(klasor) / "_oa" / "metin" / "00-kunye.json").read_text(encoding="utf-8"))


def _index(klasor):
    return (pathlib.Path(klasor) / "_oa" / "metin" / "00-INDEX.md").read_text(encoding="utf-8")


def _bos_pdf(yol, sayfa=2):
    fitz = pytest.importorskip("fitz")
    doc = fitz.open()
    for _ in range(sayfa):
        doc.new_page()          # metin katmanı YOK → OCR tetiklenir
    doc.save(str(yol))
    doc.close()


def _korpus(tmp_path):
    """Sentetik dava klasörü: 1 taranmış (boş) PDF + 1 düz metin evrak."""
    _bos_pdf(tmp_path / "005-tarama.pdf", sayfa=2)
    (tmp_path / "002-not.txt").write_text("Sentetik düz metin evrak — E. 2099/1 örnek dosyası.",
                                          encoding="utf-8")


def _oi(env=None):
    """oa_ingest.py'yi süreç-içi yükler (OA_TESSERACT_YOL import anında okunur)."""
    eski = dict(os.environ)
    try:
        if env:
            os.environ.update(env)
        spec = importlib.util.spec_from_file_location("oa_ingest_v0516_E", INGEST)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        os.environ.clear()
        os.environ.update(eski)


# ═════════════════════════════════════════════════════════════════════════
# (A) BİRİM — ocr_png dönüşü (metin, hata); ön-kontrol
# ═════════════════════════════════════════════════════════════════════════

def test_ocr_png_arac_hatasini_metin_degil_hata_olarak_doner(tmp_path):
    ikili = _sahte_tesseract(tmp_path / "bin")
    log = tmp_path / "log.txt"
    oi = _oi({"OA_TESSERACT_YOL": str(ikili), "OA_SAHTE_MOD": "yalanci", "OA_SAHTE_LOG": str(log)})
    assert str(oi.TESSERACT) == str(ikili), "OA_TESSERACT_YOL modül sabitini geçersiz kılmalı"
    png = tmp_path / "p.png"
    png.write_bytes(b"\x89PNG sahte")
    os.environ["OA_SAHTE_MOD"] = "yalanci"; os.environ["OA_SAHTE_LOG"] = str(log)
    try:
        metin, hata = oi.ocr_png(str(png), "tur")
    finally:
        os.environ.pop("OA_SAHTE_MOD", None); os.environ.pop("OA_SAHTE_LOG", None)
    assert metin is None
    assert hata and "tur.traineddata" in hata, hata


def test_on_kontrol_dil_paketi_yoksa_false_varsa_true(tmp_path):
    ikili = _sahte_tesseract(tmp_path / "bin")
    oi = _oi({"OA_TESSERACT_YOL": str(ikili)})
    os.environ["OA_SAHTE_MOD"] = "dil-yok"
    try:
        var, detay = oi._tesseract_dil_var_mi("tur")
        assert var is False and "tur" in detay
        os.environ["OA_SAHTE_MOD"] = "yalanci"
        var2, _ = oi._tesseract_dil_var_mi("tur")
        assert var2 is True
    finally:
        os.environ.pop("OA_SAHTE_MOD", None)


def test_gecersiz_oa_tesseract_yol_arac_hatasi_olarak_gorunur(tmp_path):
    """Var olmayan bir ikili yolu ÇÖKME değil, görünür araç hatası üretir (fail-closed)."""
    oi = _oi({"OA_TESSERACT_YOL": str(tmp_path / "yok" / "tesseract.exe")})
    png = tmp_path / "p.png"; png.write_bytes(b"x")
    metin, hata = oi.ocr_png(str(png), "tur")
    assert metin is None and hata


# ═════════════════════════════════════════════════════════════════════════
# (B) UÇTAN UCA — sahte tesseract ile künye/INDEX/görsel sözleşmesi
# ═════════════════════════════════════════════════════════════════════════

def _ortak_denetim(tmp_path, cp):
    assert cp.returncode == 0, f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    kunye = _kunye(tmp_path)
    assert kunye["ocr_bos_evrak"] == 0, "ortam hatası OCR-BOŞ sayılmamalı"
    assert kunye["ocr_arac_hatasi"] == 1, kunye
    pdf = next(k for k in kunye["kayitlar"] if k["kaynak"].endswith("005-tarama.pdf"))
    assert pdf["ocr_durum"] == "arac-hatasi"
    assert pdf["ocr_bos_sayfalar"] == [] and pdf["gorsel_klasor"] == ""
    assert OCR_ARAC_HATA_DAMGA in (pdf.get("hata") or "")
    assert pdf["teyit_gerek"] is True
    assert not (tmp_path / "_oa" / "metin" / "gorsel").exists(), "görsel klasörü YAZILMAMALI"
    txt = next(k for k in kunye["kayitlar"] if k["kaynak"].endswith("002-not.txt"))
    assert txt["yontem"] == "duz-metin" and txt["karakter"] > 0, "metin evrak yine işlenmeli"
    idx = _index(tmp_path)
    assert "## 🔴 OCR YAPILAMADI (ortam hatası)" in idx
    assert "tur.traineddata" in idx and "tesseract-ocr-tur" in idx
    assert "## 🔴 OCR-BOŞ" not in idx
    assert "🔴 OCR-BOŞ (görsel inceleme gerek): **0**" in idx
    md = (tmp_path / "_oa" / "metin" / pdf["md"]).read_text(encoding="utf-8")
    assert OCR_ARAC_HATA_DAMGA in md
    assert "OCR YAPILAMADI" in cp.stderr
    return kunye


def test_dil_paketi_yok_tek_uyari_ve_sayfa_basina_deneme_yok(tmp_path):
    ikili = _sahte_tesseract(tmp_path.parent / f"bin-{tmp_path.name}")
    log = tmp_path.parent / f"log-{tmp_path.name}.txt"
    _korpus(tmp_path)
    cp = _kos(tmp_path, _ortam(ikili, "dil-yok", log))
    _ortak_denetim(tmp_path, cp)
    assert "UYARI" in cp.stderr and "--list-langs" in cp.stderr and "'tur'" in cp.stderr
    cagrilar = log.read_text(encoding="utf-8").splitlines()
    assert cagrilar == ["--list-langs"], f"OCR çağrısı yapılmamalıydı (israf): {cagrilar}"


def test_dil_paketi_var_gorunup_ocr_cokerse_sayfa_duzeyinde_teshis_retry_yok(tmp_path):
    ikili = _sahte_tesseract(tmp_path.parent / f"bin-{tmp_path.name}")
    log = tmp_path.parent / f"log-{tmp_path.name}.txt"
    _korpus(tmp_path)
    cp = _kos(tmp_path, _ortam(ikili, "yalanci", log))
    _ortak_denetim(tmp_path, cp)
    cagrilar = [s for s in log.read_text(encoding="utf-8").splitlines() if s != "--list-langs"]
    # 2 sayfa × 4 retry adımı = 8 potansiyel çağrı; araç hatası İLK çağrıda teşhis edilir
    assert len(cagrilar) == 1, f"retry zinciri/sonraki sayfa çalışmamalıydı: {cagrilar}"
    assert "-l tur" in cagrilar[0]


def test_paralel_isci_yolunda_da_ayni_damga(tmp_path):
    ikili = _sahte_tesseract(tmp_path.parent / f"bin-{tmp_path.name}")
    log = tmp_path.parent / f"log-{tmp_path.name}.txt"
    _korpus(tmp_path)
    cp = _kos(tmp_path, _ortam(ikili, "dil-yok", log), isci="2")
    _ortak_denetim(tmp_path, cp)
    cagrilar = log.read_text(encoding="utf-8").splitlines()
    assert cagrilar == ["--list-langs"], f"işçiler de opts üzerinden ön-kontrolü almalı: {cagrilar}"


def test_goruntu_yolunda_da_arac_hatasi(tmp_path):
    Image = pytest.importorskip("PIL.Image")
    ikili = _sahte_tesseract(tmp_path.parent / f"bin-{tmp_path.name}")
    log = tmp_path.parent / f"log-{tmp_path.name}.txt"
    Image.new("L", (300, 100), 255).save(tmp_path / "011-tarama.png")
    cp = _kos(tmp_path, _ortam(ikili, "yalanci", log))
    assert cp.returncode == 0, cp.stderr
    kunye = _kunye(tmp_path)
    k = kunye["kayitlar"][0]
    assert k["ocr_durum"] == "arac-hatasi" and kunye["ocr_arac_hatasi"] == 1
    assert kunye["ocr_bos_evrak"] == 0
    assert not (tmp_path / "_oa" / "metin" / "gorsel").exists()


def test_arac_hatasi_onbellege_yazilmaz_ortam_duzelince_yeniden_denenir(tmp_path):
    """v1.5.1(a) doktrini: arıza sonucu önbelleğe girmez — tur.traineddata kurulunca
    aynı imzalı evrak bayat damgayla servis edilmez."""
    ikili = _sahte_tesseract(tmp_path.parent / f"bin-{tmp_path.name}")
    log = tmp_path.parent / f"log-{tmp_path.name}.txt"
    _korpus(tmp_path)
    _kos(tmp_path, _ortam(ikili, "dil-yok", log))
    onb = json.loads((tmp_path / "_oa" / "metin" / ".ingest-onbellek.json").read_text(encoding="utf-8"))
    assert not any(g.endswith("005-tarama.pdf") for g in onb), "araç hatası önbelleğe YAZILMAMALI"
    assert any(g.endswith("002-not.txt") for g in onb)


# ═════════════════════════════════════════════════════════════════════════
# (C) okuma_kapisi.py — KRİTİK EVRAK → SÜRE ADAYI (P1-10 / A-4)
# ═════════════════════════════════════════════════════════════════════════

def _kapi(args, cwd):
    cp = subprocess.run([sys.executable, str(KAPI)] + args, capture_output=True, text=True,
                        encoding="utf-8", errors="replace", cwd=str(cwd))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _kunye_md_yaz(kok, kayitlar, mdler):
    metin = kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(json.dumps({
        "klasor": str(kok), "toplam_evrak": len(kayitlar), "ocr_teyit_gerek": 0,
        "bilinmeyen": 0, "buyuk_evrak": 0, "buyuk_esik": 40000, "toplam_karakter": 0,
        "tahmini_token": 0, "kayitlar": kayitlar}, ensure_ascii=False, indent=2), encoding="utf-8")
    for ad, govde in mdler.items():
        (metin / ad).write_text("# 001 · x\n\n- Kaynak evrak: `x`\n\n---\n" + govde, encoding="utf-8")


def _sure_korpus(tmp_path):
    kayitlar = [
        {"no": "001", "ad": "tebligat mazbatasi", "kaynak": "001-tebligat.pdf", "tarih": "02.03.2026",
         "tur_tahmini": "tebligat", "karakter": 300, "teyit_gerek": True, "buyuk": False,
         "md": "001-tebligat.md"},
        {"no": "002", "ad": "evrak", "kaynak": "002-evrak.pdf", "tarih": None,
         "tur_tahmini": None, "karakter": 800, "teyit_gerek": False, "buyuk": False,
         "md": "002-evrak.md"},
        {"no": "003", "ad": "bilanco 2025", "kaynak": "003-bilanco.pdf", "tarih": None,
         "tur_tahmini": "bilanco", "karakter": 500, "teyit_gerek": False, "buyuk": False,
         "md": "003-bilanco.md"},
        {"no": "004", "ad": "odeme emri", "kaynak": "004-odeme-emri.pdf", "tarih": None,
         "tur_tahmini": None, "karakter": 400, "teyit_gerek": False, "buyuk": False,
         "md": "004-odeme-emri.md"},
    ]
    mdler = {
        "001-tebligat.md": ("TEBLİĞ MAZBATASI\nMuhatap: Ayşe Örnek\nTebliğ tarihi: 14.03.2026\n"
                            + "x " * 200 + "\nDosya açılış 01.01.2020 tarihinde yapılmıştır. "
                            + "y " * 200 + "\nİlgisiz tarih 05/05/2019 burada."),
        "002-evrak.md": ("T.C. ÖRNEK ASLİYE HUKUK MAHKEMESİ\nGEREKÇELİ KARAR\nE. 2099/1\n"
                         "Karar tarihi: 20/02/2026\n" + "gövde " * 100),
        "003-bilanco.md": "Aktif 100 Pasif 100 düzenleme tarihi 31.12.2025",
        "004-odeme-emri.md": "ÖDEME EMRİ — Örnek İcra Dairesi. Tebellüğ: 03.04.2026",
    }
    _kunye_md_yaz(tmp_path, kayitlar, mdler)


def test_sure_adaylari_liste_ve_json(tmp_path):
    _sure_korpus(tmp_path)
    sureler = tmp_path / "_oa" / "sureler.json"
    sureler.parent.mkdir(exist_ok=True)
    sureler.write_text('{"flagler": []}', encoding="utf-8")
    kod, cikti = _kapi(["--kok", str(tmp_path), "--sure-adaylari"], cwd=tmp_path)
    assert kod == 0, cikti
    assert "SÜRE ADAYI" in cikti
    assert "001-tebligat.pdf" in cikti and "004-odeme-emri.pdf" in cikti and "002-evrak.pdf" in cikti
    assert "003-bilanco.pdf" not in cikti.split("SÜRE ADAYI", 1)[1]
    assert "sure-flag" in cikti and "avukat onayıyla" in cikti
    # sure-flag YAZILMADI
    assert sureler.read_text(encoding="utf-8") == '{"flagler": []}'

    js = json.loads((tmp_path / "_oa" / "cikti" / "00-sure-adaylari.json").read_text(encoding="utf-8"))
    adaylar = {a["evrak"]: a for a in js["adaylar"]}
    assert set(adaylar) == {"001-tebligat.pdf", "002-evrak.pdf", "004-odeme-emri.pdf"}
    assert js["advisory"] is True

    teb = adaylar["001-tebligat.pdf"]
    assert teb["sinif"] == "tebligat"
    tarihler = [t["tarih"] for t in teb["tarih_adaylari"]]
    assert "14.03.2026" in tarihler, teb
    assert "01.01.2020" not in tarihler and "05/05/2019" not in tarihler, "çıpasız tarih aday olmamalı"
    assert "02.03.2026" in tarihler, "dosya adından gelen künye tarihi de aday (baglam: dosya-adi)"
    assert any(t["baglam"] == "tebliğ" for t in teb["tarih_adaylari"])

    kar = adaylar["002-evrak.pdf"]
    assert kar["sinif"] == "gerekceli_karar"
    assert kar["tur_tahmin"] == "gerekceli_karar" and kar["tur_tahmin_kaynak"] == "ad+md600"
    assert "20/02/2026" in [t["tarih"] for t in kar["tarih_adaylari"]]
    assert "hmk_istinaf" in kar["oneri_kural"]

    ode = adaylar["004-odeme-emri.pdf"]
    assert ode["sinif"] == "odeme_emri"
    assert "03.04.2026" in [t["tarih"] for t in ode["tarih_adaylari"]]
    assert any(t["baglam"] == "tebellüğ" for t in ode["tarih_adaylari"])


def test_sure_adaylari_liste_komutunda_etiket(tmp_path):
    _sure_korpus(tmp_path)
    kod, cikti = _kapi(["--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    satir = next(s for s in cikti.splitlines() if "001-tebligat.md" in s)
    assert "SÜRE ADAYI" in satir
    satir_b = next(s for s in cikti.splitlines() if "003-bilanco.md" in s)
    assert "SÜRE ADAYI" not in satir_b


def test_sure_adaylari_kunye_yoksa_hata(tmp_path):
    kod, cikti = _kapi(["--kok", str(tmp_path), "--sure-adaylari"], cwd=tmp_path)
    assert kod == 1
    assert "künye bulunamadı" in cikti


def test_sure_adaylari_bos_kulliyat_bos_liste(tmp_path):
    _kunye_md_yaz(tmp_path, [
        {"no": "001", "ad": "bilanco", "kaynak": "001-bilanco.pdf", "tarih": None,
         "tur_tahmini": "bilanco", "karakter": 10, "teyit_gerek": False, "buyuk": False,
         "md": "001-bilanco.md"}], {"001-bilanco.md": "Aktif/Pasif"})
    kod, cikti = _kapi(["--kok", str(tmp_path), "--sure-adaylari"], cwd=tmp_path)
    assert kod == 0, cikti
    assert "süre adayı YOK" in cikti
    js = json.loads((tmp_path / "_oa" / "cikti" / "00-sure-adaylari.json").read_text(encoding="utf-8"))
    assert js["adaylar"] == []
