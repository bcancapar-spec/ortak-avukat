# -*- coding: utf-8 -*-
"""P1-9(a) (v0.5.5) — oa_ingest.py --onbakis N: MEŞRU HIZLI KANAL.

DÜZELTME (bağlayıcı plan, sinav BLOKER giderimi): --onbakis AYRI bir artefakta
yazar (`_oa/metin-onbakis/` + `00-kunye.onbakis.json`) — ana `_oa/metin/`
önbelleğine/00-kunye.json/00-INDEX.md'ye HİÇ dokunmaz; bayraksız TAM koşu
byte-özdeş kalır (v1.5 determinizm kazanımı korunur).

Kapsam:
1. --onbakis 3 → 3 evrak işlenir, aynı başlık şeması ile tam koşuyla
   BYTE-ÖZDEŞ md gövdesi üretir.
2. exit 4 + 00-kunye.onbakis.json'da onbakis:true.
3. Ardından bayraksız TAM koşu → normal biter (exit 0), ana hat hiç
   etkilenmemiştir (onbakis artefaktları duruyor, ana künye TAM).
4. Bayraksız yol (--onbakis hiç verilmeden) determinizm testiyle birebir
   aynı sonucu üretir (ana hat regresyonu YOK).
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "oa_ingest.py"


def _korpus_kur(kok, n=5):
    kok = pathlib.Path(kok)
    for i in range(1, n + 1):
        (kok / f"{i:03d}-evrak.txt").write_text(
            f"Evrak {i} içeriği — yeterince uzun metin örneği burada tekrar eder. " * 2,
            encoding="utf-8")


def _run(args, klasor=None):
    cmd = [sys.executable, str(SCRIPT)]
    if klasor is not None:
        cmd.append(str(klasor))
    cmd += args
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace")


def test_onbakis_3_evrak_islenir_ve_govde_ozdes(tmp_path):
    _korpus_kur(tmp_path, n=5)
    cp = _run(["--ocr", "kapali", "--onbakis", "3"], tmp_path)
    assert cp.returncode == 4, cp.stdout + cp.stderr
    ob = tmp_path / "_oa" / "metin-onbakis"
    assert ob.is_dir()
    md_dosyalari = sorted(p for p in ob.glob("0*.md") if "INDEX" not in p.name)
    assert len(md_dosyalari) == 3, [p.name for p in md_dosyalari]

    # Aynı korpusta TAM koşu — onbakis'in ürettiği md gövdesi (evrak-1) ile
    # tam koşunun ürettiği aynı evrağın gövdesi BİREBİR aynı olmalı (başlık
    # şeması + içerik özdeş; yalnız hedef dizin farklı).
    cp2 = _run(["--ocr", "kapali", "--isci", "1"], tmp_path)
    assert cp2.returncode == 0, cp2.stdout + cp2.stderr
    ana = tmp_path / "_oa" / "metin"
    onbakis_1 = (ob / "001-evrak.md").read_text(encoding="utf-8")
    ana_1 = (ana / "001-evrak.md").read_text(encoding="utf-8")
    assert onbakis_1 == ana_1


def test_onbakis_exit4_ve_kunye_json_onbakis_true(tmp_path):
    _korpus_kur(tmp_path, n=4)
    cp = _run(["--ocr", "kapali", "--onbakis", "2"], tmp_path)
    assert cp.returncode == 4, cp.stdout + cp.stderr
    kunye_yol = tmp_path / "_oa" / "metin-onbakis" / "00-kunye.onbakis.json"
    assert kunye_yol.is_file()
    veri = json.loads(kunye_yol.read_text(encoding="utf-8"))
    assert veri["onbakis"] is True
    assert veri["onbakis_n"] == 2
    assert veri["toplam_evrak"] == 2
    assert "ONBAKIS" in cp.stdout
    assert "TAM DEĞİL" in cp.stdout


def test_onbakis_ana_hatta_dokunmaz(tmp_path):
    _korpus_kur(tmp_path, n=4)
    _run(["--ocr", "kapali", "--onbakis", "2"], tmp_path)
    ana_metin = tmp_path / "_oa" / "metin"
    ana_kunye = tmp_path / "_oa" / "metin" / "00-kunye.json"
    ana_index = tmp_path / "_oa" / "metin" / "00-INDEX.md"
    assert not ana_kunye.exists(), "onbakis ana 00-kunye.json'a DOKUNMAMALI"
    assert not ana_index.exists(), "onbakis ana 00-INDEX.md'ye DOKUNMAMALI"
    assert not ana_metin.exists() or not any(ana_metin.iterdir())


def test_onbakis_sonrasi_tam_kosu_normal_biter(tmp_path):
    _korpus_kur(tmp_path, n=4)
    cp1 = _run(["--ocr", "kapali", "--onbakis", "2"], tmp_path)
    assert cp1.returncode == 4

    cp2 = _run(["--ocr", "kapali", "--isci", "1"], tmp_path)
    assert cp2.returncode == 0, cp2.stdout + cp2.stderr
    kunye = json.loads((tmp_path / "_oa" / "metin" / "00-kunye.json").read_text(encoding="utf-8"))
    assert kunye["toplam_evrak"] == 4
    # onbakis artefaktları hâlâ duruyor (kayıpsızlık — ana hat onları silmez).
    assert (tmp_path / "_oa" / "metin-onbakis" / "00-kunye.onbakis.json").is_file()


def test_bayraksiz_yol_determinizm_ile_birebir_ayni(tmp_path, tmp_path_factory):
    """--onbakis hiç verilmezse ana hat ÖNCEKİ (P1-9 öncesi) davranışla birebir
    aynıdır — regresyon testi. İki AYRI köke aynı korpus, biri --onbakis'i
    HİÇ görmeden, diğeri önce --onbakis sonra tam koşu — 00-kunye.json'daki
    kayıtlar (kaynak/karakter/sha) BİREBİR aynı olmalı."""
    kok_a = tmp_path_factory.mktemp("ing_a")
    kok_b = tmp_path_factory.mktemp("ing_b")
    _korpus_kur(kok_a, n=3)
    _korpus_kur(kok_b, n=3)

    cp_a = _run(["--ocr", "kapali", "--isci", "1"], kok_a)
    assert cp_a.returncode == 0, cp_a.stdout + cp_a.stderr

    _run(["--ocr", "kapali", "--onbakis", "1"], kok_b)
    cp_b = _run(["--ocr", "kapali", "--isci", "1"], kok_b)
    assert cp_b.returncode == 0, cp_b.stdout + cp_b.stderr

    kunye_a = json.loads((kok_a / "_oa" / "metin" / "00-kunye.json").read_text(encoding="utf-8"))
    kunye_b = json.loads((kok_b / "_oa" / "metin" / "00-kunye.json").read_text(encoding="utf-8"))
    kayitlar_a = [(k["kaynak"], k["karakter"], k["sha"]) for k in kunye_a["kayitlar"]]
    kayitlar_b = [(k["kaynak"], k["karakter"], k["sha"]) for k in kunye_b["kayitlar"]]
    assert kayitlar_a == kayitlar_b
