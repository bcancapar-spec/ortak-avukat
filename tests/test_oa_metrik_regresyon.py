# -*- coding: utf-8 -*-
"""P1-13 (P2'den YÜKSELTİLDİ, düzeltme turu Paket C) — REGRESYON SAYAÇLARI:
oa_metrik.py'nin [7] bölümü — adım-artefakt matrisi, teyit kütüğü araç-sınıfı
dağılımı, döküm/tam-yükleme sayaçları, muhakeme kaydı sayısı — VE `--baz-yaz`/
`--baz` ile EŞİKSİZ token/sayaç kıyas raporu.
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline"
          / "scripts" / "oa_metrik.py")


def _cli(args, cwd=None):
    cp = subprocess.run([sys.executable, str(SCRIPT)] + args, capture_output=True,
                         text=True, encoding="utf-8", errors="replace", cwd=str(cwd) if cwd else None)
    return cp.returncode, cp.stdout + cp.stderr


def _kunye_kur(kok):
    metin = kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")


def test_artefakt_matrisi_var_yok_dogru(tmp_path):
    _kunye_kur(tmp_path)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "05-kiyas-test.md").write_text("gövde " * 10, encoding="utf-8")
    (cikti / "07-antitez-test.md").write_text("gövde " * 10, encoding="utf-8")

    kod, cikti_txt = _cli(["--kok", str(tmp_path)])
    assert kod == 0, cikti_txt
    metrik = json.loads((tmp_path / "_oa" / "defter" / "metrik.json").read_text(encoding="utf-8"))
    am = metrik["regresyon_sayaclari"]["artefakt_matrisi"]
    assert am["05-kiyas"] is True
    assert am["07-antitez"] is True
    assert am["04-vakia"] is False
    assert am["06-strateji"] is False


def test_muhakeme_kayit_sayisi_kunye_bolum_sayar(tmp_path):
    _kunye_kur(tmp_path)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "ornek-ictihat-muhakeme.md").write_text(
        "**KUNYE:** A\nbölüm 1\n\n**KUNYE:** B\nbölüm 2\n", encoding="utf-8")

    kod, cikti_txt = _cli(["--kok", str(tmp_path)])
    assert kod == 0, cikti_txt
    metrik = json.loads((tmp_path / "_oa" / "defter" / "metrik.json").read_text(encoding="utf-8"))
    assert metrik["regresyon_sayaclari"]["muhakeme_kayit_sayisi"] == 2


def test_teyit_kutuk_arac_sinif_dagilimi(tmp_path):
    _kunye_kur(tmp_path)
    teyit = tmp_path / "_oa" / "teyit"
    teyit.mkdir(parents=True, exist_ok=True)
    (teyit / "kunye-teyit.md").write_text(
        "| Zaman | Araç | Sorgu | Sonuç | Döküm |\n"
        "|---|---|---|---|---|\n"
        "| t1 | ictihat_ara | sorgu1 | sonuç1 [ARAMA — tam metin çekilmedi] | |\n"
        "| t2 | ictihat_getir | sorgu2 | sonuç2 DAMGA=LEHE | [döküm](x.md) |\n"
        "| t3 | mevzuat_ara | sorgu3 | sonuç3 [ARAMA — tam metin çekilmedi] | |\n"
        "| t4 | bilinmeyen_arac | sorgu4 | sonuç4 | |\n",
        encoding="utf-8")

    kod, cikti_txt = _cli(["--kok", str(tmp_path)])
    assert kod == 0, cikti_txt
    metrik = json.loads((tmp_path / "_oa" / "defter" / "metrik.json").read_text(encoding="utf-8"))
    sd = metrik["regresyon_sayaclari"]["teyit_kutuk_arac_sinif_dagilimi"]
    assert sd == {"ictihat-arama": 1, "ictihat-getir": 1, "mevzuat": 1, "diger": 1}


def test_dokum_dosya_sayisi_ve_tam_yukleme_satir_sayisi(tmp_path):
    _kunye_kur(tmp_path)
    dokum = tmp_path / "_oa" / "teyit" / "dokum"
    dokum.mkdir(parents=True, exist_ok=True)
    (dokum / "a.md").write_text("x", encoding="utf-8")
    (dokum / "b.md").write_text("x", encoding="utf-8")

    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    (defter / "tam-yukleme.jsonl").write_text(
        json.dumps({"kaynak": "dilekce.pdf", "ajan": "oa-ictihat", "zaman": "t"}) + "\n"
        + json.dumps({"kaynak": "dilekce.pdf", "ajan": "oa-vakia", "zaman": "t2"}) + "\n",
        encoding="utf-8")

    kod, cikti_txt = _cli(["--kok", str(tmp_path)])
    assert kod == 0, cikti_txt
    metrik = json.loads((tmp_path / "_oa" / "defter" / "metrik.json").read_text(encoding="utf-8"))
    reg = metrik["regresyon_sayaclari"]
    assert reg["dokum_dosya_sayisi"] == 2
    assert reg["tam_yukleme_satir_sayisi"] == 2


def test_hicbir_kanit_yokken_sayaclar_sifir_uydurulmaz(tmp_path):
    kod, cikti_txt = _cli(["--kok", str(tmp_path)])
    assert kod == 0, cikti_txt
    metrik = json.loads((tmp_path / "_oa" / "defter" / "metrik.json").read_text(encoding="utf-8"))
    reg = metrik["regresyon_sayaclari"]
    assert reg["durum"] == "olculdu"
    assert all(v is False for v in reg["artefakt_matrisi"].values())
    assert reg["muhakeme_kayit_sayisi"] == 0
    assert reg["dokum_dosya_sayisi"] == 0
    assert reg["tam_yukleme_satir_sayisi"] == 0


def test_baz_yaz_sonra_baz_kiyas_degisiklik_yoksa_esiksiz(tmp_path):
    _kunye_kur(tmp_path)
    baz_dosya = tmp_path / "metrik-baz-test.json"
    kod, _ = _cli(["--kok", str(tmp_path), "--baz-yaz", str(baz_dosya)])
    assert kod == 0
    assert baz_dosya.is_file()

    kod, cikti_txt = _cli(["--kok", str(tmp_path), "--baz", str(baz_dosya)])
    assert kod == 0, cikti_txt
    metrik = json.loads((tmp_path / "_oa" / "defter" / "metrik.json").read_text(encoding="utf-8"))
    bk = metrik["baz_kiyas"]
    assert bk["esik_asan_alanlar"] == []
    assert "BAZ KIYAS" in cikti_txt


def test_baz_kiyas_esik_asan_alan_isaretlenir_ama_engellemez(tmp_path):
    _kunye_kur(tmp_path)
    baz_dosya = tmp_path / "metrik-baz-eski.json"
    kod, _ = _cli(["--kok", str(tmp_path), "--baz-yaz", str(baz_dosya)])
    assert kod == 0
    baz_veri = json.loads(baz_dosya.read_text(encoding="utf-8"))
    # Baz'daki muhakeme kaydı sayısını elle küçük bir değere sabitleyip
    # güncel koşuda büyük bir artış simüle ediyoruz (>=%30).
    baz_veri["regresyon_sayaclari"]["muhakeme_kayit_sayisi"] = 1
    baz_dosya.write_text(json.dumps(baz_veri), encoding="utf-8")

    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "ornek-ictihat-muhakeme.md").write_text(
        "**KUNYE:** A\n**KUNYE:** B\n**KUNYE:** C\n", encoding="utf-8")

    kod, cikti_txt = _cli(["--kok", str(tmp_path), "--baz", str(baz_dosya)])
    assert kod == 0, cikti_txt
    metrik = json.loads((tmp_path / "_oa" / "defter" / "metrik.json").read_text(encoding="utf-8"))
    bk = metrik["baz_kiyas"]
    assert "muhakeme_kayit_sayisi" in bk["esik_asan_alanlar"]
    assert "ENGEL DEĞİL" in bk["not"] or "GEÇİT" in bk["not"]
